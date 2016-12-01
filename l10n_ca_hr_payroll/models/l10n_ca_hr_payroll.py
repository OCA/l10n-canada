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

from openerp import api, fields, models, _
from datetime import datetime, date, time

GET_JURISDICTION = [('federal', 'Federal'), 
                    ('provincial', 'Provincial')]

GET_TYPE = [('federal', 'Federal'),
            ('ei', 'Employment Insurance'),
            ('qc', 'Quebec'),
            ('rqap', 'RQAP / RRQ'),
            ('csst', 'CSST')]

GET_td1f = [('code1', '1'), ('code2', '2'), ('code3', '3'), ('code4', '4'),
            ('code5', '5'), ('code6', '6'), ('code7', '7'), ('code8', '8'),
            ('code9', '9'), ('code10', '10'), ('code0', '0')]

GET_td1p = [('codeA', 'A'), ('codeB', 'B'), ('codeC', 'C'), ('codeD', 'D'),
            ('codeE', 'E'), ('codeF', 'F'), ('codeG', 'G'), ('codeH', 'H'),
            ('codeI', 'I'), ('codeJ', 'J'), ('codeK', 'K'), ('codeL', 'L'),
            ('codeM', 'M'), ('codeN', 'N'), ('codeY', 'Y'), ('codeZ', 'Z'),
            ('code0', '0')]


class HrPayrollTaxTable(models.Model):
    """
    Canadian Tax Payroll Table
    """
    _name = 'hr.payroll.tax.table'
    _description = 'Canadian Tax Payroll Table'

    @api.onchange('year')
    def _onchange_year(self):
        aux_name = 'Tax Table: ' + str(year) 
        if not self.state_id: aux_name += ' / Federal'
        else: aux_name += ' / Provincial - ' + self.state_id.code
        self.name = aux_name

    # simple fields
    name = fields.Char(string='Description', size=32)
    year = fields.Integer(string='Year', required=True)
    date_from = fields.Date(string='Date from')
    date_to = fields.Date(string='Date to')
    jurisdiction = fields.Selection(GET_JURISDICTION, 'Jurisdiction', 
                                    required=True, default='federal')
    # relational fields - Many2one
    state_id = fields.Many2one('res.country.state', string='Province')
    type = fields.Selection(GET_TYPE, 'Type', required=True, 
                            default='federal')
    # relational fields - One2many
    line_federal_ids = fields.One2many('hr.payroll.tax.table.federal.line', 
                                       'table_id', string='Lines')
    line_ei_ids = fields.One2many('hr.payroll.tax.table.ei.line', 'table_id', 
                                  string='Lines')
    line_qc_ids = fields.One2many('hr.payroll.tax.table.qc.line', 'table_id', 
                                  string='Lines')
    line_rqap_ids = fields.One2many('hr.payroll.tax.table.rqap.line', 
                                    'table_id', string='Lines')
    line_csst_ids = fields.One2many('hr.payroll.tax.table.csst.line', 
                                    'table_id', string='Lines')


class HrPayrollTaxTableFederalLine(models.Model):
    """
    Federal lines
    """
    _name = 'hr.payroll.tax.table.federal.line'
    _description = 'Federal lines'
    _rec_name = 'inc_from'

    # simple fields
    inc_from = fields.Float(string='Income from', required=True, 
                            digits=(16, 2))
    inc_to = fields.Float(string='Income to', required=True, digits=(16, 2))
    code0 = fields.Float(string='Code 0', digits=(16, 2))
    code1 = fields.Float(string='Code 1', digits=(16, 2))
    code2 = fields.Float(string='Code 2', digits=(16, 2))
    code3 = fields.Float(string='Code 3', digits=(16, 2))
    code4 = fields.Float(string='Code 4', digits=(16, 2))
    code5 = fields.Float(string='Code 5', digits=(16, 2))
    code6 = fields.Float(string='Code 6', digits=(16, 2))
    code7 = fields.Float(string='Code 7', digits=(16, 2))
    code8 = fields.Float(string='Code 8', digits=(16, 2))
    code9 = fields.Float(string='Code 9', digits=(16, 2))
    code10 = fields.Float(string='Code 10', digits=(16, 2))
    # relational fields - Many2one
    table_id = fields.Many2one('hr.payroll.tax.table', string='Table')


