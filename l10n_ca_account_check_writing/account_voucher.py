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
# OpenERP's built-in routines for converting numbers to words is pretty bad, especially in French
# This is why we use the library below. You can get it at:
# https://pypi.python.org/pypi/num2words
from num2words import num2words

# For the words we use in custom_translation(), we have to put dummy _() calls here so that OpenERP
# picks them up during .pot generation
_("and")

def custom_translation(s, lang):
    # OpenERP uses the current stack frame, yes, the *stack frame* to determine which language _()
    # should translate a string in. If we want to translate a string in another language, such as
    # a supplier's language, we have to resort to hacks such as this one. "context" is sought after
    # in the stackframe, so we have to set it.
    context = {'lang': lang}
    return _(s)

def get_amount_line(amount, currency, lang):
    try:
        amount_in_word = num2words(int(amount), lang=lang[:2])
    except NotImplementedError:
        amount_in_word = num2words(int(amount))
    currency_name = currency.print_on_check
    cents = int(amount * 100) % 100
    total_length = len(amount_in_word) + len(currency_name)
    if total_length < 87:
        stars = '*' * (87 - total_length)
    else:
        stars = ''
    AND = custom_translation("and", lang)
    amount_line_fmt = '{amount_in_word} {AND} {cents}/100 {currency_name} {stars}'
    if lang.startswith('fr'):
        amount_line_fmt = '{amount_in_word} {currency_name} {AND} {cents}/100 {stars}'
    return amount_line_fmt.format(**vars())

class account_voucher(orm.Model):
    _inherit = 'account.voucher'

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id,
                        journal_id, currency_id, ttype, date,
                        payment_rate_currency_id, company_id, context=None):
        """ Inherited - add amount_in_word and allow_check_writting in returned value dictionary """
        if not context:
            context = {}
        default = super(account_voucher, self).onchange_amount(
            cr, uid, ids, amount, rate, partner_id, journal_id, currency_id,
            ttype, date, payment_rate_currency_id, company_id, context=context)
        if 'value' in default:
            amount = 'amount' in default['value'] and default['value']['amount'] or amount
            if ids:
                supplier_lang = self.browse(cr, uid, ids[0], context=context).partner_id.lang
            else:
                # It's a new record and we don't have access to our supplier lang yet
                supplier_lang = 'en_US'
            supplier_context = context.copy()
            # for some calls, such as the currency browse() call, we want to separate our user's
            # language from our supplier's. That's why we need a separate context.
            supplier_context['lang'] = supplier_lang
            currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=supplier_context)
            amount_line = get_amount_line(amount, currency, supplier_lang)
            default['value'].update({'amount_in_word': amount_line})
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
            #'bottom_ca': 'l10n.ca.account.print.check.bottom',
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
        if type(context) is not dict:
            context = {}
        i_id = ids[0]
        amount = self.browse(cr, uid, i_id, context=context).amount
        supplier_lang = self.browse(cr, uid, i_id, context=context).partner_id.lang
        supplier_context = context.copy()
        # for some calls, such as the currency browse() call, we want to separate our user's
        # language from our supplier's. That's why we need a separate context.
        supplier_context['lang'] = supplier_lang
        currency_id = self._get_current_currency(cr, uid, i_id, context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=supplier_context)
        # get the amount_in_word
        amount_line = get_amount_line(amount, currency, supplier_lang)
        self.write(cr, uid, [i_id], {'amount_in_word': amount_line})

        return super(account_voucher, self).proforma_voucher(cr, uid, ids, context=context)

# By default, the supplier reference number is not so easily accessible from a voucher line because
# there's no direct link between the voucher and the invoice. Fortunately, there was this recently
# submitted patch from Lorenzo Battistini (Agile) BG at
# https://code.launchpad.net/~elbati/account-payment/adding_account_voucher_supplier_invoice_number_7/+merge/165622
# which solves this exact problem and I shamelessely copied that code, which works well.

class voucher_line(orm.Model):
    _inherit = 'account.voucher.line'
    
    def get_suppl_inv_num(self, cr, uid, move_line_id, context=None):
        move_line = self.pool.get('account.move.line').browse(cr, uid, move_line_id, context)
        return move_line.invoice and move_line.invoice.supplier_invoice_number or ''

    def _get_supplier_invoice_number(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = ''
            if line.move_line_id:
                res[line.id] = self.get_suppl_inv_num(cr, uid, line.move_line_id.id, context=context)
        return res
    
    _columns = {
        'supplier_invoice_number': fields.function(_get_supplier_invoice_number, type='char', size=64, string="Supplier Invoice Number"),
    }
