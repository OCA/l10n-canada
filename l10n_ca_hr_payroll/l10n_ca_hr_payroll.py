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
    """
    Canadian Tax Payroll Table
    """
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
    """
    Federal Lines
    """
    _name = 'hr.payroll.tax.table.federal.line'
    _description = 'Federal Lines'
    _rec_name = 'inc_from'
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


class hr_payroll_tax_table_ei_line(orm.Model):
    """
    Employment Insurance Lines
    """
    _name = 'hr.payroll.tax.table.ei.line'
    _description = 'Employment Insurance Lines'
    _rec_name = 'inc_from'
    _columns = {
        'table_id': fields.many2one('hr.payroll.tax.table', 'Table'),
        'inc_from': fields.float('Income From', digits=(16, 2), required=True),
        'inc_to': fields.float('Income To', digits=(16, 2), required=True),
        'rate': fields.float('Rate', digits=(16, 2), required=True),
        'max_annual_insurable_earnings': fields.float(
            'Maximum Annual Insurable Earnings',
            digits=(16, 2), required=True,
        ),
    }


class hr_payroll_tax_table_qc_line(orm.Model):
    """
    Quebec Lines
    """
    _name = 'hr.payroll.tax.table.qc.line'
    _description = 'Quebec Lines'
    _rec_name = 'inc_from'
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


class hr_payroll_tax_table_rqap_line(orm.Model):
    """
    RQAP Lines
    """
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
    """
    CSST Lines
    """
    _name = 'hr.payroll.tax.table.csst.line'
    _description = 'CSST Lines'
    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'table_id': fields.many2one('hr.payroll.tax.table', 'Table'),
    }


class hr_employee(orm.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
        'ei_exempt': fields.boolean('EI Exempt'),
        'td1f': fields.selection([
            ('code1', '1'),
            ('code2', '2'),
            ('code3', '3'),
            ('code4', '4'),
            ('code5', '5'),
            ('code6', '6'),
            ('code7', '7'),
            ('code8', '8'),
            ('code9', '9'),
            ('code10', '10'),
            ('code0', '0')
        ], 'Federal Claim Code', required=True),
        'td1p': fields.selection([
            ('codeA', 'A'),
            ('codeB', 'B'),
            ('codeC', 'C'),
            ('codeD', 'D'),
            ('codeE', 'E'),
            ('codeF', 'F'),
            ('codeG', 'G'),
            ('codeH', 'H'),
            ('codeI', 'I'),
            ('codeJ', 'J'),
            ('codeK', 'K'),
            ('codeL', 'L'),
            ('codeM', 'M'),
            ('codeN', 'N'),
            ('codeY', 'Y'),
            ('codeZ', 'Z'),
            ('code0', '0')
        ], 'Provincial Claim Code', required=True),
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
        'f1': fields.float(name='Childcare/Alimony (F1)', digits=(16, 2), help="""\
Annual deductions such as child care expenses and support payments, etc.,
authorized by a tax services office or tax centre"""),
        'f2': fields.float('Alimony/Maint Garnish (F2)', digits=(16, 2), help="""\
Alimony or maintenance payments required by a legal document to be
payroll-deducted authorized by a tax services office or tax centre"""),
        'hd': fields.float('Prescribed Zone (HD)', digits=(16, 2), help="""\
Annual deduction for living in a prescribed zone as indicated on Form TD1"""),
        'lcf': fields.float('Fed Labour sponsored funds (LCF)', digits=(16, 2),
                            help="Federal labour-sponsored funds tax credit"),
        'lcp': fields.float(
            'Prov Labour sponsored funds (LCP)', digits=(16, 2),
            help="Provincial or territorial labour-sponsored funds tax credit"),
        'f': fields.float('RSP/RPP/RCA (F)', digits=(16, 2), help="""
Payroll deductions for employee contributions to a registered pension plan (RPP),
a registered retirement savings plan (RRSP),
or a retirement compensation arrangement (RCA)"""),
        'l': fields.float('Extra Tax Deductions (L)', digits=(16, 2),
                          help="Extra tax deductions requested for the pay period."),
        'k3': fields.float('Federal Medical (K3)', digits=(16, 2), help="""\
Other federal tax credits, such as medical expenses and charitable donations
authorized by a tax services office or tax centre"""),
        'u1': fields.float('Union Dues (U1)', digits=(16, 2), help="Union dues"),
        'y': fields.float('MB/ON Extra Tax Reduction(Y)', digits=(16, 2), help="""\
Extra provincial or territorial tax reduction based on applicable amounts
reported on the provincial or territorial Form TD1"""),
        'td1': fields.float('Personal Tax Credits Return (TD1)', digits=(16, 2),
                            required=True, help="Personal Tax Credits Return"),
        'eeins': fields.float('Insurance - Employee Contribution (EeINS)', digits=(16, 2), required=True),
        'erins': fields.float('Insurance - Employer Contribution (ErINS)', digits=(16, 2), required=True),
    }

    _defaults = {
        'td1f': 'code1',
        'td1p': 'codeA',
        'td1': 11038.00,
        'eeins': 0.00,
        'erins': 0.00,
    }


class hr_contract(orm.Model):
    _inherit = 'hr.contract'

    def _get_pays_per_year(self, cr, uid, ids, names, arg, context=None):
        """
        @param ids: ID of contract
        @return: The number of pays per year
        """
        res = {}
        # FIXME: Should likely pull these values from somewhere else, depending on whether a 52 or 53 year week is used
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
            if contract.schedule_pay and schedule_pay.get(contract.schedule_pay, False):
                res[contract.id] = schedule_pay[contract.schedule_pay]

        return res

    _columns = {
        'pays_per_year': fields.function(
            _get_pays_per_year, method=True, string='Pays Per Year',
            type='float', readonly=True,
        ),
        'weeks_of_vacation': fields.integer('Number of weeks of vacation', required=True),
    }

    _defaults = {
        'weeks_of_vacation': 2,
    }
