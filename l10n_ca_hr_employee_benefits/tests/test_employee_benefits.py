# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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


class test_contract_hourly_rate(common.TransactionCase):
    def setUp(self):
        super(test_contract_hourly_rate, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.contract_model = self.registry("hr.contract")
        self.category_model = self.registry("hr.employee.benefit.category")
        self.benefit_model = self.registry("hr.employee.benefit")
        self.rate_model = self.registry("hr.employee.benefit.rate")
        self.rate_line_model = self.registry("hr.employee.benefit.rate.line")
        self.payslip_model = self.registry("hr.payslip")
        self.job_model = self.registry("hr.job")
        self.salary_rule_model = self.registry("hr.salary.rule")
        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        self.employee_id = self.employee_model.create(
            cr, uid, {'name': 'Employee 1'}, context=context)

        self.job_id = self.job_model.create(
            cr, uid, {'name': 'Job 1'}, context=context)

        self.job_activity_id = self.job_model.browse(
            cr, uid, self.job_id, context=context).activity_ids[0].id

        self.contract_ids = [
            self.contract_model.create(self.cr, self.uid, {
                'employee_id': self.employee_id,
                'name': contract[0],
                'wage': 50000,
                'job_id': self.job_id,
            }, context=self.context)
            for contract in [
                ('Contract 1'),
                ('Contract 2'),
            ]
        ]

        self.rule_ids = self.salary_rule_model.search(
            cr, uid, [], context=context)

        self.category_ids = [
            self.category_model.create(cr, uid, {
                'name': category[0],
                'description': 'Test',
                'code': category[1],
                'fit_exempt': category[2],
                'salary_rule_ids': [(6, 0, category[3])],
            }, context=context)
            for category in [
                ('Category 1', 'BEN_1', False, [self.rule_ids[0]]),
                ('Category 2', 'BEN_2', False, []),
                ('Category 3', 'BEN_3', True, [self.rule_ids[1]]),
                ('Category 4', 'BEN_4', True,
                    [self.rule_ids[0], self.rule_ids[1]]),
            ]
        ]

        self.rate_ids = [
            self.rate_model.create(cr, uid, {
                'name': 'Test',
                'category_id': rate[0],
                'amount_type': rate[1],
            }, context=context)
            for rate in [
                (self.category_ids[0], 'each_pay'),
                (self.category_ids[1], 'annual'),
                (self.category_ids[2], 'percent_gross'),
                (self.category_ids[3], 'per_hour'),
            ]
        ]

        self.rate_line_ids = [
            self.rate_line_model.create(cr, uid, {
                'parent_id': line[0],
                'employee_amount': line[1],
                'employer_amount': line[2],
                'date_start': line[3],
                'date_end': line[4],
            }, context=context)
            for line in [
                (self.rate_ids[0], 20, 40, '2014-01-01', '2014-06-30'),
                (self.rate_ids[0], 25, 50, '2014-07-01', False),

                (self.rate_ids[1], 600, 700, '2014-01-01', '2014-06-30'),
                (self.rate_ids[1], 800, 900, '2014-07-01', False),

                (self.rate_ids[2], 2.0, 3.5, '2014-01-01', '2014-06-30'),
                (self.rate_ids[2], 2.5, 4.5, '2014-07-01', False),

                (self.rate_ids[3], 5, 10, '2014-01-01', '2014-06-30'),
                (self.rate_ids[3], 7, 13, '2014-07-01', False),
            ]
        ]

        self.benefit_ids = [
            self.benefit_model.create(cr, uid, {
                'category_id': benefit[0],
                'rate_id': benefit[1],
                'date_start': benefit[2],
                'date_end': benefit[3],
                'contract_id': benefit[4],
                'job_id': benefit[5]
            }, context=context)
            for benefit in [
                (self.category_ids[0], self.rate_ids[0],
                    '2014-01-01', '2014-12-31', self.contract_ids[0], False),
                (self.category_ids[1], self.rate_ids[1],
                    '2014-01-01', '2014-12-31', self.contract_ids[0], False),
                (self.category_ids[2], self.rate_ids[2],
                    '2014-01-01', '2014-12-31', self.contract_ids[0], False),
                (self.category_ids[3], self.rate_ids[3],
                    '2014-01-01', '2014-12-31', False, self.job_id),
            ]
        ]

        self.payslip_id = self.payslip_model.create(cr, uid, {
            'employee_id': self.employee_id,
            'contract_id': self.contract_ids[0],
            'gross_salary': 2500,
            'pays_per_year': 12,
            'date_from': '2014-01-01',
            'date_to': '2014-01-31',
            'worked_days_line_ids': [(0, 0, {
                'activity_id': line[0],
                'number_of_hours': line[1],
                'hourly_rate': 25,
                'code': 'ddd',
                'name': 'ddd',
                'date_from': line[2],
                'date_to': line[3],
            }) for line in [
                (self.job_activity_id, 25, '2014-01-01', '2014-01-15'),
                (self.job_activity_id, 75, '2014-01-16', '2014-01-31'),
            ]]
        }, context=context)

    def get_payslip(self):
        cr, uid, context = self.cr, self.uid, self.context

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        payslip.compute_benefits(payslip)

        return payslip

    def test_sum_benefits_annual_employee(self):
        """
        Test sum_benefits method with annual=True and employer=False
        """
        payslip = self.get_payslip()
        res = payslip.sum_benefits(payslip, employer=False, annual=True)

        self.assertEqual(
            round(res),
            round((20 + 600.0 / 12 + 2.0 * 2500 / 100 + 5 * 100) * 12))

    def test_sum_benefits_annual_employer(self):
        """
        Test sum_benefits method with annual=True and employer=True
        """
        payslip = self.get_payslip()
        res = payslip.sum_benefits(payslip, employer=True, annual=True)

        self.assertEqual(
            round(res),
            round((40 + 700.0 / 12 + 3.5 * 2500 / 100 + 10 * 100) * 12))

    def test_sum_benefits_each_pay_employee(self):
        """
        Test sum_benefits method with annual=False and employer=False
        """
        payslip = self.get_payslip()
        res = payslip.sum_benefits(payslip, employer=False, annual=False)

        self.assertEqual(
            round(res),
            round(20 + 600.0 / 12 + 2.0 * 2500 / 100 + 5 * 100))

    def test_sum_benefits_each_pay_employer(self):
        """
        Test sum_benefits method with annual=False and employer=True
        """
        payslip = self.get_payslip()
        res = payslip.sum_benefits(payslip, employer=True, annual=False)

        self.assertEqual(
            round(res),
            round(40 + 700.0 / 12 + 3.5 * 2500 / 100 + 10 * 100))

    def test_sum_benefits_overlapping_dates(self):
        """
        Test sum_benefits method with overlapping dates
        """
        cr, uid, context = self.cr, self.uid, self.context

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        payslip.write({'date_from': '2014-06-16', 'date_to': '2014-07-15'})

        payslip.worked_days_line_ids[0].write({
            'date_from': '2014-06-16', 'date_to': '2014-07-05',
            'number_of_hours': 75
        })

        payslip.worked_days_line_ids[0].write({
            'date_from': '2014-07-06', 'date_to': '2014-07-15',
            'number_of_hours': 25
        })

        payslip.compute_benefits(payslip)

        res = payslip.sum_benefits(payslip, employer=False, annual=False)

        self.assertEqual(
            round(res),
            round(
                (20. + 25.) / 2 +
                (600. + 800.) / (2 * 12) +
                (2.0 + 2.5) * 2500 / (2 * 100) +
                5. * 75 * 15 / 20 +
                5. * 75 * 5 / 20 +
                7. * 25
            ))

    def test_sum_benefits_list_of_codes(self):
        """
        Test sum_benefits method with a list of codes given as parameter
        """
        payslip = self.get_payslip()
        res = payslip.sum_benefits(
            payslip, employer=False, annual=False,
            benefit_codes=['BEN_1', 'BEN_3'])

        self.assertEqual(
            round(res), round(20 + 2.0 * 2500 / 100))

        res = payslip.sum_benefits(
            payslip, employer=False, annual=False,
            benefit_codes=['BEN_2', 'BEN_4'])

        self.assertEqual(
            round(res), round(600.0 / 12 + 5 * 100))

    def test_sum_benefits_single_benefit_code(self):
        """
        Test sum_benefits method with a single benefit code given
        as parameter
        """
        payslip = self.get_payslip()
        res = payslip.sum_benefits(
            payslip, employer=False, annual=False,
            benefit_codes='BEN_3')

        self.assertEqual(
            round(res), round(2.0 * 2500 / 100))

    def test_sum_benefits_exemption(self):
        """
        Test sum_benefits method with an exemption
        """
        payslip = self.get_payslip()
        res = payslip.sum_benefits(
            payslip, employer=False, annual=False,
            exemption='fit_exempt')

        # Benefit categories 1 and 2 are not exempted
        self.assertEqual(
            round(res), round(20 + 600.0 / 12))

    def test_sum_benefits_added_manually(self):
        """
        Test sum_benefits method with a benefit added manually
        """
        cr, uid, context = self.cr, self.uid, self.context

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        payslip.write({'benefit_line_ids': [(0, 0, {
            'category_id': self.category_ids[0],
            'employee_amount': 1000,
            'employer_amount': 1500,
        })]})

        payslip = self.get_payslip()
        res = payslip.sum_benefits(
            payslip, employer=False, annual=False,
            category_ids=[self.category_ids[0]])

        self.assertEqual(res, 20 + 1000)

        res = payslip.sum_benefits(
            payslip, employer=True, annual=False,
            category_ids=[self.category_ids[0]])

        self.assertEqual(res, 40 + 1500)

        # Test generate a second time
        payslip = self.get_payslip()
        res = payslip.sum_benefits(
            payslip, employer=False, annual=False,
            category_ids=[self.category_ids[0]])

        self.assertEqual(res, 20 + 1000)

    def test_sum_benefits_salary_rule_id(self):
        """
        Test sum_benefits with salary rule id as parameter
        """
        payslip = self.get_payslip()
        res = payslip.sum_benefits(
            payslip, employer=False, annual=False,
            rule_id=self.rule_ids[1])

        # Benefit categories 3 and 4 are related to salary rule #1
        self.assertEqual(
            round(res), round(2.0 * 2500 / 100 + 5 * 100))
