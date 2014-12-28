# -*- coding:utf-8 -*-char(

##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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


class hr_canada_t4(orm.Model):
    _name = 'hr.canada.t4'
    _inherit = 'hr.canada.fiscal_slip'

    _columns = {
        'empt_prov_cd': fields.selection(
            [
                ('AB', 'Alberta'),
                ('BC', 'British Columbia'),
                ('MB', 'Manitoba'),
                ('NB', 'New Brunswick'),
                ('NL', 'Newfoundland and Labrador'),
                ('NS', 'Nova Scotia'),
                ('NT', 'Northwest Territories'),
                ('NU', 'Nunavut'),
                ('ON', 'Ontario'),
                ('PE', 'Prince Edward Island'),
                ('QC', 'Quebec'),
                ('SK', 'Saskatchewan'),
                ('YT', 'Yukon Territories'),
                ('US', 'United States'),
                ('ZZ', 'Other'),
            ],
            string='Province, territory or country of employment code',
            required=True, type="char"),

        'rpp_dpsp_rgst_nbr': fields.integer(
            'Registered pension plan registration number'),

        'cpp_qpp_xmpt_cd': fields.related(
            'employee_id', 'cpp_exempt',
            string='Canada Pension Plan or Quebec Pension Plan exempt',
            type="boolean"),

        'ei_xmpt_cd': fields.related(
            'employee_id', 'ei_exempt',
            string='Employment Insurance exempt',
            type="boolean"),

        'prov_pip_xmpt_cd': fields.related(
            'employee_id', 'pip_exempt',
            string='Provincial parental insurance plan exempt',
            type="boolean"),

        'empt_cd': fields.char('Employment code'),
        'empt_incamt': fields.float('Employment income'),
        'cpp_cntrb_amt': fields.float('Canada Pension Plan contributions'),
        'qpp_cntrb_amt': fields.float('Quebec Pension Plan contributions'),
        'empe_eip_amt': fields.float('Employment Insurance premium'),
        'rpp_cntrb_amt': fields.float('Registered pension plan contributions'),
        'itx_ddct_amt': fields.float('Income tax deducted'),
        'ei_insu_ern_amt': fields.float(
            'Employment Insurance insurable earnings'),
        'cpp_qpp_ern_amt': fields.float('CPP or QPP pensionable earnings'),
        'unn_dues_amt': fields.float('Union dues'),
        'chrty_dons_amt': fields.float('Charitable donations'),
        'padj_amt': fields.float('Pension adjustment'),
        'prov_pip_amt': fields.float('PPIP Premiums'),
        'prov_insu_ern_amt': fields.float('PPIP Insurable earnings'),
        'empr_cpp_amt': fields.float("Employer's CPP contributions"),
        'empr_eip_amt': fields.float("Employer's EI premiums"),

        'other_amount_ids': fields.one2many(
            'hr.canada.t4.other_amount', 'slip_id', 'Other Income Amounts'),
    }

    defaults = {
        'empt_prov_cd': lambda self, cr, uid, context:
        self.pool.get('res.users').browse(
            cr, uid, uid, context=context
        ).company_id.default_province_employment,
    }

    def _check_other_amounts(self, cr, uid, ids, context=None):
        for slip in self.browse(cr, uid, ids, context=context):

            # Check that their is maximum 6 amounts
            if len(slip.other_amount_ids) > 6:
                return False

            # For each amount, the source must be different
            sources = [amount.source for amount in slip.other_amount_ids]
            if len(set(sources)) != len(sources):
                return False

        return True

    def _check_cpp_and_qpp(self, cr, uid, ids, context=None):
        for slip in self.browse(cr, uid, ids, context=context):
            if slip.cpp_cntrb_amt and slip.qpp_cntrb_amt:
                return False
        return True

    _constraints = [
        (
            _check_other_amounts,
            """Error! You can enter a maximum of 6 other amounts
and they must be different from each other""",
            ['other_amount_ids']
        ),
        (
            _check_cpp_and_qpp,
            """Error! You can not have an amount for both cpp and qpp
   contributions""",
            ['cpp_cntrb_amt', 'qpp_cntrb_amt']
        ),
    ]

    def compute_amounts(
        self, cr, uid, ids, context=None
    ):
        for slip in self.browse(cr, uid, ids, context=context):
            # Get all payslip of the employee for the year
            date_from = str(slip.year) + '-01-01'
            date_to = str(slip.year) + '-12-31'
            payslip_ids = self.pool['hr.payslip'].search(
                cr, uid, [
                    ('employee_id', '=', slip.employee_id.id),
                    ('date_from', '>=', date_from),
                    ('date_to', '<=', date_to),
                    ('state', '=', 'done'),
                ], context=context)

            payslips = self.pool['hr.payslip'].browse(
                cr, uid, payslip_ids, context=context)

            # Create a dict with the sum from every
            # required payslip rules
            rules_sum_dict = {
                'FIT_I_OTHER_WAGE': ['empt_incamt', 0],
                'CPP_EE_C': ['cpp_cntrb_amt', 0],
                'QPP_EE_C': ['qpp_cntrb_amt', 0],
                'EI_EE_C': ['empe_eip_amt', 0],
                'FIT_T': ['itx_ddct_amt', 0],
                'EI_EE_MAXIE': ['ei_insu_ern_amt', 0],
                'CPP_EE_MAXIE': ['cpp_qpp_ern_amt', 0],
                'PPIP_EE_C': ['prov_pip_amt', 0],
                'PPIP_EE_MAXIE': ['prov_insu_ern_amt', 0],
                'CPP_ER_C': ['empr_cpp_amt', 0],
                'EI_ER_C': ['empr_eip_amt', 0],
                'RPP_EE_C': ['rpp_cntrb_amt', 0],
            }

            for payslip in payslips:
                for line in payslip.details_by_salary_rule_category:
                    if line.code in rules_sum_dict:
                        rules_sum_dict[line.code][1] += \
                            line.total

                    # QPP Earnings are included in cpp_qpp_ern_amt
                    elif line.code == 'QPP_EE_MAXIE':
                        rules_sum_dict['CPP_EE_MAXIE'][1] += line.total

                    # RCA contributions are included in rpp_cntrb_amt
                    # RCA is a more specific kind of RPP
                    elif line.code == 'RCA_EE_C':
                        rules_sum_dict['RPP_EE_C'][1] += line.total

            # get the dict of fields to return
            slip.write({
                rules_sum_dict[rule][0]: rules_sum_dict[rule][1]
                for rule in rules_sum_dict
            })
