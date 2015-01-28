# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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

from openerp.osv import orm


class hr_employee(orm.Model):
    _inherit = 'hr.employee'

    def sum_leave_accruals(
        self, cr, uid, ids, employee_id, accrual_code, date, context=None
    ):
        """
        Sums over the lines of an employee's leave accruals
        Returns a dict that contains 3 amounts
            * 'current_added_ytd'
            * 'current_taken_ytd'
            * 'previous_ytd'
        """
        employee = self.browse(cr, uid, employee_id, context=context)

        accrual_id = False

        for accrual in employee.leave_accrual_ids:
            if accrual.code == accrual_code:
                accrual_id = accrual.id
                break

        # If the employee doesn't have the accrual of the given type,
        # create it
        if not accrual_id:
            template_id = self.pool['hr.leave.accrual.template'].search(
                cr, uid, [('code', '=', accrual_code)], context=context)[0]

            accrual_id = self.pool['hr.leave.accrual'].create(
                cr, uid, {
                    'employee_id': employee_id,
                    'template_id': template_id,
                }, context=context)

        return self.pool['hr.leave.accrual'].sum_lines_by_category(
            cr, uid, accrual_id, date, context=context)

    def create(
        self, cr, uid, vals, context=None
    ):
        """
        After an employee is created, add the missing leave accruals.
        The employee must have a leave accrual for
            VAC - vacations
            SL - sick leaves
            COMP - compensatory leaves
        """

        # Create the employee and access the record
        employee_id = super(hr_employee, self).create(
            cr, uid, vals, context=context
        )
        employee = self.browse(
            cr, uid, employee_id, context=context,
        )

        # Get the codes related to the leave accruals that the employee
        # does not already has
        employee_accruals_codes = [
            accrual.template_id.code
            for accrual in employee.leave_accrual_ids
        ]
        required_accrual_codes = [
            code for code in ['VAC', 'SL', 'COMP']
            if code not in employee_accruals_codes
        ]

        # Get the template ids related to the required leave accruals
        template_obj = self.pool['hr.leave.accrual.template']
        template_ids = template_obj.search(
            cr, uid,
            [('code', 'in', required_accrual_codes)],
            context=context,
        )
        required_accruals = [
            (0, 0, {
                'template_id': template_id,
                'employee_id': employee_id,
            })
            for template_id in template_ids
        ]

        # Create the new leave accruals
        self.write(
            cr, uid, [employee_id],
            {'leave_accrual_ids': required_accruals},
            context=context,
        )
        return employee_id
