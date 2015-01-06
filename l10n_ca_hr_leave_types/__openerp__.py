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
    'name': 'Canada - Leave Types',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Canada - Leave Types
====================
 * Adds leave accruals used for Canada Payslips
 * Adds function hr_leave_accrual.sum_lines_by_category that allows to querry
    over a leave accrual for payslip computation

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': 'Savoir-faire Linux',
    'website': 'https://www.savoirfairelinux.com',
    'depends': [
        'hr_leave_accruals',
        'hr_public_holidays',
        'l10n_ca_hr_payroll',
    ],
    'data': [
        'data/hr_salary_rule_data_vacation.xml',
        'data/hr_salary_rule_data_legal_leaves.xml',
        'data/hr_salary_rule_data_sick_leaves.xml',
        'data/hr_salary_rule_data_compensatory.xml',
        'data/hr_leave_accrual_template_data.xml',
        'view/res_company_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
