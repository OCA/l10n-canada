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

from openerp.osv import fields, orm, osv
import time

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

class hr_payroll_tax_table(orm.Model):
    '''
    Canadian Tax Payroll Table
    '''
    _name = 'hr.payroll.tax.table'
    _description = 'Canadian Tax Payroll Table'

    def onchange_year(self, cr, uid, ids, year, prov=False):
        res = {}
        res['name'] = 'Tax Table: ' + str(year)
        if prov:
            prov_obj = self.pool.get('res.country.state').browse(cr, uid, prov)
            res['name'] += ' / Provincial - ' + prov_obj.code
        else:
            res['name'] += ' / Federal'

        return {'value': res}
        
    _columns = {
            'name': fields.char('Description', size=128),
            'year': fields.integer('Year', required=True),
            'date_from': fields.date('Date From'),
            'date_to': fields.date('Date To'),
            'jurisdiction': fields.selection(get_jurisdiction, 'Jurisdiction', required=True),
            'state_id': fields.many2one('res.country.state', 'Province'),
            'type': fields.selection(get_type, 'Type', required=True),
            'line_federal_ids': fields.one2many('hr.payroll.tax.table.federal.line', 'table_id', 'Lines'),
            'line_ei_ids': fields.one2many('hr.payroll.tax.table.ei.line', 'table_id', 'Lines'),
            'line_qc_ids': fields.one2many('hr.payroll.tax.table.qc.line', 'table_id', 'Lines'),
            'line_rqap_ids': fields.one2many('hr.payroll.tax.table.rqap.line', 'table_id', 'Lines'),
            'line_csst_ids': fields.one2many('hr.payroll.tax.table.csst.line', 'table_id', 'Lines'),
            }

    _defaults = {
            'jurisdiction': 'federal',
            'type': 'federal',
            }

class hr_payroll_tax_table_federal_line(orm.Model):
    '''
    Federal Lines
    '''
    _name = 'hr.payroll.tax.table.federal.line'
    _description = 'Federal Lines'
    _columns = {
        'table_id': fields.many2one('hr.payroll.tax.table', 'Table'),
        'inc_from': fields.float('Income From', digits=(16, 2), required=True),
        'inc_to': fields.float('Income To', digits=(16, 2), required=True),
        'code0': fields.float('Code 0', digits=(16, 2)),
        'code1': fields.float('Code 1', digits=(16, 2)),
        'code2': fields.float('Code 2', digits=(16, 2)),
        'code3': fields.float('Code 3', digits=(16, 2)),
        'code4': fields.float('Code 4', digits=(16, 2)),
        'code5': fields.float('Code 5', digits=(16, 2)),
        'code6': fields.float('Code 6', digits=(16, 2)),
        'code7': fields.float('Code 7', digits=(16, 2)),
        'code8': fields.float('Code 8', digits=(16, 2)),
        'code9': fields.float('Code 9', digits=(16, 2)),
        'code10': fields.float('Code 10', digits=(16, 2)),
        }

    _rec_name = 'inc_from'

class hr_payroll_tax_table_ei_line(orm.Model):
    '''
    Employment Insurance Lines
    '''
    _name = 'hr.payroll.tax.table.ei.line'
    _description = 'Employment Insurance Lines'
    _columns = {
        'table_id': fields.many2one('hr.payroll.tax.table', 'Table'),
        'inc_from': fields.float('Income From', digits=(16, 2), required=True),
        'inc_to': fields.float('Income To', digits=(16, 2), required=True),
        'rate': fields.float('Rate', digits=(16, 2), required=True),
        'max_annual_insurable_earnings': fields.float('Maximum Annual Insurable Earnings', digits=(16, 2), required=True),
        }

    _rec_name = 'inc_from'

class hr_payroll_tax_table_qc_line(orm.Model):
    '''
    Quebec Lines
    '''
    _name = 'hr.payroll.tax.table.qc.line'
    _description = 'Quebec Lines'
    _columns = {
        'table_id': fields.many2one('hr.payroll.tax.table', 'Table'),
        'inc_from': fields.float('Income From', digits=(16, 2), required=True),
        'inc_to': fields.float('Income To', digits=(16, 2), required=True),
        'code0': fields.float('Code 0', digits=(16, 2)),
        'codeA': fields.float('Code A', digits=(16, 2)),
        'codeB': fields.float('Code B', digits=(16, 2)),
        'codeC': fields.float('Code C', digits=(16, 2)),
        'codeD': fields.float('Code D', digits=(16, 2)),
        'codeE': fields.float('Code E', digits=(16, 2)),
        'codeF': fields.float('Code F', digits=(16, 2)),
        'codeG': fields.float('Code G', digits=(16, 2)),
        'codeH': fields.float('Code H', digits=(16, 2)),
        'codeI': fields.float('Code I', digits=(16, 2)),
        'codeJ': fields.float('Code J', digits=(16, 2)),
        'codeK': fields.float('Code K', digits=(16, 2)),
        'codeL': fields.float('Code L', digits=(16, 2)),
        'codeM': fields.float('Code M', digits=(16, 2)),
        'codeN': fields.float('Code N', digits=(16, 2)),
        'codeY': fields.float('Code Y', digits=(16, 2)),
        'codeZ': fields.float('Code Z', digits=(16, 2)),
        }

    _rec_name = 'inc_from'

