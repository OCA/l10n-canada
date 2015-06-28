# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
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

from openerp.tests import common


class TestDeductions(common.TransactionCase):
    def setUp(self):
        super(TestDeductions, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.deduction_model = self.registry('hr.deduction.category')
        self.jurisdiction_model = self.registry('hr.deduction.jurisdiction')
        self.payslip_model = self.registry("hr.payslip")
        self.contract_model = self.registry("hr.contract")
        self.user_model = self.registry("res.users")
        self.rule_model = self.registry('hr.salary.rule')
        self.rule_category_model = self.registry("hr.salary.rule.category")
        self.structure_model = self.registry("hr.payroll.structure")

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.jurisdiction_id = self.jurisdiction_model.create(cr, uid, {
            'name': 'Federal',
        }, context=context)

        self.category_id = self.rule_category_model.search(
            cr, uid, [], context=context)[0]

        self.rule_id = self.rule_model.create(
            cr, uid, {
                'name': 'Test 1',
                'sequence': 1,
                'code': 'RULE_1',
                'category_id': self.category_id,
                'amount_select': 'code',
                'amount_python_compute': """
result = rule.sum_deductions(payslip)
"""
            }, context=context)

        self.rule_2_id = self.rule_model.create(
            cr, uid, {
                'name': 'Test 2',
                'sequence': 1,
                'code': 'RULE_2',
                'category_id': self.category_id,
                'amount_select': 'code',
                'amount_python_compute': """
result = rule.sum_deductions(payslip)
"""
            }, context=context)

        self.structure_id = self.structure_model.create(cr, uid, {
            'name': 'TEST',
            'parent_id': False,
            'code': 'TEST',
            'rule_ids': [(6, 0, [self.rule_id, self.rule_2_id])]
        }, context=context)

        self.deductions = [
            self.deduction_model.create(
                self.cr, self.uid, {
                    'name': 'Test',
                    'jurisdiction_id': self.jurisdiction_id,
                    'description': 'Test',
                    'salary_rule_ids': [(6, 0, deduction[0])],
                    'amount_type': deduction[1],
                },
                context=self.context
            )
            for deduction in [
                ([self.rule_id], 'annual'),
                ([self.rule_id, self.rule_2_id], 'each_pay'),
            ]
        ]

        self.employee_id = self.employee_model.create(
            self.cr, self.uid, {
                'name': 'Employee 1',
                'deduction_ids': [
                    (0, 0, {
                        'category_id': self.deductions[0],
                        'date_start': '2015-01-01',
                        'date_end': '2015-04-16',
                        'amount': 400,
                    }),
                    (0, 0, {
                        'category_id': self.deductions[0],
                        'date_start': '2015-05-15',
                        'date_end': '2015-07-31',
                        'amount': 600,
                    }),
                    (0, 0, {
                        'category_id': self.deductions[1],
                        'date_start': '2015-01-01',
                        'date_end': '2015-02-28',
                        'amount': 50,
                    }),
                    (0, 0, {
                        'category_id': self.deductions[1],
                        'date_start': '2015-01-01',
                        'date_end': '2015-12-31',
                        'amount': 60,
                    }),
                    (0, 0, {
                        'category_id': self.deductions[1],
                        'date_start': '2015-05-01',
                        'date_end': '2015-06-30',
                        'amount': 30,
                    }),
                ],
            },
            context=self.context)

        self.contract_id = self.contract_model.create(
            cr, uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 52000,
                'schedule_pay': 'monthly',
                'struct_id': self.structure_id,
            }, context=context)

        self.payslip_id = self.payslip_model.create(cr, uid, {
            'employee_id': self.employee_id,
            'contract_id': self.contract_id,
            'pays_per_year': 12,
            'date_from': '2015-02-01',
            'date_to': '2015-02-28',
            'date_payment': '2015-02-28',
            'struct_id': self.structure_id,
        }, context=context)

        self.payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

    def compute_payslip(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.compute_sheet(
            cr, uid, [self.payslip_id], context=context)

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        return {
            line.code: line.total
            for line in payslip.details_by_salary_rule_category
        }

    def test_sum_deductions(self):
        payslip = self.compute_payslip()

        self.assertEqual(round(payslip['RULE_1']), round(400 / 12 + 50 + 60))
        self.assertEqual(round(payslip['RULE_2']), 50 + 60)

    def test_sum_deductions_2(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.payslip_model.write(cr, uid, [self.payslip_id], {
            'date_from': '2015-04-16',
            'date_to': '2015-05-15',
            'date_payment': '2015-05-15',
        }, context=context)

        payslip = self.compute_payslip()

        self.assertEqual(round(payslip['RULE_1']), 600 / 12 + 30 + 60)
        self.assertEqual(round(payslip['RULE_2']), 30 + 60)
