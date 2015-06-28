# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


def get_payslip(payslip):
    """
    In salary rules, the variable 'payslip' refers to a BrowseRecord which
    is different from a payslip browse_record

    BrowsableObject is a problem because the worked days and other
    inputs it refers to may be deprecated. It contains an attribute dict
    that contains the related browse_record.

    :param payslip: a payslip BrowsableObject or a browse_record

    :return: a refreshed payslip browse_record
    """
    if not isinstance(payslip, orm.browse_record):
        payslip = payslip.dict

    payslip.refresh()

    return payslip


class HrSalaryRule(orm.Model):
    _inherit = 'hr.salary.rule'

    _columns = {
        'payslip_input_ids': fields.many2many(
            'hr.payslip.input.category',
            'hr_payslip_input_salary_rule_rel',
            string='Payslip Inputs',
        ),

        'leave_activity_ids': fields.many2many(
            'hr.activity',
            'hr_activity_salary_rule_rel',
            string='Related Leave Activities',
        ),

        'leave_accrual_id': fields.many2one(
            'hr.holidays.status',
            'Leave Accrual',
        ),
    }

    def _get_payslip_input_categories(
        self, cr, uid, ids, context=None
    ):
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1

        rule = self.browse(cr, uid, ids[0], context=context)
        return rule.payslip_input_ids

    def sum_payslip_input(
        self, cr, uid, ids, payslip, context=None
    ):
        """
        Sum over the other input lines of the payslip for a given
        input type
        :param payslip: BrowsablePayslip object or browse_record
        """
        payslip = get_payslip(payslip)

        categories = self._get_payslip_input_categories(
            cr, uid, ids, context=context)

        res = 0

        for input_line in payslip.input_line_ids:
            if input_line.category_id in categories:
                res += input_line.amount

        return res

    def reduce_payslip_input_amount(
        self, cr, uid, ids,
        payslip, reduction, context=None
    ):
        """
        When unused leaves requested are lower then those available,
        reduce the related inputs
        """
        payslip = get_payslip(payslip)

        categories = self._get_payslip_input_categories(
            cr, uid, ids, context=context)

        input_lines = [
            input_line for input_line in payslip.input_line_ids
            if input_line.category_id in categories
        ]

        for input_line in input_lines:
            if reduction == 0:
                break

            current_reduction = min(input_line.amount, reduction)
            new_amount = input_line.amount - current_reduction

            input_line.write({'amount': new_amount})
            reduction = reduction - current_reduction

    def _get_leave_activities(
        self, cr, uid, ids, context=None
    ):
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1

        rule = self.browse(cr, uid, ids[0], context=context)
        return rule.leave_activity_ids

    def reduce_leaves(
        self, cr, uid, ids, payslip, reduction,
        in_cash=False, context=None
    ):
        """
        When the leave hours computed in worked days are greater than the
        available hours from the employee's leave accrual, this method
        is called to reduce the worked days lines related to the leave type.

        :param in_cash: Whether to apply the reduction in cash or in hours
        """
        payslip = get_payslip(payslip)

        # To avoid integers as parameter to mess up with divisions
        reduction = float(reduction)

        activities = self._get_leave_activities(cr, uid, ids, context=context)

        default_unpaid_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'hr_worked_days_activity',
            'activity_holiday_status_unpaid')[1]

        worked_days = [
            wd for wd in payslip.worked_days_line_ids
            if wd.activity_id in activities
        ]

        worked_days.sort(key=lambda wd: wd.date_from)
        worked_days.reverse()

        for wd in worked_days:
            if reduction == 0:
                break

            current_reduction = (
                reduction / (wd.hourly_rate * wd.rate / 100)
                if in_cash else reduction
            )

            # Get the maximum of reduction of the current worked day
            current_reduction = min(wd.number_of_hours, current_reduction)
            current_reduction = max(current_reduction, 0)

            # Apply the reduction to the worked days line
            number_of_hours = wd.number_of_hours - current_reduction
            wd.write({'number_of_hours': number_of_hours})

            unpaid_activity = wd.activity_id.unpaid_activity_id

            # Create a worked days record to replace the previous wd
            self.pool['hr.payslip.worked_days'].create(
                cr, uid, {
                    'payslip_id': wd.payslip_id.id,
                    'date_from': wd.date_from,
                    'date_to': wd.date_to,
                    'number_of_hours': current_reduction,
                    'rate': wd.rate,
                    'hourly_rate': 0,
                    'activity_id': unpaid_activity.id if unpaid_activity
                    else default_unpaid_id,
                }, context=context)

            # substract the amount reduced before next iteration
            reduction -= (
                current_reduction * wd.hourly_rate * wd.rate / 100
                if in_cash else current_reduction
            )

            if wd.number_of_hours == 0:
                wd.unlink()

    def sum_leaves(
        self, cr, uid, ids, payslip, in_cash=False, context=None
    ):
        """
        Used in salary rules to sum leave hours from worked_days
        e.g. sum over the hours of vacation (leave_code == 'VAC')

        :param leave_code: a string or a list of string
        :param payslip: a payslip BrowsableObject or a browse_record
        :param in_cash: Whether to return an amount in cash of hours

        :return: the amount of allowance requested by the employee
        """
        payslip = get_payslip(payslip)

        activities = self._get_leave_activities(cr, uid, ids, context=context)

        worked_days = [
            wd for wd in payslip.worked_days_line_ids
            if wd.activity_id in activities
        ]

        if in_cash:
            return sum(wd.total for wd in worked_days)

        return sum(wd.number_of_hours for wd in worked_days)

    def _get_leave_accrual(self, cr, uid, ids, context=None):
        """
        If a salary rule is used to read or update a leave accrual,
        a leave type must be related to it.
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1

        rule = self.browse(cr, uid, ids[0], context=context)

        if not rule.leave_accrual_id:
            raise orm.except_orm(
                _('Error'),
                _('Salary rule %s is used to read leave '
                    'accruals but it has no related leave accrual.') % (
                    rule.name))

        return rule.leave_accrual_id

    def sum_leave_accruals(
        self, cr, uid, ids, payslip, in_cash=False, context=None,
    ):
        """
        Sum over the lines of an employee's leave accruals available for
        the current payslip
        """
        payslip = get_payslip(payslip)

        employee = payslip.employee_id
        leave_type = self._get_leave_accrual(cr, uid, ids, context=context)

        accrual_id = self.pool['hr.employee'].get_leave_accrual_id(
            cr, uid, employee.id, leave_type_id=leave_type.id, context=context)

        # Standard case for other types of leaves
        return self.pool['hr.leave.accrual'].sum_leaves_available(
            cr, uid, accrual_id, payslip.date_to, in_cash=in_cash,
            context=context)
