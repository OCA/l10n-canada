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


def get_amount_line(amount, currency, lang):
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


class AccountVoucher(models.Model):
    _inherit = _name = 'account.voucher'

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id,
                        journal_id, currency_id, ttype, date,
                        payment_rate_currency_id, company_id, context=None):
        """
        Inherited - add amount_in_word and allow_check_writting in returned
        value dictionary
        """
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        default = super(AccountVoucher, self).onchange_amount(
            cr, uid, ids, amount, rate, partner_id, journal_id, currency_id,
            ttype, date, payment_rate_currency_id, company_id, context=context)

        if 'value' in default:
            amount = default['value'].get('amount', amount)
            amount_in_word = self._get_amount_in_word(cr,
                                                      uid,
                                                      currency_id=currency_id,
                                                      amount=amount,
                                                      context=context)

            if amount_in_word is not None:
                default['value'].update({'amount_in_word': amount_in_word})
            if journal_id:
                allow_check_writing = self.pool.get('account.journal').browse(
                    cr, uid, journal_id, context=context).allow_check_writing
                default['value'].update({'allow_check': allow_check_writing})
        return default

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

        check_layout = self.browse(cr, uid, ids[0], context=context).company_id.check_layout
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
            amount_in_word = self._get_amount_in_word(cr, uid, i_id, context=context)
            self.write(cr, uid, i_id, {'amount_in_word': amount_in_word}, context=context)

        return super(AccountVoucher, self).proforma_voucher(cr, uid, ids, context=context)

    def _get_amount_in_word(self, cr, uid, i_id=None, currency_id=None, amount=None, context=None):
        if context is None:
            context = {}
        if amount is None:
            amount = self.browse(cr, uid, i_id, context=context).amount

        # get lang
        supplier_lang = context.get('lang', config.get('lang', None))
        if i_id is not None:
            partner_id = self.browse(cr, uid, i_id, context=context).partner_id
            if partner_id:
                supplier_lang = partner_id.lang

        context = dict(context, lang=supplier_lang)
        if currency_id is None:
            if i_id is None:
                return None
            currency_id = self._get_current_currency(cr, uid, i_id, context=context)

        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)
        # get the amount_in_word
        return get_amount_line(amount, currency, supplier_lang)


class VoucherLine(models.Model):
    _inherit = _name = 'account.voucher.line'

    @api.multi
    def get_suppl_inv_num(self):
        for rec in self:
            move_line = self.env['account.move.line'].browse(rec.move_line_id.id)
            rec.supplier_invoice_number = (
                move_line.invoice and
                move_line.invoice.supplier_invoice_number or ''
            )

    supplier_invoice_number = fields.Char(size=64, string="Supplier Invoice Number",
                                          compute=get_suppl_inv_num)
