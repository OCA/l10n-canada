# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
    'name': 'Canada - Fiscal Slips',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'description': """
Canada - Fiscal Slips
=====================
 * Add fiscal slip base for Canada. The model contains all fields required
 in every fiscal slip, such as the T4.
 * Add a sub-menu that contains fiscal slips views.

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': 'Savoir-faire Linux',
    'website': 'https://www.savoirfairelinux.com',
    'depends': [
        'hr_payroll',
        'res_partner_attributes_add_SIN',
        'res_partner_attributes_add_BN',
        'hr_employee_firstname',
    ],
    'data': [
        'hr_canada_fiscal_slip_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
