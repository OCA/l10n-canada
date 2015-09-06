# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Odoo Canada. All Rights Reserved.
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
    'name': 'Canada - Income Tax Deductions',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Canada Income Tax Deductions
============================
 * Adds Income Tax Deductions

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com',
    'depends': [
        'hr_payroll',
        'hr_salary_rule_reference',
        'hr_period',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_deduction_category.xml',
        'views/hr_deduction_jurisdiction.xml',
        'views/hr_employee.xml',
        'views/hr_payslip.xml',
        'views/hr_salary_rule.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
