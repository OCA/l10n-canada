# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
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
    "name": "Supplier on expense line - Required",
    "version": "1.2",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "category": "Human Resources",
    "license": "AGPL-3",
    "description": """
Supplier on expense line - Required
===================================
This module makes supplier field on the demo expense lines required.
It allows the main module 'Supplier on expense line' to install correctly,
without any warnings when demo data is activated.

Contributors
------------
* Agathe Mollé <agathe.molle@savoirfairelinux.com>
""",
    "depends": ['hr_expense_line_supplier'],
    "installable": True,
    "auto_install": True,
}
