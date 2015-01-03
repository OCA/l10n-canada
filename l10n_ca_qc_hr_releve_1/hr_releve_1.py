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
import unicodedata
from openerp.tools.translate import _
from pydmtx import DataMatrix
import os
import base64


class hr_releve_1(orm.Model):
    _name = 'hr.releve_1'
    _inherit = 'hr.canada.fiscal_slip'
    _description = 'Relevé 1'

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
            required_fields_dict = {
                'a_revenu_emploi': 'QIT_G',
                'b_cotisation_rrq': 'QPP_EE_C',
                'c_cotisation_ass_emploi': 'EI_EE_C',
                'd_cotisation_rpa': 'RPP_EE_C',
                'e_impot_que': 'QIT_A',
                'g_salaire_admis_rrq': 'QPP_EE_MAXIE',
                'h_cotisation_rqap': 'PPIP_EE_C',
                'i_salaire_admis_rqap': 'PPIP_EE_MAXIE',
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

            # get the dict of fields to return
            res = {
                field: rules_sum_dict[required_fields_dict[field]]
                for field in required_fields_dict.keys()
            }

            # If the slip as no number, assign one
            if not slip.number:
                res['number'] = self.pool['res.company'].\
                    get_next_rq_sequential_number(
                        cr, uid, 'hr.releve_1', slip.company_id.id, slip.year,
                        context=context)

            self.write(cr, uid, [slip.id], res, context=context)

    def _make_dtmx_string_field(
        self, cr, uid, value, nb_chars,
        mandatory=False, field_name=False, context=None
    ):
        """
        This function transform a unicode, int or float into
        an ascii string of a precise length

        In every case, it completes the string with spaces
        """
        # Empty fields
        if not value:
            if mandatory:
                raise orm.except_orm(
                    _('Error'), _('The field %s is missing') %
                    field_name,
                )
            res = ' ' * nb_chars

        # Floats: removes the floating point but keeps every digit
        # Adds spaces before the string
        elif isinstance(value, float):
            value = str(int(value * 100))
            res = "%s%s" % (' ' * (nb_chars - len(value)), value)

        # Integers: the same logic as with floats
        elif isinstance(value, (int, long)):
            value = str(value)
            res = "%s%s" % (' ' * (nb_chars - len(value)), value)

        # Unicode: converts to ascii and adds missing spaces after
        else:
            value = unicodedata.normalize(
                'NFKD', unicode(value)
            ).encode('ascii', 'ignore')
            res = "%s%s" % (value, ' ' * (nb_chars - len(value)),)

        # We check that the field is the proper size
        if len(res) > nb_chars:
            raise orm.except_orm(
                _('Error'), _('The value %s is too long') % res)

        return res

    def _make_address_dtmx_barcode_string(
            self, cr, uid, address, context=None):
        res = ""

        # 3 fields of 30 chars
        for field_detail in [
            (address.street, True, _('Street Line 1')),
            (address.street2, False, _('Street Line 2')),
            (address.city, True, _('City')),
        ]:
            # Get the first 30 chars of the field
            field = field_detail[0]
            field = field and field[0:30]

            res += self._make_dtmx_string_field(
                cr, uid,
                value=field, nb_chars=30,
                mandatory=field_detail[1], field_name=field_detail[2],
                context=context)

        # Province - 2 chars
        res += self._make_dtmx_string_field(
            cr, uid, address.state_id.code, 2,
            mandatory=True, field_name=_('Province'),
            context=context)

        # Postal Code - 6 chars
        res += self._make_dtmx_string_field(
            cr, uid, address.zip, 6,
            mandatory=True, field_name=_('Zip Code'),
            context=context)

        return res

    def make_dtmx_barcode(self, cr, uid, ids, context=None):
        """
        Create the DataMatrix Codebar
        """
        for releve_1 in self.browse(cr, uid, ids, context=context):
            # Code related to the slip type
            dtmx_barcode_string = self._make_dtmx_string_field(
                cr, uid, "12EE", nb_chars=4, context=context)

            # Authorization number
            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, "FS9999999", nb_chars=9, context=context)

            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, releve_1.company_id.rq_preparator_number, 8,
                field_name=_("Preparator Number"),
                context=context)

            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, releve_1.year, nb_chars=4, context=context)

            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, releve_1.type, nb_chars=1, context=context)

            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, releve_1.previous_number, nb_chars=9, context=context)

            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, releve_1.reference, nb_chars=9, context=context)

            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, releve_1.number, nb_chars=9, context=context)

            # amounts - 9 chars
            for field in [
                "a_revenu_emploi", "b_cotisation_rrq",
                "c_cotisation_ass_emploi", "d_cotisation_rpa",
                "e_impot_que", "f_cotisation_syndicale",
                "g_salaire_admis_rrq", "h_cotisation_rqap",
                "i_salaire_admis_rqap", "j_regime_ass_maladie",
                "k_voyage", "l_autre_avantage",
                "m_commission", "n_don_bienfaisance",
                "o_autre_revenu", "p_regime_ass_inter_entr",
                "q_salaire_differe", "r_revenu_indien",
                "s_pourboire_recu",
            ]:
                dtmx_barcode_string += self._make_dtmx_string_field(
                    cr, uid, releve_1[field], nb_chars=9, context=context)

            # P if tip earned - 1 char
            dtmx_barcode_string += releve_1.s_pourboire_recu and 'P' or ' '

            for field in [
                "t_pourboire_attribue", "u_retraite_progressive",
                "v_nourriture_logement", "w_vehicule",
            ]:
                dtmx_barcode_string += self._make_dtmx_string_field(
                    cr, uid, releve_1[field], nb_chars=9, context=context)

            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, releve_1.o_autre_revenu_source.code, nb_chars=2,
                context=context)

            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, int(releve_1.nas), nb_chars=9, context=context)

            # Reference Number (not mandatory) - 20 chars
            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, releve_1.reference, nb_chars=20,
                context=context)

            for field_detail in [
                (releve_1.lastname, True, _('Last Name')),
                (releve_1.firstname, True, _('First Name')),
            ]:
                # Get the first 30 chars of the field
                field = field_detail[0]
                field = field and field[0:30]

                dtmx_barcode_string += self._make_dtmx_string_field(
                    cr, uid, value=field, nb_chars=30,
                    mandatory=field_detail[1], field_name=field_detail[2],
                    context=context)

            # Employee address
            if not releve_1.address_home_id:
                raise orm.except_orm(
                    _('Error'), _('The employee home address is not set')
                )
            dtmx_barcode_string += self._make_address_dtmx_barcode_string(
                cr, uid, releve_1.address_home_id, context=context)

            # company name - 60 chars
            dtmx_barcode_string += self._make_dtmx_string_field(
                cr, uid, value=releve_1.company_id.name, nb_chars=60,
                context=context)

            # Company address
            dtmx_barcode_string += self._make_address_dtmx_barcode_string(
                cr, uid, releve_1.company_id, context=context)

            # Loop for every additional information
            for i in range(0, 4):
                if releve_1.other_info_ids and \
                        len(releve_1.other_info_ids) > i:

                    other_info = releve_1.other_info_ids[i]

                    # get the source of the additional information
                    source = other_info.source and other_info.source \
                        or other_info.source_case_o

                    # write the source
                    dtmx_barcode_string += self._make_dtmx_string_field(
                        cr, uid, source, 5, context=context)

                    # get the amount of the additional information
                    dtmx_barcode_string += self._make_dtmx_string_field(
                        cr, uid, other_info.amount, 15, context=context)

                else:
                    dtmx_barcode_string += self._make_dtmx_string_field(
                        cr, uid, False, 20,
                        context=context)

            # Make DataMatrix code
            dmtx_code = DataMatrix()
            dmtx_code.encode(dtmx_barcode_string)

            # Put the datamatrix code in a temp file
            directory = os.path.join('/tmp')
            if not os.path.isdir(directory):
                os.makedirs(directory)

            filename = directory + '/releve_1_datamatrix_code.jpg'
            dmtx_code.save(filename, 'JPEG')

            # Get a binary field by decoding the temp file
            b64_data = base64.encodestring(open(filename, "rb").read())

            self.write(
                cr, uid, [releve_1.id], {
                    'dtmx_barcode_string': dtmx_barcode_string,
                    'dtmx_barcode_image': b64_data,
                }, context=context)

            # Remove the temp file
            os.remove(filename)

    _columns = {
        'type': fields.selection(
            [
                ('R', 'Original'),
                ('A', 'Amended'),
                ('D', 'Cancelled'),
            ],
            'Type',
            required=True,
        ),
        'number': fields.integer(
            'Sequential Number',
            select=True,
        ),
        'previous_number': fields.related(
            'amended_slip',
            'number',
            type="integer",
            string='Previous Sequential Number',
        ),
        'amended_slip': fields.many2one(
            'hr.releve_1', 'Amended Slip'),

        'a_revenu_emploi': fields.float(
            'A - RevenuEmploi', digits=(15, 2), required=True),

        'b_cotisation_rrq': fields.float(
            'B - CotisationRRQ', digits=(15, 2), required=True),

        'c_cotisation_ass_emploi': fields.float(
            'C - CotisationAssEmploi', digits=(15, 2), required=True),

        'd_cotisation_rpa': fields.float(
            'D - CotisationRPA', digits=(15, 2)),

        'e_impot_que': fields.float(
            'E - ImpotQue', digits=(15, 2), required=True),

        'f_cotisation_syndicale': fields.float(
            'F - CotisationSyndicale', digits=(15, 2)),

        'g_salaire_admis_rrq': fields.float(
            'G - SalaireAdmisRRQ', digits=(15, 2), required=True),

        'h_cotisation_rqap': fields.float(
            'H - CotisationRQAP', digits=(15, 2), required=True),

        'i_salaire_admis_rqap': fields.float(
            'I - SalaireAdmisRQAP', digits=(15, 2), required=True),

        'j_regime_ass_maladie': fields.float(
            'J - RegimeAssMaladie', digits=(15, 2)),

        'k_voyage': fields.float(
            'K - Voyage', digits=(15, 2)),

        'l_autre_avantage': fields.float(
            'L - AutreAvantage', digits=(15, 2)),

        'm_commission': fields.float(
            'M - Commission', digits=(15, 2)),

        'n_don_bienfaisance': fields.float(
            'N - DonBienfaisance', digits=(15, 2)),

        'o_autre_revenu': fields.float(
            'O - AutreRevenu', digits=(15, 2)),
        'o_autre_revenu_source': fields.many2one(
            'hr.releve_1.other_info.source',
            string="Code (case O)"),

        'p_regime_ass_inter_entr': fields.float(
            'P - RegimeAssInterEntr', digits=(15, 2)),

        'q_salaire_differe': fields.float(
            'Q - SalaireDiffere', digits=(15, 2)),

        'r_revenu_indien': fields.float(
            'R - RevenuIndien', digits=(15, 2)),

        's_pourboire_recu': fields.float(
            'S - PourboireRecu', digits=(15, 2)),

        't_pourboire_attribue': fields.float(
            'T - PourboireAttribue', digits=(15, 2)),

        'u_retraite_progressive': fields.float(
            'U - RetraiteProgressive', digits=(15, 2)),

        'v_nourriture_logement': fields.float(
            'V - NourritureLogement', digits=(15, 2)),

        'w_vehicule': fields.float(
            'W - Vehicule', digits=(15, 2)),

        'other_info_ids': fields.one2many(
            'hr.releve_1.other_info',
            'slip_id',
            'Additional Information'),

        'dtmx_barcode_string': fields.text(
            'Datamatrix Code'),

        'dtmx_barcode_image': fields.binary(
            'DataMatrix Bar Code'),

    }
    _defaults = {
        'type': 'R',
        'a_revenu_emploi': 0,
        'b_cotisation_rrq': 0,
        'c_cotisation_ass_emploi': 0,
        'd_cotisation_rpa': 0,
        'e_impot_que': 0,
        'g_salaire_admis_rrq': 0,
        'h_cotisation_rqap': 0,
        'i_salaire_admis_rqap': 0,
    }

    def _check_other_info(self, cr, uid, ids, context=None):
        for slip in self.browse(cr, uid, ids, context=context):

            # Check that their is maximum 4 amounts
            if len(slip.other_info_ids) > 4:
                return False

            # For each amount, the source must be different
            sources = [amount.source for amount in slip.other_info_ids]
            if len(set(sources)) != len(sources):
                return False

        return True

    _constraints = [
        (
            _check_other_info,
            """Error! You can enter a maximum of 4 other amounts
and they must be different from each other""",
            ['other_info_ids']
        ),
    ]
