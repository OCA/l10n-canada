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
{
    'name': 'Canada - Check Writing',
    'version': '8.0.1.0.0',
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'http://www.savoirfairelinux.com',
    'category': 'Generic Modules/Accounting',
    "license": "AGPL-3",
    'description': """
Print checks in Canadian's format'
==================================

This module provides reports to print check using the canadian format from:
http://www.cdnpay.ca/imis15/pdf/pdfs_rules/standard_006_fr.pdf

Note that the amount in letter is generated when you enter/change the amount,
not when you print. You will need to modify it if you change the language of
the supplier.

To use this module, you will need to install num2words Python library:
https://pypi.python.org/pypi/num2words

Contributors
------------
* David Cormier (david.cormier@savoirfairelinux.com)
* Joao Alfredo Gama Batista (joao.gama@savoirfairelinux.com)
* Marc Cassuto (marc.cassuto@savoirfairelinux.com)
* Mathieu Benoit (mathieu.benoit@savoirfairelinux.com)
* Maxime Chambreuil (maxime.chambreuil@savoirfairelinux.com)
* Vincent Vinet (vincent.vinet@savoirfairelinux.com)
* Virgil Dupras (virgil.dupras@savoirfairelinux.com)
* Sandy Carter (sandy.carter@savoirfairelinux.com)
* Primaco (info@primaco.ca)
""",
    'depends': [
        'l10n_ca_toponyms',
        'account_check_writing',
        'res_currency_print_on_check',
        'account_voucher_supplier_invoice_number',
    ],
    'data': [
        'l10n_ca_account_check_writing_report.xml',
    ],
    'demo': [],
    'test': [
        'test/amount_in_word.yml',
    ],
    'external_dependencies': {
        'python': ['num2words'],
    },
    'installable': True,
}
