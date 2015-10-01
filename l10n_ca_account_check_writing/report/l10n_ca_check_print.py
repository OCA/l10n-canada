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

import time
from openerp.report import report_sxw


class ReportPrintCheck(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportPrintCheck, self).__init__(cr, uid, name, context)
        self.number_lines = 0
        self.number_add = 0
        self.localcontext.update({
            'time': time,
            'get_all_lines': self.get_all_lines,
            'ltrim': self.ltrim,
            'spad': self.pad_stars,
            'amount_in_word': self.get_amount_in_word,
        })

    def ltrim(self, s, maxlen):
        if len(s) > maxlen:
            return s[-maxlen:]

    def pad_stars(self, s, maxlen):
        """ Pad string with stars """
        return u'{0:*>{1}}'.format(s, maxlen)

    def get_amount_in_word(self, voucher):
        currency = voucher._get_current_currency(voucher.id)
        return voucher._amount_in_words(currency)[0]

    def get_all_lines(self, voucher):
        debit_lines = voucher.line_dr_ids
        credit_lines = voucher.line_cr_ids
        return self.get_lines(debit_lines + credit_lines)

    def get_lines(self, voucher_lines):
        result = []
        self.number_lines = len(voucher_lines)
        for i in range(0, min(10, self.number_lines)):
            if i < self.number_lines:
                voucher_line = voucher_lines[i]
                # Don't show lines with amount=0; this means, an invoice/credit
                # note has not been linked to this check
                if voucher_line.amount != 0:
                    # In general, the supplier invoice reference number is a
                    # much better description for writing checks than our own
                    # reference number, but if we don't have it, we might as
                    # well use our internal number
                    if voucher_line.supplier_invoice_number:
                        name = voucher_line.supplier_invoice_number
                    else:
                        name = voucher_line.name
                    # Display credits with a minus
                    if voucher_line.type == "cr":
                        sign = -1
                    else:
                        sign = 1
                    res = {
                        'date_due': (
                            voucher_line.date_due or voucher_line.date_original
                        ),
                        'name': name,
                        'amount_original': (
                            voucher_line.amount_original and
                            voucher_line.amount_original * sign or False),
                        'amount_unreconciled': (
                            voucher_line.amount_unreconciled and
                            voucher_line.amount_unreconciled * sign or False),
                        'amount': (voucher_line.amount and
                                   voucher_line.amount * sign or False),
                    }
                    result.append(res)
            else:
                res = {
                    'date_due': False,
                    'name': False,
                    'amount_original': False,
                    'amount_unreconciled': False,
                    'amount': False,
                }
                result.append(res)

        return result


report_sxw.report_sxw(
    'report.l10n.ca.account.print.check.top',
    'account.voucher',
    'addons/l10n_ca_account_check_writing/report/l10n_ca_check_print_top.rml',
    parser=ReportPrintCheck, header=False
)

report_sxw.report_sxw(
    'report.l10n.ca.account.print.check.middle',
    'account.voucher',
    'addons/l10n_ca_account_check_writing/'
    'report/l10n_ca_check_print_middle.rml',
    parser=ReportPrintCheck, header=False
)
