#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Savoir-faire Linux. All Rights Reserved.
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
    'name': 'Canada - Quebec - Payroll Accounting',
    'category': 'Localization',
    'version': '0.2',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Quebec Payroll Accounting 
=========================

This module:
 * creates financial accounts for payroll
 * updates salary rules with accounting information

    !!! Warning !!!

Make sure to install AND CONFIGURE the canadian chart of accounts module (l10n_ca)
before installing this module. Chart template needs to be selected to populate
the account.account table and allow you to link salary rules with the financial 
account.
    """,
    'author':'Savoir-faire Linux',
    'website':'http:/www.savoirfairelinux.com',
    'depends': [
        'l10n_ca_qc_hr_payroll',
        'l10n_ca_hr_payroll_account',
    ],
    'data': [
        'l10n_ca_qc_hr_payroll_account_data.xml',
    ],
    'test': ['test/l10n_ca_qc_hr_payroll_account.yml'],
    'demo': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
