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

from openerp import api, fields, models, _

from openerp.tools import config
# Odoo's built-in routines for converting numbers to words is pretty bad,
# especially in French This is why we use the library below. You can get it at:
# https://pypi.python.org/pypi/num2words
from num2words import num2words

# For the words we use in custom_translation(), we have to put dummy _() calls
# here so that Odoo picks them up during .pot generation
_("and")


def custom_translation(s, lang):
    # Odoo uses the current stack frame, yes, the *stack frame* to determine
    # which language _() should translate a string in. If we want to translate
    # a string in another language, such as a supplier's language, we have to
    # resort to hacks such as this one. "context" is sought after in the
    # stackframe, so we have to set it.
    context = {'lang': lang}  # NOQA
    return _(s)


class AccountVoucher(models.Model):
    _inherit = _name = 'account.voucher'

    @api.model
    def _amount_to_text(self, amount, currency_id):
        context = self._context
        lang = context.get('lang', config.get('lang', None))
        if self.partner_id:
            lang = self.partner_id.lang or lang

        currency = self.env['res.currency'].browse(currency_id)
        try:
            amount_in_word = num2words(int(amount), lang=lang[:2])
        except NotImplementedError:
            amount_in_word = num2words(int(amount))
        currency_name = currency.print_on_check
        cents = int(amount * 100) % 100
        total_length = len(amount_in_word) + len(currency_name)
        if total_length < 67:
            stars = '*' * (67 - total_length)
        else:
            stars = ''
        AND = custom_translation("and", lang)
        amount_line_fmt = u'{amount} {AND} {cents}/100 {currency} {stars}'
        if lang.startswith('fr'):
            amount_line_fmt = u'{amount} {currency} {AND} {cents}/100 {stars}'
        return amount_line_fmt.format(
            amount=amount_in_word,
            cents=cents,
            currency=currency_name,
            stars=stars,
            AND=AND,
        )

    def print_check(self, cr, uid, ids, context=None):
        if not ids:
            return {}

        check_layout_report = {
            'top': 'account.print.check.top',
            'middle': 'account.print.check.middle',
            'bottom': 'account.print.check.bottom',
            'top_ca': 'l10n.ca.account.print.check.top',
            'middle_ca': 'l10n.ca.account.print.check.middle',
            # 'bottom_ca': 'l10n.ca.account.print.check.bottom',
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
        for i_id in ids:
            amount_in_word = self._get_amount_in_word(cr, uid, i_id,
                                                      context=context)
            self.write(cr, uid, i_id, {'amount_in_word': amount_in_word},
                       context=context)

        return super(AccountVoucher, self).proforma_voucher(cr, uid, ids,
                                                            context=context)


class VoucherLine(models.Model):
    _inherit = _name = 'account.voucher.line'

    @api.multi
    def get_suppl_inv_num(self):
        move_obj = self.env['account.move.line']
        for rec in self:
            move_line = move_obj.browse(rec.move_line_id.id)
            rec.supplier_invoice_number = (
                move_line.invoice and
                move_line.invoice.supplier_invoice_number or ''
            )

    supplier_invoice_number = fields.Char(size=64,
                                          string="Supplier Invoice Number",
                                          compute=get_suppl_inv_num)
