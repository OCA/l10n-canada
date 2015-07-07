# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 - 2014 Savoir-faire Linux. All Rights Reserved.
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
    'name': 'Canada - Quebec - Payroll Accounting',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'description': """
Quebec Payroll Accounting
=========================
Add the accounting of the Releve 1 summary.

Map the salary rules of the Quebec payroll structure to accounts of
the Canada account chart.

Contributors
------------
* Jonatan Cloutier <jonatan.cloutier@savoirfairelinux.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* David Dufresne <david.dufresne@savoirfairelinux.com>
""",
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'http:/www.savoirfairelinux.com',
    'depends': [
        'l10n_ca_qc_hr_payroll',
        'l10n_ca_hr_payroll_account',
    ],
    'data': [
        'views/hr_releve_1_summary.xml',
        'views/res_company.xml',
        'data/hr_salary_rule.xml',
        'data/res_company.xml',
    ],
    'test': [],
    'installable': True,
}
