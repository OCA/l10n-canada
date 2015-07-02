# -*- coding: utf-8 -*-
# #############################################################################
#
# Odoo, Open Source Management Solution
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
import logging
_logger = logging.getLogger(__name__)
import re
import time
from openerp.tools import config
from openerp.report import report_sxw
from openerp.tools.translate import _
# Odoo's built-in routines for converting numbers to words is pretty bad,
# especially in French
# This is why we use the library below. You can get it at:
# https://pypi.python.org/pypi/num2words
from num2words import num2words
# For the words we use in custom_translation(), we have to put dummy _()
# calls here so that Odoo picks them up during .pot generation
_("and")


class report_print_check(report_sxw.rml_parse):
    MAX_LINES = 10

    def __init__(self, cr, uid, name, context):
        super(report_print_check, self).__init__(cr, uid, name, context)
        self.cr = cr
        self.uid = uid
        self.context = context
        self.number_lines = 0
        self.number_add = 0
        self.extra_message = ''
        self.localcontext.update({
            'time': time,
            'get_all_lines': self.get_all_lines,
            'get_extra_messages': self.get_extra_messages,
            'get_amount_in_word': self._get_amount_in_word,
        })

    def get_extra_messages(self):
        return self.extra_message

    def get_all_lines(self, voucher):
        debit_lines = voucher.line_dr_ids
        credit_lines = voucher.line_cr_ids
        return self.get_lines(debit_lines + credit_lines)

    def get_lines(self, voucher_lines):
        result = []
        self.number_lines = len(voucher_lines)
        for voucher_line in voucher_lines:
            # Don't show lines with amount=0; this means, an invoice/credit
            # note has not been linked to this check
            if voucher_line.amount != 0:
                # In general, the supplier invoice reference number is a much
                # better description for writing checks than our own reference
                # number, but if we don't have it, we might as well use our
                # internal number
                if voucher_line.supplier_invoice_number:
                    name = voucher_line.supplier_invoice_number
                else:
                    name = voucher_line.name
                # Display credits with a negative sign
                if voucher_line.type == 'cr':
                    sign = -1
                else:
                    sign = 1
                res = {
                    'date_due': (
                        voucher_line.date_due or voucher_line.date_original
                    ),
                    'name': name,
                    'amount_original': sign * voucher_line.amount_original,
                    'amount_unreconciled': (
                        sign * voucher_line.amount_unreconciled
                    ),
                    'amount': sign * voucher_line.amount,
                }
                result.append(res)

        res_len = len(result)
        if self.MAX_LINES is not None and res_len > self.MAX_LINES:
            self.extra_message = _(
                "More than %d lines in voucher, print Check Stubs"
                " to have all %d lines",
            ) % (self.MAX_LINES, res_len)
            result = result[:self.MAX_LINES]

        return result

    def _get_amount_in_word(self, i_id=None, currency_id=None,
                            amount=None):
        cr = self.cr
        uid = self.uid
        context = self.context
        ac_vouch_obj = self.pool.get("account.voucher")
        if context is None:
            context = {}
        if amount is None:
            amount = ac_vouch_obj.browse(cr, uid, i_id, context=context).amount

        # get lang
        supplier_lang = context.get('lang', config.get('lang', None))
        if i_id is not None:
            partner_id = ac_vouch_obj.browse(cr, uid, i_id,
                                             context=context).partner_id
            if partner_id:
                supplier_lang = partner_id.lang

        context = dict(context, lang=supplier_lang)
        if currency_id is None:
            if i_id is None:
                return None
            currency_id = self._get_current_currency(cr, uid, i_id,
                                                     context=context)

        currency = self.pool.get('res.currency').browse(cr, uid,
                                                        currency_id,
                                                        context=context)
        # get the amount_in_word
        return self._get_amount_line(amount, currency, supplier_lang)

    @staticmethod
    def _get_amount_line(amount, currency, lang):
        if not lang:
            lang = 'EN'

        # max char with font Courier 9.0
        max_char = 72
        # turning the amount into integer removes all the decimals.
        # We will use that to turn the base into word but we want to keep the
        # cents into numbers.
        base_amont = int(amount)
        # Extraction of cents
        cents = int(amount * 100) % 100
        currency_name = currency.print_on_check

        try:
            base_amount_in_word = num2words(base_amont, lang=lang[:2])
        except NotImplementedError:
            base_amount_in_word = num2words(base_amont)

        # it should not have any AND in the base_amount_in_word
        # so we just use the power of regex to sub them.
        base_amount_in_word = re.sub(r' and ', ' ', base_amount_in_word)

        if lang.startswith('fr'):
            first_line = u'{amount_in_word} {currency_name} {AND} {cents}/100 '
        else:
            first_line = u'{amount_in_word} {AND} {cents}/100 {currency_name} '

        first_line = first_line.format(
            AND=custom_translation("and", lang),
            currency_name=currency_name,
            amount_in_word=base_amount_in_word,
            cents=cents
        )

        first_line = first_line.title()

        nb_missing_char = max_char - len(first_line)
        if nb_missing_char:
            stars = '*' * nb_missing_char
        else:
            stars = ''
        amount_line_fmt = stars + first_line
        return amount_line_fmt

    def _get_current_currency(self, cr, uid, voucher_id, context=None):
        """
        Get the currency of the voucher.

        :param voucher_id: Id of the voucher what i want to obtain
                           current currency.
        :return: currency id of the voucher
        :rtype: int
        """
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id,
                                                          context)
        return voucher.currency_id.id or self._get_company_currency(cr, uid,
                                                                    voucher.id,
                                                                    context)

    def _get_company_currency(self, cr, uid, voucher_id, context=None):
        """
        Get the currency of the actual company.

        :param voucher_id: Id of the voucher what i want to obtain
                           company currency.
        :return: currency id of the company of the voucher
        :rtype: int
        """
        ac_vouch_obj = self.pool.get('account.voucher')
        journal = ac_vouch_obj.browse(cr, uid, voucher_id, context).journal_id
        return journal.company_id.currency_id.id


def custom_translation(s, lang):
    # Odoo uses the current stack frame, yes, the *stack frame* to determine
    # which language _() should translate a string in. If we want to translate
    # a string in another language, such as a supplier's language, we have to
    # resort to hacks such as this one. "context" is sought after in the
    # stackframe, so we have to set it.
    context = {'lang': lang}  # noqa: _() checks local frame for context
    return _(s)


class report_print_stub(report_print_check):
    MAX_LINES = None


report_sxw.report_sxw(
    'report.l10n.ca.account.print.check.top',
    'account.voucher',
    'addons/l10n_ca_account_check_writing/report/l10n_ca_check_print_top.rml',
    parser=report_print_check, header=False
)

report_sxw.report_sxw(
    'report.l10n.ca.account.print.check.middle',
    'account.voucher',
    'addons/l10n_ca_account_check_writing/report/'
    'l10n_ca_check_print_middle.rml',
    parser=report_print_check, header=False
)

report_sxw.report_sxw(
    'report.l10n.ca.account.print.check.stubs',
    'account.voucher',
    'addons/l10n_ca_account_check_writing/report/'
    'l10n_ca_check_print_stubs.rml',
    parser=report_print_stub, header=False
)

# report_sxw.report_sxw(
#     'report.l10n.ca.account.print.check.bottom',
#     'account.voucher',
# 'addons/l10n_ca_account_check_writing/report/l10n_ca_check_print_bottom.rml',
#     parser=report_print_check,header=False
# )
