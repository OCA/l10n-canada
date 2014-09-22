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
import time
import datetime
strptime = datetime.datetime.strptime


def get_jurisdiction(self, cursor, user_id, context=None):
    return (
        ('federal', 'Federal'),
        ('provincial', 'Provincial'))


def get_type(self, cursor, user_id, context=None):
    return (
        ('federal', 'Federal'),
        ('ei', 'Employment Insurance'),
        ('qc', 'Quebec'),
        ('rqap', 'RQAP / RRQ'),
        ('csst', 'CSST'))


class hr_deduction_category(orm.Model):
    _name = 'hr.deduction.category'
    _description = 'Categories of employee deductions used for salary rules'
    _columns = {
        'name': fields.char('Category Name', size=256, required=True),
        'code': fields.char('Code', size=52, required=True, help="""\
The code that can be used in the salary rules to identify thededuction"""),
        'description': fields.char(
            'Description',
            size=512,
            required=True,
            help="""\
Brief explanation of which benefits the category contains."""),
        'default_amount': fields.float('Default Amount', required=True),
        'jurisdiction': fields.selection(
            get_jurisdiction,
            'Jurisdiction',
            required=True
        ),
        'note': fields.text('Note'),
    }
    _defaults = {
        'default_amount': 0.0,
        'jurisdiction': 'federal',
    }


class hr_employee_deduction(orm.Model):
    _name = 'hr.employee.deduction'
    _description = 'Employee deductions used for salary rules'
    _columns = {
        'name': fields.char('Deduction Name', size=256, required=True),
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True,
            readonly=True,
        ),
        'category_id': fields.many2one(
            'hr.deduction.category',
            'Category',
            required=True,
            ondelete='cascade',
            select=True
        ),
        'amount': fields.float('Amount', required=True, help="""\
It is used in computation of the payslip. May be an annual or
periodic amount depending on the category. The deduction may be
a tax credit."""),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date'),
        'code': fields.related(
            'category_id',
            'code',
            type='char',
            size=52,
            string='Code'
        ),
        'jurisdiction': fields.related(
            'category_id',
            'jurisdiction',
            type='selection',
            selection=get_jurisdiction
        ),
        'estimated_income': fields.boolean(
            'Estimated Income',
            help="""\
True if included in the calculation of the estimated annual net income,
False otherwise""",
        ),
    }
    _defaults = {
        'amount': 0.0,
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'estimated_income': True,
    }

    def onchange_category_id(self, cr, uid, ids, category_id=False):
        res = {'value': {'amount': 0.0}}
        if category_id:
            category = self.pool.get('hr.deduction.category')
            category = category.browse(cr, uid, category_id)
            res['value']['amount'] = category.default_amount
            res['value']['name'] = category.name
        return res


class hr_benefit_category(orm.Model):
    _name = 'hr.benefit.category'
    _description = 'Categories of employee benefits'
    _columns = {
        'name': fields.char('Benefit Name', size=256, required=True),
        'code': fields.char('Code', size=52, required=True, help="""\
The code that can be used in the salary rules to identify the benefit"""),
        'description': fields.char(
            'Description',
            size=512,
            required=True,
            help="Brief explanation of which benefits the category contains."
        ),
        'is_cash': fields.boolean('Is Cash', help="""\
True if the benefit is paid in cash to the employee,
False if paid in Kind."""),
        'default_amount': fields.float(
            'Default Employee Contribution',
            required=True,
            help="""\
Default annual amount that the employee contributes"""
        ),
        'default_er_amount': fields.float(
            'Default Employer Contribution',
            required=True,
            help="Default annual amount that the employer contributes"
        ),
        'ei_exempt': fields.boolean('EI Exempt'),
        'fit_exempt': fields.boolean('FIT Exempt'),
    }
    _defaults = {
        'is_cash': True,
        'default_amount': 0.0,
        'ei_exempt': False,
        'fit_exempt': False,
    }