class HrPayrollTaxTableEILine(models.Model):
    """
    Employment insurance lines
    """
    _name = 'hr.payroll.tax.table.ei.line'
    _description = 'Employment insurance lines'
    _rec_name = 'inc_from'

    # simple fields
    inc_from = fields.Float(string='Income from', required=True, 
                            digits=(16, 2))
    inc_to = fields.Float(string='Income to', required=True, digits=(16, 2))
    rate = fields.Float(string='Rate', required=True, digits=(16, 2))
    max_annual_insurable_earnings = fields.Float(required=True, digits=(16, 2),
                                    string='Maximum Annual Insurable Earnings') 
    # relational fields - Many2one
    table_id = fields.Many2one('hr.payroll.tax.table', string='Table')


class HrPayrollTaxTableQCLine(models.Model):
    """
    Quebec lines
    """
    _name = 'hr.payroll.tax.table.qc.line'
    _description = 'Quebec lines'
    _rec_name = 'inc_from'
    
    # simple fields
    inc_from = fields.Float(string='Income from', required=True, 
                            digits=(16, 2))
    inc_to = fields.Float(string='Income to', required=True, digits=(16, 2))
    code0 = fields.Float(string='Code 0', digits=(16, 2))
    codeA = fields.Float(string='Code A', digits=(16, 2))
    codeB = fields.Float(string='Code B', digits=(16, 2))
    codeC = fields.Float(string='Code C', digits=(16, 2))
    codeD = fields.Float(string='Code D', digits=(16, 2))
    codeE = fields.Float(string='Code E', digits=(16, 2))
    codeF = fields.Float(string='Code F', digits=(16, 2))
    codeG = fields.Float(string='Code G', digits=(16, 2))
    codeH = fields.Float(string='Code H', digits=(16, 2))
    codeI = fields.Float(string='Code I', digits=(16, 2))
    codeJ = fields.Float(string='Code J', digits=(16, 2))
    codeK = fields.Float(string='Code K', digits=(16, 2))
    codeL = fields.Float(string='Code L', digits=(16, 2))
    codeM = fields.Float(string='Code M', digits=(16, 2))
    codeN = fields.Float(string='Code N', digits=(16, 2))
    codeY = fields.Float(string='Code Y', digits=(16, 2))
    codeZ = fields.Float(string='Code Z', digits=(16, 2))
    # relational fields - Many2one
    table_id = fields.Many2one('hr.payroll.tax.table', string='Table')


class HrPayrollTaxTableRQAPLine(models.Model):
    """
    RQAP lines
    """
    _name = 'hr.payroll.tax.table.rqap.line'
    _description = 'RQAP lines'
    
    # simple fields
    inc_from = fields.Float(string='Income from', required=True, 
                            digits=(16, 2))
    inc_to = fields.Float(string='Income to', required=True, digits=(16, 2))
    employee_contrib = fields.Float(string='Employee contribution', 
                                    digits=(16, 2))
    employer_contrib = fields.Float(string='Employer contribution', 
                                    digits=(16, 2))
    max_annual_insurable_earnings = fields.Float(required=True, digits=(16, 2),
                                    string='Maximum Annual Insurable Earnings')
    # relational fields - Many2one
    table_id = fields.Many2one('hr.payroll.tax.table', string='Table')


