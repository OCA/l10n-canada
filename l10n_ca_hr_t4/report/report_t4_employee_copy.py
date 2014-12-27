# -*- coding:utf-8 -*-#########################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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

from openerp.report import report_sxw


class report_t4_employee_copy(report_sxw.rml_parse):
    """
    This report is a T4 slip for the employee.
    It is not a copy to be sent to the CRA.
    """
    def __init__(self, cr, uid, name, context):
        super(report_t4_employee_copy, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'other_amounts_codes': {
                'hm_brd_lodg_amt': 30,
                'spcl_wrk_site_amt': 31,
                'prscb_zn_trvl_amt': 32,
                'med_trvl_amt': 33,
                'prsnl_vhcl_amt': 34,
                'rsn_per_km_amt': 35,
                'low_int_loan_amt': 36,
                'empe_hm_loan_amt': 37,
                'stok_opt_ben_amt': 97,
                'sob_a00_feb_amt': 38,
                'shr_opt_d_ben_amt': 98,
                'sod_d_a00_feb_amt': 39,
                'oth_tx_ben_amt': 40,
                'shr_opt_d1_ben_amt': 99,
                'sod_d1_a00_feb_amt': 41,
                'empt_cmsn_amt': 42,
                'cfppa_amt': 43,
                'dfr_sob_amt': 53,
                'elg_rtir_amt': 66,
                'nelg_rtir_amt': 67,
                'indn_elg_rtir_amt': 68,
                'indn_nelg_rtir_amt': 69,
                'mun_ofcr_examt': 70,
                'indn_empe_amt': 71,
                'oc_incamt': 72,
                'oc_dy_cnt': 73,
                'pr_90_cntrbr_amt': 74,
                'pr_90_ncntrbr_amt': 75,
                'cmpn_rpay_empr_amt': 77,
                'fish_gro_ern_amt': 78,
                'fish_net_ptnr_amt': 79,
                'fish_shr_prsn_amt': 80,
                'plcmt_emp_agcy_amt': 81,
                'drvr_taxis_oth_amt': 82,
                'brbr_hrdrssr_amt': 83,
                'pub_trnst_pass_amt': 84,
                'epaid_hlth_pln_amt': 85,
                'stok_opt_csh_out_eamt': 86,
                'vlntr_firefighter_xmpt_amt': 87,
                'indn_txmpt_sei_amt': 88,
            },
        })

report_sxw.report_sxw(
    'report.t4_employee_copy',
    'hr.canada.t4',
    'l10n_ca_hr_t4/report/report_t4_employee_copy.rml',
    parser=report_t4_employee_copy,
    header=False
)
