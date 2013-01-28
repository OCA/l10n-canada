#-*- coding:utf-8 -*-
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

from osv import fields, osv

"""
class hr_payroll_tax_table(osv.osv):
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
            'fed_prov': fields.selection([
                ('federal','Federal'),
                ('provincial','Provincial')], 'Federal/Provincial', required=True),
            'province': fields.many2one('res.country.state', 'Province'),
            'line_ids': fields.one2many('hr.payroll.tax.table.line', 'table_id', 'Lines'),
            }

    _defaults = {
            'fed_prov': 'federal',
            }
hr_payroll_tax_table()

class hr_payroll_tax_table_line(osv.osv):
    '''
    Canadian Tax Payroll Table Lines
    '''
    _name = 'hr.payroll.tax.table.line'
    _description = 'Canadian Tax Payroll Table Lines'
    _columns = {
        'name': fields.char('Name', size=64),
        'code': fields.char('Code', size=16),
        'inc_from': fields.float('Income From', digits=(16, 2)),
        'inc_to': fields.float('Income To', digits=(16, 2)),
        'rate': fields.float('Rate', digits=(16, 2)),
        'table_id': fields.many2one('hr.payroll.tax.table', 'Table'),
        }
hr_payroll_tax_table_line()
"""

class hr_employee(osv.osv):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
        'ei_exempt': fields.boolean('EI Exempt'),
        'td1f': fields.selection([(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(0,0)], 'Federal Claim Code', required=True),
        'td1p': fields.selection([(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(0,0)], 'Provincial Claim Code', required=True),
        'cpp_exempt': fields.boolean('CPP/QPP Exempt'),
        'qpip_exempt': fields.boolean('QPIP Exempt'),
        'cpp_ytd_adj': fields.float('CPP/QPP YTD Adjustment', help="Amount to adjust CPP/QPP for calculations. Used if employee has contributed elsewhere and will be factored in when calculating maximum CPP payment"),
        'ei_ytd_adj': fields.float('EI YTD Adjustment', help="Amount to adjust EI for calculations. Used if employee has contributed elsewhere and will be factored in when calculating maximum EI payment"),
        'vac_pay': fields.float('Vacation Pay %', digits=(16,2)),
        'f1': fields.float('Childcare/Alimony (F1)', digits=(16,2), help="Annual deductions such as child care expenses and support payments, etc., authorized by a tax services office or tax centre"),
        'f2': fields.float('Alimony/Maint Garnish (F2)', digits=(16,2), help="Alimony or maintenance payments required by a legal document to be payroll-deducted authorized by a tax services office or tax centre"),
        'hd': fields.float('Prescribed Zone (HD)', digits=(16,2), help="Annual deduction for living in a prescribed zone as indicated on Form TD1"),
        'lcf': fields.float('Fed Labour sponsored funds (LCF)', digits=(16,2), help="Federal labour-sponsored funds tax credit"),
        'lcp': fields.float('Prov Labour sponsored funds (LCP)', digits=(16,2), help="Provincial or territorial labour-sponsored funds tax credit"),
        'f': fields.float('RSP/RPP/RCA (F)', digits=(16,2), help="Payroll deductions for employee contributions to a registered pension plan (RPP), a registered retirement savings plan (RRSP), or a retirement compensation arrangement (RCA)"),
        'l': fields.float('Extra Tax Deductions (L)', digits=(16,2), help="Extra tax deductions requested for the pay period."),
        'k3': fields.float('Federal Medical (K3)', digits=(16,2), help="Other federal tax credits, such as medical expenses and charitable donations authorized by a tax services office or tax centre"),
        'u1': fields.float('Union Dues (U1)', digits=(16,2), help="Union dues"),
        'y': fields.float('MB/ON Extra Tax Reduction(Y)', digits=(16,2), help="Extra provincial or territorial tax reduction based on applicable amounts reported on the provincial or territorial Form TD1"),
            }

    _defaults = {
        'td1f': 1,
        'td1p': 1,
        }

hr_employee()

class hr_contract(osv.osv):
    _inherit = 'hr.contract'

    def _get_pays_per_year(self, cr, uid, ids, names, arg, context=None):
        """
        @param ids: ID of contract
        @return: The number of pays per year
        """
        res = {}
        #FIXME: Should likely pull these values from somewhere else, depending on whether a 52 or 53 year week is used
        schedule_pay = {
            'monthly': 12,
            'quarterly': 4,
            'semi-annually': 2,
            'annually': 1,
            'weekly': 52,
            'bi-weekly': 26,
            'bi-monthly': 6,
            }
        for contract in self.browse(cr, uid, ids, context):
            if contract.schedule_pay and schedule_pay.get(contract.schedule_pay, False):
                res[contract.id] = schedule_pay[contract.schedule_pay]

        return res

    _columns = {
        'pays_per_year': fields.function(_get_pays_per_year, method=True, string='Pays Per Year', type='float', readonly=True),
        }

hr_contract()

            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
