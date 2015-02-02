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

    @api.one
    def _amount_in_words(self, currency_id):
        context = self._context.copy()
        lang = context.get('lang', config.get('lang', None))
        if self.partner_id:
            lang = self.partner_id.lang or lang

        if lang:
            context['lang'] = lang

        env = self.env(context=context)
        amount = self.amount
        currency = self.env['res.currency'].with_env(env).browse(currency_id)
        if lang:
            try:
                amount_in_word = num2words(int(amount), lang=lang)
            except NotImplementedError:
                amount_in_word = num2words(int(amount))
        else:
            amount_in_word = num2words(int(amount))

        currency_name = currency.print_on_check
        cents = int(amount * 100) % 100

        res = _(u'{amount} and {cents}/100 {currency}').format(
            amount=amount_in_word,
            cents=cents,
            currency=currency_name,
        )

        if len(res) < 79:
            res = u" ".join([u"*" * (80 - len(res)), res])

        return res

    @api.multi
    def print_check(self):
        if not self.ids:
            return {}

        check_layout_report = {
            'top': 'account.print.check.top',
            'middle': 'account.print.check.middle',
            'bottom': 'account.print.check.bottom',
            'top_ca': 'l10n.ca.account.print.check.top',
            'middle_ca': 'l10n.ca.account.print.check.middle',
        }

        check_layout = self[0].company_id.check_layout
        return {
            'type': 'ir.actions.report.xml',
            'report_name': check_layout_report[check_layout],
            'datas': {
                'model': 'account.voucher',
                'id': self.ids[0],
                'ids': self.ids,
                'report_type': 'pdf'
            },
            'nodestroy': True
        }

    @api.multi
    def proforma_voucher(self):
        # update all amount in word when perform a voucher
        for voucher in self:
            currency = self._get_current_currency(voucher.id)
            amount_in_word = voucher._amount_in_words(currency)[0]
            voucher.write({'amount_in_word': amount_in_word})

        return super(AccountVoucher, self).proforma_voucher()
