# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2014 Odoo Canada. All Rights Reserved.
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
    'name': 'Canada - Payroll',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Canada Payroll Rules
====================
 * Adds Federal Salary Rules
 * Adds Federal Salary Structure
 * Adds 'Pays Per Year' field on the Contract Form
 * Adds Income Tax Deductions
 * Adds Employee Benefits (related to contracts)


Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Jonatan Cloutier <jonatan.cloutier@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
""",
    'author': 'Savoir-faire Linux',
    'website': 'https://www.savoirfairelinux.com',
    'depends': [
        'hr_payroll',
        'l10n_ca_toponyms',
    ],
    'data': [
        'security/ir.model.access.csv',
        'l10n_ca_hr_salary_rule_view.xml',
        'l10n_ca_hr_contract_view.xml',
        'l10n_ca_hr_employee_view.xml',
        'l10n_ca_hr_deduction_category_view.xml',
        'l10n_ca_hr_benefit_category_view.xml',
        'l10n_ca_hr_deduction_category_data.xml',
        'l10n_ca_hr_salary_rule_data.xml',
        'l10n_ca_hr_structure_data.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
