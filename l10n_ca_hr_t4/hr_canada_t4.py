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
            required=True,
            type="char",
        ),
        'rpp_dpsp_rgst_nbr': fields.integer(
            'Registered pension plan registration number',
        ),
        'cpp_qpp_xmpt_cd': fields.related(
            'employee_id',
            'cpp_exempt',
            string='Canada Pension Plan or Quebec Pension Plan exempt',
            type="boolean",
        ),
        'ei_xmpt_cd': fields.related(
            'employee_id',
            'ei_exempt',
            string='Employment Insurance exempt',
            type="boolean",
        ),
        'prov_pip_xmpt_cd': fields.related(
            'employee_id',
            'pip_exempt',
            string='Provincial parental insurance plan exempt',
            type="boolean",
        ),
        'empt_cd': fields.char(
            'Employment code',
        ),
        'empt_incamt': fields.float(
            'Employment income'
        ),
        'cpp_cntrb_amt': fields.float(
            'Canada Pension Plan contributions'
        ),
        'qpp_cntrb_amt': fields.float(
            'Quebec Pension Plan contributions'
        ),
        'empe_eip_amt': fields.float(
            'Employment Insurance premium'
        ),
        'rpp_cntrb_amt': fields.float(
            'Registered pension plan contributions'
        ),
        'itx_ddct_amt': fields.float(
            'Income tax deducted'
        ),
        'ei_insu_ern_amt': fields.float(
            'Employment Insurance insurable earnings'
        ),
        'cpp_qpp_ern_amt': fields.float(
            'CPP or QPP pensionable earnings'
        ),
        'unn_dues_amt': fields.float(
            'Union dues'
        ),
        'chrty_dons_amt': fields.float(
            'Charitable donations'
        ),
        'padj_amt': fields.float(
            'Pension adjustment'
        ),
        'prov_pip_amt': fields.float(
            'PPIP Premiums'
        ),
        'prov_insu_ern_amt': fields.float(
            'PPIP Insurable earnings'
        ),
        'empr_cpp_amt': fields.float(
            "Employer's CPP contributions"
        ),
        'empr_eip_amt': fields.float(
            "Employer's EI premiums"
        ),
        'other_amount_ids': fields.one2many(
            'hr.canada.t4.other_amount',
            'slip_id',
            'Other Income Amounts',
        ),
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

            # Get all payslip of the employee for the period
            payslips = [
                payslip for payslip in
                slip.employee_id.payslip_ids
                if slip.year == int(payslip.date_from[0:4])
            ]

            # Create a dict with the sum from every
            # required payslip rules
            required_fields_dict = {
                'empt_incamt': 'FIT_I',
                'cpp_cntrb_amt': 'CPP_EE_C',
                'qpp_cntrb_amt': 'QPP_EE_C',
                'empe_eip_amt': 'EI_EE_C',
                'itx_ddct_amt': 'FIT_T',
                'ei_insu_ern_amt': 'EI_EE_MAXIE',
                'cpp_qpp_ern_amt': 'CPP_EE_MAXIE',
                'prov_pip_amt': 'PPIP_EE_C',
                'prov_insu_ern_amt': 'PPIP_EE_MAXIE',
                'empr_cpp_amt': 'CPP_ER_C',
                'empr_eip_amt': 'EI_ER_C',
                'rpp_cntrb_amt': 'RPP_EE_C',
            }
            rules_sum_dict = {
                rule_code: 0
                for rule_code in required_fields_dict.values()
            }

            for payslip in payslips:
                for line in payslip.details_by_salary_rule_category:
                    if line.code in rules_sum_dict:
                        rules_sum_dict[line.salary_rule_id.code] += \
                            line.total

                    elif line.code == 'QPP_EE_MAXIE':
                        rules_sum_dict['CPP_EE_MAXIE'] += line.total

                    elif line.code == 'RCA_EE_C':
                        rules_sum_dict['RPP_EE_C'] += line.total

            # get the dict of fields to return
            self.write(
                cr, uid,
                [slip.id],
                {
                    field: rules_sum_dict[required_fields_dict[field]]
                    for field in required_fields_dict.keys()
                },
                context=context,
            )
