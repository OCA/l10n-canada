# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

from openerp.osv import orm, fields
from openerp.tools.translate import _

CURRENCY_NAMES = {
    # First, the important ones
    'USD': _('U.S. dollar'),
    'EUR': _('European Euro'),
    'GBP': _('U.K. pound sterling'),
    'CAD': _('Canadian dollar'),
    'AUD': _('Australian dollar'),
    'JPY': _('Japanese yen'),
    'INR': _('Indian rupee'),
    'NZD': _('New Zealand dollar'),
    'CHF': _('Swiss franc'),
    'ZAR': _('South African rand'),
    # The rest, alphabetical
    'AED': _('U.A.E. dirham'),
    'ANG': _('Neth. Antilles florin'),
    'ARS': _('Argentine peso'),
    'ATS': _('Austrian schilling'),
    'BBD': _('Barbadian dollar'),
    'BEF': _('Belgian franc'),
    'BHD': _('Bahraini dinar'),
    'BRL': _('Brazilian real'),
    'BSD': _('Bahamian dollar'),
    'CLP': _('Chilean peso'),
    'CNY': _('Chinese renminbi'),
    'COP': _('Colombian peso'),
    'CZK': _('Czech Republic koruna'),
    'DEM': _('German deutsche mark'),
    'DKK': _('Danish krone'),
    'EGP': _('Egyptian Pound'),
    'ESP': _('Spanish peseta'),
    'FIM': _('Finnish markka'),
    'FJD': _('Fiji dollar'),
    'FRF': _('French franc'),
    'GHC': _('Ghanaian cedi (old)'),
    'GHS': _('Ghanaian cedi'),
    'GRD': _('Greek drachma'),
    'GTQ': _('Guatemalan quetzal'),
    'HKD': _('Hong Kong dollar'),
    'HNL': _('Honduran lempira'),
    'HRK': _('Croatian kuna'),
    'HUF': _('Hungarian forint'),
    'IDR': _('Indonesian rupiah'),
    'IEP': _('Irish pound'),
    'ILS': _('Israeli new shekel'),
    'ISK': _('Icelandic krona'),
    'ITL': _('Italian lira'),
    'JMD': _('Jamaican dollar'),
    'KRW': _('South Korean won'),
    'LKR': _('Sri Lanka rupee'),
    'LTL': _('Lithuanian litas'),
    'LVL': _('Latvian lats'),
    'MAD': _('Moroccan dirham'),
    'MMK': _('Myanmar (Burma) kyat'),
    'MXN': _('Mexican peso'),
    'MYR': _('Malaysian ringgit'),
    'MZN': _('Mozambican metical'),
    'NIO': _('Nicaraguan córdoba'),
    'NLG': _('Netherlands guilder'),
    'NOK': _('Norwegian krone'),
    'PAB': _('Panamanian balboa'),
    'PEN': _('Peruvian new sol'),
    'PHP': _('Philippine peso'),
    'PKR': _('Pakistan rupee'),
    'PLN': _('Polish zloty'),
    'PTE': _('Portuguese escudo'),
    'RON': _('Romanian new leu'),
    'RSD': _('Serbian dinar'),
    'RUB': _('Russian rouble'),
    'SAR': _('Saudi riyal'),
    'SEK': _('Swedish krona'),
    'SGD': _('Singapore dollar'),
    'SIT': _('Slovenian tolar'),
    'SKK': _('Slovak koruna'),
    'THB': _('Thai baht'),
    'TND': _('Tunisian dinar'),
    'TRL': _('Turkish lira'),
    'TWD': _('Taiwanese new dollar'),
    'UAH': _('Ukrainian hryvnia'),
    'VEB': _('Venezuelan bolivar'),
    'VEF': _('Venezuelan bolivar fuerte'),
    'VND': _('Vietnamese dong'),
    'XAF': _('CFA franc'),
    'XCD': _('East Caribbean dollar'),
    'XPF': _('CFP franc'),
}

UNKNOWN_CURRENCY = _('Unknown')

class res_currency(orm.Model):
    _inherit = 'res.currency'

    def _get_display_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        for currency in self.browse(cr, uid, ids, context):
            display_name = CURRENCY_NAMES.get(currency.name, UNKNOWN_CURRENCY)
            res[currency.id] = display_name
        return res
    
    _columns = {
        'display_name': fields.function(_get_display_name, type='char', size=64, string="Display Name"),
    }
