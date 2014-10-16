# -*- encoding: utf-8 -*-
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

{
    "name": "Taxes included in expense",
    "version": "1.2",
    "author": "Savoir-faire Linux",
    "category": "Account",
    "website": "http://wwww.savoirfairelinux.com",
    "license": "AGPL-3",
    "description": """
Taxes included in expense
=========================
This module adds a checkbox to tax to include tax in expense invoices.
It is useful if your taxes are not included in the price, but you
want to ease the life of your employees by allowing them to enter
their expenses with the taxes included.

Contributors
------------
* Jonatan Cloutier <jonatan.cloutier@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
""",
    "depends": ["account"],
    "data": [
        "account_tax_view.xml",
    ],
    "installable": True
}