class hr_contract_benefit(orm.Model):
    _name = 'hr.contract.benefit'
    _description = 'The benefits in an employee contract'
    _columns = {
        'name': fields.char(
            'Deduction Name',
            size=256,
            required=True
        ),
        'contract_id': fields.many2one(
            'hr.contract',
            'Contract',
            required=True,
            ondelete='cascade',
            select=True
        ),
        'category_id': fields.many2one(
            'hr.benefit.category',
            'Benefit',
            required=True,
            ondelete='cascade',
            select=True
        ),
        'amount': fields.float(
            'Employee Contribution',
            required=True,
            help="""\
Enter the amount that you would pay for a complete year,
even if the duration is lower that a year.""",
        ),
        'er_amount': fields.float(
            'Employer Contribution',
            required=True,
            help="""\
Enter the amount that you would pay for a complete year,
even if the duration is lower that a year.""",
        ),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date'),
        'is_annual': fields.boolean(
            'Annual',
            help="""\
True if the entered amounts of contribution for employee and
employer are annual, False if they are entered for the period."""
        ),
        'ei_exempt': fields.related(
            'category_id',
            'ei_exempt',
            type='char',
            size=52,
            string='EI Exempt'
        ),
        'fit_exempt': fields.related(
            'category_id',
            'fit_exempt',
            type='char',
            size=52,
            string='FIT Exempt'
        ),
        'code': fields.related(
            'category_id',
            'code',
            type='char',
            size=52,
            string='Code'
        ),
    }
    _defaults = {
        'amount': 0,
        'er_amount': 0,
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'is_annual': True,
    }

    def onchange_category_id(self, cr, uid, ids, category_id=False):
        res = {'value': {'amount': 0.0}}
        if category_id:
            category = self.pool.get('hr.benefit.category')
            category = category.browse(cr, uid, category_id)
            res['value']['amount'] = category.default_amount
            res['value']['er_amount'] = category.default_er_amount
            res['value']['name'] = category.name
        return res


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


class hr_contract(orm.Model):
    _inherit = 'hr.contract'

    def _get_pays_per_year(self, cr, uid, ids, names, arg, context=None):
        """
        @param ids: ID of contract
        @return: The number of pays per year
        """
        res = {}
        # FIXME: Should likely pull these values from somewhere else,
        # depending on whether a 52 or 53 year week is used
        schedule_pay = {
            'weekly': 52,
            'bi-weekly': 26,
            'semi-monthly': 24,
            'monthly': 12,
            'bi-monthly': 6,
            'quarterly': 4,
            'semi-annually': 2,
            'annually': 1,
        }
        for contract in self.browse(cr, uid, ids, context):
            if contract.schedule_pay and schedule_pay.get(
                contract.schedule_pay, False
            ):
                res[contract.id] = schedule_pay[contract.schedule_pay]
        return res

    _columns = {
        'pays_per_year': fields.function(
            _get_pays_per_year, method=True, string='Pays Per Year',
            type='float', readonly=True,
        ),
        'weeks_of_vacation': fields.integer('Number of weeks of vacation',
                                            required=True),
        'benefit_line_ids': fields.one2many(
            'hr.contract.benefit',
            'contract_id',
            'Employee Benefits'
        ),
    }

    _defaults = {
        'weeks_of_vacation': 2,
    }

    def sum_benefits(
        self, cr, uid, ids, contract_id, date_from, date_to,
        exemption=False, benefit_code=False, employer=False,
        annual=True, pays_per_year=False, context=None
    ):

        # convert string dates to date objects
        payslip_from = strptime(date_from, "%Y-%m-%d").date()
        payslip_to = strptime(date_to, "%Y-%m-%d").date()

        payslip_duration = (payslip_to - payslip_from).days + 1

        contract = self.read(
            cr, uid, contract_id,
            ['benefit_line_ids'],
            context
        )
        benefit_ids = contract['benefit_line_ids']

        attrs = [
            'code', 'amount', 'er_amount', 'category_id',
            'date_start', 'date_end', 'is_annual'
        ]
        if exemption:
            attrs.append(exemption)

        benefits = self.pool.get(
            'hr.contract.benefit'
        ).read(
            cr, uid, benefit_ids, attrs, context
        )

        res = 0
        for b in benefits:
            if (not exemption or not b[exemption]) and (
                not benefit_code or b['code'] == benefit_code
            ):

                # convert string dates to date objects
                b['date_start'] = strptime(b['date_start'], "%Y-%m-%d").date()
                b['date_end'] = b['date_end'] and \
                    strptime(b['date_end'], "%Y-%m-%d").date()

                amount = employer and b['er_amount'] or b['amount']

                # some calculations need annual benefit amounts,
                # other need the periodic amount
                # benefits can have an annual amount or a periodic amount
                if annual and not b['is_annual']:
                    amount = pays_per_year * amount
                elif not annual and b['is_annual']:
                    amount = amount / pays_per_year

                # Ponderate the amount of benefit in regard
                # to the payslip dates
                if b['is_annual']:
                    start_offset = max(
                        (b['date_start'] - payslip_from).days,
                        0
                    )
                    end_offset = b['date_end'] and \
                        max((payslip_to - b['date_end']).days, 0) or 0
                else:
                    start_offset = max(
                        (payslip_from - b['date_start']).days,
                        0
                    )
                    end_offset = max((b['date_end'] - payslip_to).days, 0)

                ratio = 1 - (start_offset + end_offset) / payslip_duration
                amount = amount * ratio

                res += amount

        return res

    _defaults = {
    }
