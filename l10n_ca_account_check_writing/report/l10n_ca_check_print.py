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

import time
from openerp.report import report_sxw
from openerp.tools.translate import _


class report_print_check(report_sxw.rml_parse):
    MAX_LINES = 10

    def __init__(self, cr, uid, name, context):
        super(report_print_check, self).__init__(cr, uid, name, context)
        self.number_lines = 0
        self.number_add = 0
        self.extra_message = ''
        self.localcontext.update({
            'time': time,
            'get_all_lines': self.get_all_lines,
            'get_extra_messages': self.get_extra_messages,
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
            # Don't show lines with amount=0; this means, an invoice/credit note has not been linked to this check
            if voucher_line.amount != 0:
                # In general, the supplier invoice reference number is a much better description
                # for writing checks than our own reference number, but if we don't have it, we
                # might as well use our internal number
                if voucher_line.supplier_invoice_number:
                    name = voucher_line.supplier_invoice_number
                else:
                    name = voucher_line.name
                res = {
                    'date_due': voucher_line.date_due,
                    'name': name,
                    'amount_original': voucher_line.amount_original and voucher_line.amount_original or False,
                    'amount_unreconciled': voucher_line.amount_unreconciled and voucher_line.amount_unreconciled or False,
                    'amount': voucher_line.amount and voucher_line.amount or False,
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
    'addons/l10n_ca_account_check_writing/report/l10n_ca_check_print_middle.rml',
    parser=report_print_check, header=False
)

report_sxw.report_sxw(
    'report.l10n.ca.account.print.check.stubs',
    'account.voucher',
    'addons/l10n_ca_account_check_writing/report/l10n_ca_check_print_stubs.rml',
    parser=report_print_stub, header=False
)

# report_sxw.report_sxw(
#     'report.l10n.ca.account.print.check.bottom',
#     'account.voucher',
#     'addons/l10n_ca_account_check_writing/report/l10n_ca_check_print_bottom.rml',
#     parser=report_print_check,header=False
# )
