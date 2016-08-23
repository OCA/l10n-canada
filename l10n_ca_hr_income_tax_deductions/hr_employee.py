# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Odoo Canada. All Rights Reserved.
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

from openerp.osv import fields, orm
import datetime
strptime = datetime.datetime.strptime


class hr_employee(orm.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _columns = {
        'deduction_ids': fields.one2many(
            'hr.employee.deduction',
            'employee_id',
            'Income Tax Deductions',
            help="""\
Income Tax deductions for the computation of the employee's payslips"""
        ),
    }

    def sum_deductions(
        self, cr, uid, ids,
        employee_id,
        date_from, date_to,
        deduction_codes, pays_per_year,
        estimated_income=False,
        context=None
    ):
        """Sums over an employee's income tax deductions

        estimated_income: whether the result will be used to calculate the
        employee's estimated income
        """
        employee = self.browse(cr, uid, employee_id, context=context)
        deductions = employee.deduction_ids
        if not deductions:
            return 0

        # Get the payslup duration.
        # This is required because a deduction's start-end interval may
        # partially overlap the payslip's period.
        payslip_from = strptime(date_from, "%Y-%m-%d").date()
        payslip_to = strptime(date_to, "%Y-%m-%d").date()
        payslip_duration = (payslip_to - payslip_from).days + 1

        res = 0

        if not isinstance(deduction_codes, list):
            deduction_codes = [deduction_codes]

        for d in deductions:
            if d.code in deduction_codes and (
                # Some deductions need to be ignored when computing
                # the estimated income for the year
                not estimated_income or d.category_id.estimated_income
            ):
                # Case where the deduction begins after the payslip period
                # begins.
                date_start = strptime(d.date_start, "%Y-%m-%d").date()
                start_offset = max((date_start - payslip_from).days, 0)

                # Case where the deduction ends before the payslip period
                # ends.
                date_end = d.date_end and \
                    strptime(d.date_end, "%Y-%m-%d").date() or False
                end_offset = date_end and \
                    max((payslip_to - date_end).days, 0) or 0

                # Get the ratio of the payslip period covered by the deduction.
                ratio = 1 - float(start_offset + end_offset) / payslip_duration
                ratio = max(ratio, 0)

                amount = d.amount * ratio

                # If the user entered a periodical amount ('each_pay') instead
                # of an annual amount('annual'), we need to convert the amount
                if d.amount_type == 'each_pay':
                    amount = pays_per_year * amount

                res += amount

        return res
