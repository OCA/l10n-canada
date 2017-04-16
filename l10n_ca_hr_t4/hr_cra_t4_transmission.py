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

from openerp.osv import fields, orm
from dict2xml import dict2xml
from openerp.tools.translate import _


class hr_cra_t4_transmission_rel(orm.Model):
    _name = 'hr.cra.t4.transmission.rel'
    _description = 'Relation between the Transmission XML and T4 slips'

    _columns = {
        'transmission_o_id': fields.many2one(
            'hr.cra.t4.transmission',
            'Transmission Original',
            ondelete='cascade',
        ),
        'transmission_a_id': fields.many2one(
            'hr.cra.t4.transmission',
            'Transmission Modified',
            ondelete='cascade',
        ),
        'transmission_c_id': fields.many2one(
            'hr.cra.t4.transmission',
            'Transmission Cancelled',
            ondelete='cascade',
        ),
        't4_slip_id': fields.many2one(
            'hr.cra.t4',
            'T4 Slip',
            required=True,
            ondelete='cascade',
        ),
    }


class hr_cra_t4_transmission(orm.Model):
    _name = 'hr.cra.t4.transmission'
    _inherit = 'hr.cra.transmission'
    _description = 'T4 Transmission XML'

    def send_slips(
        self, cr, uid, ids, context=None
    ):
        for trans in self.browse(cr, uid, ids, context=context):
            self.pool['hr.cra.t4'].write(
                cr, uid, [t4.id for t4 in trans.t4_slip_ids],
                {'state': 'sent'}, context=context)

    def generate_xml(
        self, cr, uid, ids, context=None
    ):
        for trans in self.browse(cr, uid, ids, context=context):
            # We create an empty list of T4 slip dicts
            t4_slip_dict_list = []
            for t4_slip in trans.t4_slip_ids:

                employee = t4_slip.employee_id

                # T4 slip input amounts
                amounts_dict = {
                    # xml label : (required, amount)
                    'empt_incamt': (False, t4_slip.empt_incamt),
                    'cpp_cntrb_amt': (False, t4_slip.cpp_cntrb_amt),
                    'qpp_cntrb_amt': (False, t4_slip.qpp_cntrb_amt),
                    'empe_eip_amt': (False, t4_slip.empe_eip_amt),
                    'rpp_cntrb_amt': (False, t4_slip.rpp_cntrb_amt),
                    'itx_ddct_amt': (False, t4_slip.itx_ddct_amt),
                    'ei_insu_ern_amt': (True, t4_slip.ei_insu_ern_amt),
                    'cpp_qpp_ern_amt': (True, t4_slip.cpp_qpp_ern_amt),
                    'unn_dues_amt': (False, t4_slip.unn_dues_amt),
                    'chrty_dons_amt': (False, t4_slip.chrty_dons_amt),
                    'padj_amt': (False, t4_slip.padj_amt),
                    'prov_pip_amt': (False, t4_slip.prov_pip_amt),
                    'prov_insu_ern_amt': (False, t4_slip.prov_insu_ern_amt),
                }

                amounts_dict = {
                    label: amounts_dict[label][1]
                    and "%.2f" % amounts_dict[label][1] or '0.00'
                    for label in amounts_dict
                    if amounts_dict[label][0] or amounts_dict[label][1]
                }

                # Employee Name
                # First name and last name are mandatory
                # Initial is optional
                if not t4_slip.firstname or not t4_slip.lastname:
                    raise orm.except_orm(
                        _('Error'),
                        _('The name for employee %s is not correctrly set.')
                        % employee.name
                    )
                name_dict = {
                    'snm': t4_slip.lastname[0:20],
                    'gvn_nm': t4_slip.firstname[0:12],
                }
                if t4_slip.initial:
                    name_dict['init'] = t4_slip.initial

                # Employee Address
                if not employee.address_home_id:
                    raise orm.except_orm(
                        _('Error'),
                        _('The address for employee %s is not correctrly set.')
                        % employee.name)

                address_dict = self.make_address_dict(
                    cr, uid, employee.address_home_id, context=context
                )

                # T4 slip
                if not t4_slip.nas:
                    raise orm.except_orm(
                        _('Error'),
                        _('The SIN for employee %s is missing.')
                        % employee.name
                    )

                t4_slip_dict = {
                    'EMPE_NM': name_dict,
                    'EMPE_ADDR': address_dict,
                    'sin': t4_slip.nas,
                    'bn': trans.ne,

                    # Boolean fields (we need 0 or 1)
                    'cpp_qpp_xmpt_cd': int(t4_slip.cpp_qpp_xmpt_cd),
                    'ei_xmpt_cd': int(t4_slip.ei_xmpt_cd),
                    'prov_pip_xmpt_cd': int(t4_slip.prov_pip_xmpt_cd),

                    'rpt_tcd': t4_slip.type,
                    'empt_prov_cd': t4_slip.empt_prov_cd,
                    'T4_AMT': amounts_dict,
                    'OTH_INFO': {
                        amount.source.xml_tag: amount.amount
                        for amount in t4_slip.other_amount_ids
                    }
                }

                # Optional fields on T4 Slip
                if t4_slip.empt_cd:
                    t4_slip_dict['empt_cd'] = t4_slip.empt_cd

                if t4_slip.rpp_dpsp_rgst_nbr:
                    t4_slip_dict['rpp_dpsp_rgst_nbr'] = \
                        t4_slip.rpp_dpsp_rgst_nbr

                if t4_slip.no_employee:
                    t4_slip_dict['no_employee'] = t4_slip.no_employee

                # Append the current T4 dict to the list of T4 dicts
                t4_slip_dict_list.append(t4_slip_dict)

            # Company
            company = trans.company_id

            # The company address
            company_address_dict = self.make_address_dict(
                cr, uid, company, context=context
            )

            company_name = company.name
            # The CRA wants '&' replaced by '&amp;' in company name
            # The problem is that they also want the name split into
            # 2 rows of 30 chars max. Not worth the time so we remove '&'.
            company_name.replace('&', '')
            name_dict = {
                'l1_nm': company_name[0:30],
                'l2_nm': company_name[30:60],
            }

            # Social insurance numbers of proprietors
            pprtr_sin = {'pprtr_1_sin': trans.proprietor_1_nas}
            if trans.proprietor_2_nas:
                pprtr_sin['pprtr_2_sin'] = trans.proprietor_2_nas

            # Slip return totals
            # Sum amounts over every T4 slips in the slip return
            amount_sum_dict = {
                # xml_label: [field_to_sum_over, sum]
                'tot_empt_incamt': ['empt_incamt', 0],
                'tot_empe_cpp_amt': ['cpp_cntrb_amt', 0],
                'tot_empe_eip_amt': ['empe_eip_amt', 0],
                'tot_rpp_cntrb_amt': ['rpp_cntrb_amt', 0],
                'tot_itx_ddct_amt': ['itx_ddct_amt', 0],
                'tot_padj_amt': ['padj_amt', 0],
                'tot_empr_cpp_amt': ['empr_cpp_amt', 0],
                'tot_empr_eip_amt': ['empr_eip_amt', 0],
            }

            # First, iterate over every T4 slip
            for slip in trans.t4_slip_ids:
                for label in amount_sum_dict:
                    field = amount_sum_dict[label][0]
                    amount_sum_dict[label][1] += slip[field]

            # Then, we convert results to string
            amount_sum_dict = {
                label: amount_sum_dict[label][1]
                and "%.2f" % amount_sum_dict[label][1] or '0.00'
                for label in amount_sum_dict
            }

            # The contact is required
            # all fields are mandatory but the extension
            contact_dict = {
                'cntc_nm': trans.contact_id.name[0:22],
                'cntc_area_cd': trans.contact_area_code,
                'cntc_phn_nbr': trans.contact_phone,
            }
            if trans.contact_extension:
                contact_dict['cntc_extn_nbr'] = \
                    trans.contact_extension

            t4_summary_dict = {
                'bn': trans.ne,
                'EMPR_ADDR': company_address_dict,
                'EMPR_NM': name_dict,
                'CNTC': contact_dict,
                'tx_yr': trans.year,
                'slp_cnt': len(trans.t4_slip_ids),
                'PPRTR_SIN': pprtr_sin,
                'rpt_tcd': trans.type,
                'T4_TAMT': amount_sum_dict,
            }

            # Create the slip return xml structure
            slip_return_dict = {
                'T4': {
                    'T4Slip': t4_slip_dict_list,
                    'T4Summary': t4_summary_dict,
                }
            }

            slip_return_xml = dict2xml(slip_return_dict, 'Return')

            # This function creates the T619 xml structure.
            # This structures embeds the slip return xml.
            # Seperated this in another file, because it is a
            # distinct structure.
            T619_xml = self.make_T619_xml(
                cr, uid, slip_return_xml, trans, context=context
            )

            # We write the resulting XML structure to the XML field
            self.write(
                cr, uid, [trans.id],
                {'xml': T619_xml},
                context=context,
            )

    def _get_t4_slip_ids(
        self, cr, uid, ids, field_name, arg=None, context=None
    ):
        """
        Get the T4 slips whether the transmission type is
        Original, Amended or Cancelled
        """
        res = {}

        for trans in self.browse(cr, uid, ids, context=context):
            t4_ids_field = {
                'O': 't4_original_ids',
                'A': 't4_amended_ids',
                'C': 't4_cancelled_ids',
            }[trans.type]

            res[trans.id] = [
                t4_slip.id for t4_slip in trans[t4_ids_field]
            ]

        return res

    def _count_slips(
        self, cr, uid, ids, field_name, arg=None, context=None
    ):
        """
        Count the T4 slips in transmission
        """
        res = {}

        for trans in self.browse(cr, uid, ids, context=context):
            res[trans.id] = len(trans.t4_slip_ids)

        return res

    _columns = {
        't4_slip_ids': fields.function(
            _get_t4_slip_ids,
            relation='hr.cra.t4',
            type="many2many",
            string="T4 Slips",
            method=True,
        ),
        't4_original_ids': fields.many2many(
            'hr.cra.t4',
            'hr_cra_t4_transmission_rel',
            'transmission_o_id',
            't4_slip_id',
            'T4 Slip originals',
        ),
        't4_amended_ids': fields.many2many(
            'hr.cra.t4',
            'hr_cra_t4_transmission_rel',
            'transmission_a_id',
            't4_slip_id',
            'T4 modified',
        ),
        't4_cancelled_ids': fields.many2many(
            'hr.cra.t4',
            'hr_cra_t4_transmission_rel',
            'transmission_c_id',
            't4_slip_id',
            'T4 to cancel',
        ),
        'number_of_slips': fields.function(
            _count_slips,
            type="integer",
            string="Number of Slips",
            method=True,
        ),
    }