class HrPayrollTaxTableCSSTLine(models.Model):
    """
    CSST lines
    """
    _name = 'hr.payroll.tax.table.csst.line'
    _description = 'CSST lines'
    
    # simple fields
    name = fields.Char(string='Description', size=256)
    # relational fields - Many2one
    table_id = fields.Many2one('hr.payroll.tax.table', string='Table')    
    

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # simple fields
    ei_exempt = fields.Boolean(string='EI Exempt')
    td1f = fields.Selection(GET_td1f, 'Federal claim code', required=True, 
                            default='code1')
    td1p = fields.Selection(GET_td1p, 'Provincial claim code', required=True, 
                            default='codeA')
    cpp_exempt = fields.Boolean(string='CPP/QPP Exempt')
    qpip_exempt = fields.Boolean(string='QPIP Exempt')
    cpp_ytd_adj = fields.Float(string='CPP/QPP YTD Adjustment',
                               help='''Amount to adjust CPP/QPP for 
                               calculations.\n Used if employee has 
                               contributed elsewhere and will be factored in 
                               when calculating maximum CPP payment''')
    ei_ytd_adj = fields.Float(string='EI YTD Adjustment',
                              help='''Amount to adjust EI for calculations.
                              \nUsed if employee has contributed elsewhere 
                              and will be factored in when calculating maximum 
                              EI payment''')
    vac_pay = fields.Float(string='Vacation Pay %', digits=(16, 2))
    f1 = fields.Float(string='Childcare/Alimony (F1)', digits=(16, 2),
                      help='''Annual deductions such as child care expenses 
                      and support payments, etc., authorized by a tax services 
                      office or tax centre''')
    f2 = fields.Float(string='Alimony/Maint Garnish (F2)', digits=(16, 2), 
                      help='''Alimony or maintenance payments required by a 
                      legal document to be payroll-deducted authorized by a 
                      tax services office or tax centre''')
    hd = fields.Float(string='Prescribed Zone (HD)', digits=(16, 2), 
                      help='''Annual deduction for living in a prescribed 
                      zone as indicated on Form TD1''')
    lcf = fields.Float(string='Fed Labour sponsored funds (LCF)', 
                       digits=(16, 2), help='''Provincial or territorial 
                       labour-sponsored funds tax credit''')
    lcp = fields.Float(string='Prov Labour sponsored funds (LCP)', 
                       digits=(16, 2), help='''Provincial or territorial 
                       labour-sponsored funds tax credit''')
    f = fields.Float(string='RSP/RPP/RCA (F)', digits=(16, 2), 
                     help='''Payroll deductions for employee contributions to 
                     a registered pension plan (RPP), a registered retirement 
                     savings plan (RRSP), or a retirement compensation 
                     arrangement (RCA)''')
    l = fields.Float(string='Extra Tax Deductions (L)', digits=(16, 2), 
                     help='''Extra tax deductions requested for the pay 
                     period''')
    k3 = fields.Float(string='Federal Medical (K3)', digits=(16, 2), 
                      help='''Other federal tax credits, such as medical 
                      expenses and charitable donations authorized by a tax 
                      services office or tax centre''')
    u1 = fields.Float(string='Union Dues (U1)', digits=(16, 2), 
                      help='''Union dues''')
    y = fields.Float(string='MB/ON Extra Tax Reduction(Y)', digits=(16, 2), 
                      help='''Extra provincial or territorial tax reduction 
                      based on applicable amounts reported on the provincial 
                      or territorial Form TD1''')
    td1 = fields.Float(string='Personal Tax Credits Return (TD1)', 
                       digits=(16, 2), required=True, default=11038.00, 
                       help='''Personal Tax Credits Return''')
    eeins = fields.Float(string='Insurance - Employee Contribution (EeINS)', 
                         digits=(16, 2), required=True, default=0.00)
    erins = fields.Float(string='Insurance - Employer Contribution (ErINS)', 
                         digits=(16, 2), required=True, default=0.00)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    @api.depends('pays_per_year')
    def _get_pays_per_year(self):
        last_date = str(datetime.now().year) + '-12-31'
        weekly = datetime.strptime(last_date, '%Y-%m-%d').strftime("%W")
        schedule_pay = {
            'weekly': weekly,
            'bi-weekly': int(weekly) / 2,
            'monthly': 12,
            'bi-monthly': 6,
            'quarterly': 4,
            'semi-annually': 2,
            'annually': 1,
        }
        for contract in self:
            my_schedule = contract.schedule_pay or False
            if my_schedule and schedule_pay.get(my_schedule):
                contract.pays_per_year = schedule_pay[my_schedule]
                
    # simple fields
    pays_per_year = fields.Integer(string='Pays Per Year', readonly=True,
                                 compute='_get_pays_per_year',
                                 help='The number of pays per year')
    weeks_of_vacation = fields.Integer(string='Number of weeks of vacation',
                                       required=True, default=2)
    
