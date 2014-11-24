# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp import api, models, _

from openerp.tools import config
# Odoo's built-in routines for converting numbers to words is pretty bad,
# especially in French This is why we use the library below. You can get it at:
# https://pypi.python.org/pypi/num2words
from num2words import num2words


class AccountVoucher(models.Model):
    _inherit = _name = 'account.voucher'

    @api.model
    def _amount_to_text(self, amount, currency_id):
        context = self._context.copy()
        lang = context.get('lang', config.get('lang', None))
        if self.partner_id:
            lang = self.partner_id.lang or lang

        if lang:
            context['lang'] = lang

        currency = self.env['res.currency'].browse(currency_id)
        if lang:
            try:
                amount_in_word = num2words(int(amount), lang=lang)
            except NotImplementedError:
                amount_in_word = num2words(int(amount))
        else:
            amount_in_word = num2words(int(amount))

        currency_name = currency.print_on_check
        cents = int(amount * 100) % 100
        total_length = len(amount_in_word) + len(currency_name)
        if total_length < 67:
            stars = '*' * (67 - total_length)
        else:
            stars = ''

        res = _(u'{amount} and {cents}/100 {currency}').format(
            amount=amount_in_word,
            cents=cents,
            currency=currency_name,
        )

        if len(res) < 79:
            res = u" ".join([res, u"*" * (80 - len(res))])

        return res

    def print_check(self, cr, uid, ids, context=None):
        if not ids:
            return {}

        check_layout_report = {
            'top': 'account.print.check.top',
            'middle': 'account.print.check.middle',
            'bottom': 'account.print.check.bottom',
            'top_ca': 'l10n.ca.account.print.check.top',
            'middle_ca': 'l10n.ca.account.print.check.middle',
        }

        check_layout = self.browse(cr, uid, ids[0],
                                   context=context).company_id.check_layout
        return {
            'type': 'ir.actions.report.xml',
            'report_name': check_layout_report[check_layout],
            'datas': {
                'model': 'account.voucher',
                'id': ids and ids[0] or False,
                'ids': ids and ids or [],
                'report_type': 'pdf'
            },
            'nodestroy': True
        }

    def proforma_voucher(self, cr, uid, ids, context=None):
        # update all amount in word when perform a voucher
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        for voucher in self.browse(cr, uid, ids, context=context):
            amount = voucher.amount
            currency = self._get_current_currency(cr, uid, voucher.id,
                                                  context=context)
            amount_in_word = self._amount_to_text(cr, uid, amount, currency,
                                                  context=context)
            voucher.write({'amount_in_word': amount_in_word})

        return super(AccountVoucher, self).proforma_voucher(cr, uid, ids,
                                                            context=context)
