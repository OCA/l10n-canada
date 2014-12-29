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


class hr_cra_t4_other_amount(orm.Model):
    """
    Used to enter the additional information on T4
    """
    _name = 'hr.cra.t4.other_amount'
    _description = 'Other Income Amount on T4 Slip'
    _columns = {
        'slip_id': fields.many2one(
            'hr.cra.t4',
            required=True,
            ondelete='cascade',
        ),
        'source': fields.many2one(
            'hr.cra.t4.other_amount.source',
            'Source of the amount',
            required=True,
        ),
        'amount': fields.float(
            'Amount',
            digits=(15, 2),
            required=True,
        ),
    }


class hr_cra_t4_other_amount_source(orm.Model):
    """
    The source of an other amount on T4 slip
    """
    _name = 'hr.cra.t4.other_amount.source'
    _description = 'Other Income Amounts on T4 Slip'
    _columns = {
        'name': fields.char(
            'Description',
            required=True,
        ),
        'xml_tag': fields.char(
            'XML Transmission Tag',
            required=True,
            help="The tag requested by Canada Revenu Agency for "
            "XML transmission"
        ),
        'box_number': fields.integer(
            'Box Number',
            required=True,
            help="Box number on T4 slip",
        ),
    }
