# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2015 Savoir-faire Linux. All Rights Reserved.
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
    'description': """
Canada Payroll
==============
* Create the payslips of your employees
* Produce the T4 for the Canadian Revenu Agency
* Produce the T4 Summary and the xml for electronic transmission
* Manage employee benefits
* Track the leave accruals of your employees

Contributors
------------
* Amura Consulting
* Jonatan Cloutier <jonatan.cloutier@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
* David Dufresne <david.dufresne@savoirfairelinux.com>
""",
    'author': "Odoo Canada,Odoo Community Association (OCA)",
    'website': 'https://community.odoo.com/project/42',
    'depends': [
        'document',
        'hr_payroll',
        'l10n_ca_toponyms',
        'l10n_ca_hr_income_tax_deductions',
        'hr_employee_exemption',
        'hr_employee_benefit',
        'hr_employee_benefit_exemption',
        'hr_employee_benefit_on_job',
        'hr_employee_benefit_percent',
        'hr_contract_hourly_rate',
        'hr_worked_days_hourly_rate',
        'hr_worked_days_activity',
        'hr_salary_rule_variable',
        'hr_employee_firstname',
        'hr_payslip_ytd_amount',
        'hr_leave_accruals',
        'hr_public_holidays',
        'hr_payroll_analysis',
        'hr_period',
    ],
    'data': [
        'views/menu.xml',
        'views/hr_holidays_entitlement.xml',
        'views/hr_activity.xml',
        'views/hr_salary_rule.xml',
        'views/res_company.xml',
        'views/hr_payslip.xml',
        'views/hr_payslip_run.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'views/hr_cra_t4.xml',
        'views/hr_cra_t4_box.xml',
        'views/hr_cra_t4_summary.xml',
        'views/hr_employee_benefit_category.xml',
        'data/hr_holidays_entitlement.xml',
        'data/hr_deduction_jurisdiction.xml',
        'data/hr_income_tax_exemption.xml',
        'data/hr_employee_benefit_category.xml',
        'data/hr_holidays_status.xml',
        'data/salary_rules/base.xml',
        'data/salary_rules/ben.xml',
        'data/salary_rules/ei.xml',
        'data/salary_rules/cpp.xml',
        'data/salary_rules/fit.xml',
        'data/salary_rules/pension_plans.xml',
        'data/salary_rules/vacation.xml',
        'data/salary_rules/public_holidays.xml',
        'data/salary_rules/sick_leaves.xml',
        'data/salary_rules/compensatory.xml',
        'data/hr_deduction_category.xml',
        'data/hr_payslip_input_category.xml',
        'data/hr_cra_t4_box.xml',
        'data/hr_cra_t4_other_amount.xml',
        'data/hr_cra_t4_summary_box.xml',
        'data/hr_structure.xml',
        'data/hr_leave_accrual.xml',
        'data/public_holidays/2015.xml',
        'data/salary_rule_variables/2014.xml',
        'data/salary_rule_variables/2015.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'report/hr_payroll_report.xml',
    ],
    'external_dependencies': {
        'python': ['iso3166'],
    },
    'test': [],
    'demo': ['demo/demo_data.xml'],
    'installable': True,
}
