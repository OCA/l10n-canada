# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2014 Odoo Canada. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Canada - Payroll Accounting',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Canada Payroll Accounting
=========================

This module:
 * creates salary journal
 * creates financial accounts for payroll
 * updates salary rules with accounting information

Contributors
------------
* Jonatan Cloutier <jonatan.cloutier@savoirfairelinux.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
""",
    'author': "Odoo Canada,Odoo Community Association (OCA)",
    'website': 'https://community.odoo.com/project/42',
    'depends': [
        'l10n_ca',
        'l10n_ca_hr_payroll',
        'hr_payroll_account',
    ],
    'data': [
        'l10n_ca_hr_payroll_account_data.xml',
    ],
    'test': [],
    'demo': [],
    'installable': False,
}
