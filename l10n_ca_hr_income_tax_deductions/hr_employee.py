# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Amura Consulting. All Rights Reserved.
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
        date_from,
        date_to,
        deduction_code,
        estimated_income=False,
        context=None
    ):

        payslip_from = strptime(date_from, "%Y-%m-%d").date()
        payslip_to = strptime(date_to, "%Y-%m-%d").date()
        payslip_duration = (payslip_to - payslip_from).days + 1

        employee = self.browse(cr, uid, employee_id, context=context)
        deductions = employee.deduction_ids

        res = 0

        for d in deductions:
            if d.code == deduction_code and (
                not estimated_income or d.estimated_income
            ):
                date_start = strptime(d.date_start, "%Y-%m-%d").date()
                start_offset = max((date_start - payslip_from).days, 0)

                date_end = d.date_end and \
                    strptime(d.date_end, "%Y-%m-%d").date() or False
                end_offset = date_end and \
                    max((payslip_to - date_end).days, 0) or 0

                ratio = 1 - (start_offset + end_offset) / payslip_duration
                amount = d.amount * ratio
                res += amount

        return res

    _defaults = {
    }