class hr_payroll_tax_table_rqap_line(orm.Model):
    '''
    RQAP Lines
    '''
    _name = 'hr.payroll.tax.table.rqap.line'
    _description = 'RQAP Lines'
    _columns = {
        'table_id': fields.many2one('hr.payroll.tax.table', 'Table'),
        'inc_from': fields.float('Income From', digits=(16, 2), required=True),
        'inc_to': fields.float('Income To', digits=(16, 2), required=True),
        'employee_contrib': fields.float('Employee contribution', digits=(16, 2)),
        'employer_contrib': fields.float('Employer contribution', digits=(16, 2)),
        'max_annual_insurable_earnings': fields.float('Maximum Annual Insurable Earnings', digits=(16, 2)),
        }

class hr_payroll_tax_table_csst_line(orm.Model):
    '''
    CSST Lines
    '''
    _name = 'hr.payroll.tax.table.csst.line'
    _description = 'CSST Lines'
    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'table_id': fields.many2one('hr.payroll.tax.table', 'Table'),
        }


class hr_deduction_category(orm.Model):
    _name = 'hr.deduction.category'
    _description = 'Categories of employee deductions used for salary rules'
    _columns = {
		'name': fields.char('Category Name', size=52, required=True),
		'code': fields.char('Code', size=52, required=True, help="The code that can be used in the salary rules to identify the deduction"),
		'description': fields.char('Description', size=512, required=True, help="Brief explanation of which benefits the category contains."),
		'default_amount': fields.float('Default Amount', required=True),
        'jurisdiction': fields.selection(get_jurisdiction, 'Jurisdiction', required=True),
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
        'name': fields.char('Deduction Name', size=52, required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True, readonly=True),
        'category_id': fields.many2one('hr.deduction.category', 'Category', required=True, ondelete='cascade', select=True),
        'amount': fields.float('Amount', required=True, help="It is used in computation of the payslip. May be an annual or periodic amount depending on the category. The deduction may be a tax credit."),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date'),
        'code': fields.related('category_id', 'code', type='char', size=52, string='Code'),
    }
    _defaults = {
        'amount' : 0.0,
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
    }
    def onchange_category_id(self, cr, uid, ids, category_id=False):
        res = {'value':{'amount': 0.0,}}
        if category_id:
            category = self.pool.get('hr.deduction.category').browse(cr, uid, category_id)
            res['value']['amount'] = category.default_amount
            res['value']['name'] = category.name
        return res


class hr_benefit_category(orm.Model):
	_name = 'hr.benefit.category'
	_description = 'Categories of employee benefits'
	_columns = {
		'name': fields.char('Benefit Name', size=52, required=True),
		'code': fields.char('Code', size=52, required=True, help="The code that can be used in the salary rules to identify the benefit"),
		'description': fields.char('Description', size=512, required=True, help="Brief explanation of which benefits the category contains."),
		'is_cash': fields.boolean('Is Cash', help="True if the benefit is paid in cash to the employee, False if paid in Kind."),
		'default_amount': fields.float('Default Employee Contribution', required=True, help="Default annual amount that the employee contributes"),
		'default_er_amount': fields.float('Default Employer Contribution', required=True, help="Default annual amount that the employer contributes"),
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
    	'name': fields.char('Deduction Name', size=52, required=True),
        'contract_id': fields.many2one('hr.contract', 'Contract', required=True, ondelete='cascade', select=True),
        'category_id': fields.many2one('hr.benefit.category', 'Benefit', required=True, ondelete='cascade', select=True),
        'amount': fields.float('Employee Contribution', required=True, help="Enter the amount that you would pay for a complete year, even if the duration is lower that a year."),
        'er_amount': fields.float('Employer Contribution', required=True, help="Enter the amount that you would pay for a complete year, even if the duration is lower that a year."),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date'),
        'ei_exempt': fields.related('category_id', 'ei_exempt', type='char', size=52, string='EI Exempt'),
        'fit_exempt': fields.related('category_id', 'fit_exempt', type='char', size=52, string='FIT Exempt'),
        'code': fields.related('category_id', 'code', type='char', size=52, string='Code'),
        'estimated_income': fields.boolean('Estimated Income', help="True if included in the calculation of the estimated annual net income, False otherwise")
    }
    _defaults = {
        'amount' : 0,
        'er_amount' : 0,
        'estimated_income': True,
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
    }
    def onchange_category_id(self, cr, uid, ids, category_id=False):
        res = {'value':{'amount': 0.0,}}
        if category_id:
            category = self.pool.get('hr.benefit.category').browse(cr, uid, category_id)
            res['value']['amount'] = category.default_amount
            res['value']['er_amount'] = category.default_er_amount
            res['value']['name'] = category.name
        return res


