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
        'fit_exempt': fields.boolean('Federal Income Tax Exempt'),
        'pit_exempt': fields.boolean('Provincial Income Tax Exempt'),
        'ei_exempt': fields.boolean('EI Exempt'),
        'cpp_exempt': fields.boolean('CPP/QPP Exempt'),
        'qpip_exempt': fields.boolean('QPIP Exempt'),
        'cpp_ytd_adj': fields.float('CPP/QPP YTD Adjustment', help="""\
Amount to adjust CPP/QPP for calculations.
Used if employee has contributed elsewhere and will be factored in when
calculating maximum CPP payment"""),
        'ei_ytd_adj': fields.float('EI YTD Adjustment', help="""\
Amount to adjust EI for calculations.
Used if employee has contributed elsewhere and will be factored in when
calculating maximum EI payment"""),
        'vac_pay': fields.float('Vacation Pay %', digits=(16, 2)),
        'federal_deduction_ids': fields.one2many(
            'hr.employee.deduction',
            'employee_id',
            'Federal Income Tax Deductions',
            help="""\
Income Tax deductions for the computation of the employee's payslips"""),
        'provincial_deduction_ids': fields.one2many(
            'hr.employee.deduction',
            'employee_id',
            'Provincial Income Tax Deductions',
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

        employee = self.read(
            cr, uid, employee_id,
            ['federal_deduction_ids', 'provincial_deduction_ids'],
            context
        )

        deduction_ids = employee['federal_deduction_ids'] + \
            employee['provincial_deduction_ids']

        attrs = ['code', 'amount', 'category_id', 'date_start', 'date_end']
        if estimated_income:
            attrs.append('estimated_income')

        deductions = self.pool.get('hr.employee.deduction').read(
            cr, uid, deduction_ids, attrs, context
        )

        res = 0

        for d in deductions:
            if d['code'] == deduction_code and (
                not estimated_income or d['estimated_income']
            ):

                d['date_start'] = strptime(d['date_start'], "%Y-%m-%d").date()
                d['date_end'] = d['date_end'] and \
                    strptime(d['date_end'], "%Y-%m-%d").date()

                start_offset = max((d['date_start'] - payslip_from).days, 0)
                end_offset = d['date_end'] and \
                    max((payslip_to - d['date_end']).days, 0) or 0

                ratio = 1 - (start_offset + end_offset) / payslip_duration
                amount = d['amount'] * ratio

                res += amount
        return res

    _defaults = {
    }
