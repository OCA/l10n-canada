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


class hr_canada_t4_other_amount(orm.Model):
    """
    Used to enter the additional information on T4
    """
    _name = 'hr.canada.t4.other_amount'
    _description = 'Other Income Amounts on T4 Slip'
    _columns = {
        'slip_id': fields.many2one(
            'hr.canada.t4',
            required=True,
            ondelete='cascade',
        ),
        # Needed to split the source into 2 because one view field
        # could not carry that many
        'source': fields.selection(
            [
                ('hm_brd_lodg_amt', "30 - Housing, board and lodging amount"),
                ('spcl_wrk_site_amt', "31 - Special work site amount"),
                ('prscb_zn_trvl_amt', "32 - Travel in a prescribed\
zone amount"),
                ('med_trvl_amt', "33 - Medical travel amount"),
                ('prsnl_vhcl_amt', "34 - Personal use of employer\
automobile amount"),
                ('rsn_per_km_amt', "35 - Total Reasonable Per-Kilometre\
Allowance amount"),
                ('low_int_loan_amt', "36 - Interest-free and low-interest\
loan amount"),
                ('empe_hm_loan_amt', "37 - Employee home-relocation loan\
deduction amount"),
                ('stok_opt_ben_amt', "97 - Stock option benefit amount\
before February 28, 2000"),
                ('sob_a00_feb_amt', "38 - Security options benefits"),
                ('shr_opt_d_ben_amt', "98 - Stock option and share\
deduction 110(1) (d) amount before February 28, 2000"),
                ('sod_d_a00_feb_amt', "39 - Security options\
deductions 110(1)(d)"),
                ('oth_tx_ben_amt', "40 - Other taxable allowance and\
benefit amount"),
                ('shr_opt_d1_ben_amt', "99 - Stock option and share\
deduction 110(1) (d.1) amount before February 28, 2000"),
                ('sod_d1_a00_feb_amt', "41 - Security options deduction\
110(1)(d.1)"),
                ('empt_cmsn_amt', "42 - Employment commission amount"),
                ('cfppa_amt', "43 - Canadian forces personnel and police\
allowance"),
                ('dfr_sob_amt', "53 - Deferred security option benefits"),
                ('elg_rtir_amt', "66 - Eligible retiring allowances"),
                ('nelg_rtir_amt', "67 - Non-eligible retiring allowances"),
                ('indn_elg_rtir_amt', "68 - Status Indian Eligible\
retiring allowances"),
                ('indn_nelg_rtir_amt', "69 - Status Indian Non-eligible\
retiring allowances"),
                ('mun_ofcr_examt', "70 - Municipal officer expense allowance\
amount"),
                ('indn_empe_amt', "71 - Status Indian employee amount"),
                ('oc_incamt', "72 - Outside of Canada employment income\
amount- Section 122.3"),
                ('oc_dy_cnt', "73 - Employment outside of Canada Day Count"),
                ('pr_90_cntrbr_amt', "74 - Pre-1990 past service contributions\
while a contributor"),
                ('pr_90_ncntrbr_amt', "75 - Pre-1990 past service\
contributions while not a contributor"),
                ('cmpn_rpay_empr_amt', "77 - Workers’ compensation benefit\
repaid to the employer amount"),
                ('fish_gro_ern_amt', "78 - Fishers - Gross earnings"),
                ('fish_net_ptnr_amt', "79 - Fishers - Net Partnership Amount"),
                ('fish_shr_prsn_amt', "80 - Fishers - Shareperson Amount"),
                ('plcmt_emp_agcy_amt', "81 - Placement or employment agency"),
                ('drvr_taxis_oth_amt', "82 - Driver of taxi or other\
passenger-carrying vehicle"),
                ('brbr_hrdrssr_amt', "83 - Barber or hairdresser"),
                ('pub_trnst_pass_amt', "84 - Public transit pass"),
                ('epaid_hlth_pln_amt', "85 - Employee-paid premiums for\
private health services plans"),
                ('stok_opt_csh_out_eamt', "86 - Stock option cash-out\
expense"),
                ('vlntr_firefighter_xmpt_amt', "87 - Volunteer Firefighter\
Exempt Amount"),
                ('indn_txmpt_sei_amt', "88 - Indian (exempt income) –\
Self-employment"),
            ],
            'Source of the amount',
            required=True,
        ),
        'amount': fields.float(
            'Amount',
            digits=(15, 2),
            required=True,
        ),
    }