class hr_employee(orm.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
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
		'deduction_ids':fields.one2many('hr.employee.deduction', 'employee_id', 'Deductions', help="Deductions for the computation of the employee's payslips"),
    }

    def sum_deductions(self, cr, uid, ids, date_from, date_to, employee_id, deduction_code, estimated_income=False, context=None):
    	
		employee = self.read(cr, uid, employee_id, ['deduction_ids'], context)
		
		deduction_ids = employee['deduction_ids']
		
		attrs = ['code', 'amount', 'category_id', 'date_from', 'date_to']
		if estimated_income:
			attrs.append('estimated_income')
			
		deductions = self.pool.get('hr.employee.deduction').read(cr, uid, deduction_ids, attrs, context)
		
		res = 0
		
		for d in deductions:
			if d['code'] == deduction_code and (estimated_income == False or d['estimated_income'] == True):
				if d['date_start'] <= date_from and (d['date_end'] == False or d['date_end'] >= date_start):
					res += d['amount']
					
				elif b['date_start'] > date_from and (d['date_end'] or d['date_end'] >= date_to):
					res += d['amount'] * (date_to - d['date_start'])/(date_to - date_from)
					
				elif b['date_start'] <= date_from and d['date_end'] < date_to:
					res += d['amount'] * (d['date_end'] - date_from)/(date_to - date_from)
				
				else:
					res += d['amount'] * (d['date_end'] - d['date_start'])/(date_to - date_from)
				
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
            'monthly': 12,
            'bi-monthly': 6,
            'quarterly': 4,
            'semi-annually': 2,
            'annually': 1,
        }
        for contract in self.browse(cr, uid, ids, context):
            if contract.schedule_pay and schedule_pay.get(contract.schedule_pay,
                                                          False):
                res[contract.id] = schedule_pay[contract.schedule_pay]

        return res

    _columns = {
        'pays_per_year': fields.function(
            _get_pays_per_year, method=True, string='Pays Per Year',
            type='float', readonly=True,
        ),
        'weeks_of_vacation': fields.integer('Number of weeks of vacation',
                                            required=True),
		'benefit_line_ids': fields.one2many('hr.contract.benefit', 'contract_id','Employee Benefits'),
    }

    _defaults = {
        'weeks_of_vacation': 2,
    }
    
    def sum_benefits(self, cr, uid, ids, contract_id, date_from, date_to, exemption=False, benefit_code=False, employer=False, context=None):
    	
		contract = self.read(cr, uid, contract_id, ['benefit_line_ids'], context)
		
		benefit_ids = contract['benefit_line_ids']
		
		attrs = ['code', 'amount', 'category_id', 'date_start', 'date_end']
		if exemption:
			attrs.append(exemption)
		
		benefits = self.pool.get('hr.contract.benefit').read(cr, uid, benefit_ids, attrs, context)
		
		res = 0
		for b in benefits:
			if (exemption == False or b[exemption] == False) and (benefit_code == False or b['code'] == benefit_code):
				amount = employer and b['er_amount'] or b['amount']
				
				if b['date_start'] <= date_from and (b['date_end'] == False or b['date_end'] >= date_start):
					res += amount
					
				elif b['date_start'] > date_from and (b['date_end'] == False or b['date_end'] >= date_to):
					res += amount * (date_to - b['date_start'])/(date_to - date_from)
					
				elif b['date_start'] <= date_from and b['date_end'] < date_to:
					res += amount * (b['date_end'] - date_from)/(date_to - date_from)
				
				else:
					res += amount * (b['date_end'] - b['date_start'])/(date_to - date_from)
				
		return res
		
		
    	
    _defaults = {
    }
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
