# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Affero GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the Affero GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Canada - Accounting profile",
    "version": "1.0",
    "author": "Savoir-faire Linux",
    "website": "http://www.savoirfairelinux.com",
    "category": "Localisation/Canada",
    "license": "AGPL-3",
    "description": """
Canada Accounting Profile
=========================

This module provides all the dependencies, data, translations, parameters and
configuration panel to have OpenERP as an accounting software ready for
canadians accountants and equivalent to local solutions like Acomba, Simply
Accounting, Avantage or Quickbooks.

Contributors
------------
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
""",
    "depends": [
        'l10n_ca_toponyms',
        'l10n_ca_account_check_writing',
        'currency_rate_update',
        'report_xls',
        'account_financial_report_webkit',
        'account_financial_report_webkit_xls',
        'account_journal_report_xls',
        'account_move_line_report_xls',
        'account_chart_report',
        'account_reversal',
        'partner_aging',
        'npg_account_make_deposit',
        'npg_bank_account_reconciliation',
        'account_statement_base_import',
        'account_invoice_merge',
        'account_voucher_supplier_invoice_number',
    ],
    "license": "AGPL-3",
    "data": [],
    "installable": True,
}
