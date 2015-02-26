# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp.tools.translate import _


class res_partner(orm.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def onchange_sin(self, cr, uid, ids, sin):
        ret = {'value': 0}

        def digits_of(n):
            return [int(d) for d in str(n)]

        def luhn_checksum(sin):
            digits = digits_of(sin)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = 0
            checksum += sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10

        def is_luhn_valid(sin):
            return luhn_checksum(sin) == 0

        if is_luhn_valid(sin):
            ret['value'] = sin
        else:
            ret['value'] = 0
            ret['warning'] = {
                'title': 'Error',
                'message': _('The number provided is not a valid SIN number !')
            }
        return ret

    _columns = {
        'sin': fields.float('SIN', digits=(9, 0),
                            help="Social Insurance Number (9 digits)"),
    }
