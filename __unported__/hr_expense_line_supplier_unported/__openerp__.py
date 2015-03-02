# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Supplier on expense line',
    'version': '1.0',
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'http://www.savoirfairelinux.com',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'description': """
Supplier on expense line
========================
This module adds a supplier field on the expense line and set the taxes of
the employee invoice based on the fiscal position of the supplier.

The tax calculation doesn't work in v7 and v8 for an expense. The expense now
create a voucher that only has one tax rate by voucher and we can't
safely select one tax rate per expense form. To fix this situation the
expense form should suport the taxes like a supplier invoice form and a
the end of the workflow produce a voucher and the journal entries like
what is done when a supplier invoice is open.

Contributors
------------
* Jonatan Cloutier <jonatan.cloutier@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
""",
    'depends': ['hr_expense'],
    'data': [
        'hr_expense.xml',
    ],
    'installable': False,
}
