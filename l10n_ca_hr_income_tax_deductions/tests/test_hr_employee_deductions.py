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


class test_sum_deductions(common.TransactionCase):
    def setUp(self):
        super(test_sum_deductions, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.deduction_category_model = self.registry('hr.deduction.category')
        self.user_model = self.registry("res.users")
        self.context = self.user_model.context_get(self.cr, self.uid)

        self.deductions = {
            deduction[1]: self.deduction_category_model.create(
                self.cr, self.uid, {
                    'name': 'Test',
                    'jurisdiction': deduction[0],
                    'description': 'Test',
                    'code': deduction[2],
                },
                context=self.context
            )
            for deduction in [
                ('both', 'D1', 'TEST_1'),
                ('provincial', 'D2', 'TEST_2'),
                ('provincial', 'D4', 'TEST_2'),
                ('federal', 'D3', 'TEST_3'),
            ]
        }

        self.employee_id = self.employee_model.create(
            self.cr, self.uid, {
                'name': 'Employee 1',
                'deduction_ids': [
                    (0, 0, {
                        'category_id': self.deductions['D1'],
                        'date_start': '2014-01-01',
                        'date_end': '2014-06-30',
                        'amount': 400,
                        'amount_type': 'annual',
                    }),
                    (0, 0, {
                        'category_id': self.deductions['D2'],
                        'date_start': '2014-01-01',
                        'date_end': '2014-12-31',
                        'amount': 500,
                        'amount_type': 'annual',
                    }),
                    (0, 0, {
                        'category_id': self.deductions['D4'],
                        'date_start': '2014-01-01',
                        'date_end': '2014-02-28',
                        'amount': 50,
                        'amount_type': 'each_pay',
                    }),
                    (0, 0, {
                        'category_id': self.deductions['D3'],
                        'date_start': '2014-05-15',
                        'date_end': '2014-07-31',
                        'amount': 600,
                        'amount_type': 'annual',
                    }),
                ],
            },
            context=self.context)

    def tearDown(self):
        self.employee_model.unlink(
            self.cr, self.uid, [self.employee_id], context=self.context)
        self.deduction_category_model.unlink(
            self.cr, self.uid, self.deductions.values(), context=self.context)
        super(test_sum_deductions, self).tearDown()

    def test_sum_deductions_normal_case(self):
        res = self.employee_model.sum_deductions(
            self.cr, self.uid, [self.employee_id],
            self.employee_id,
            '2014-02-01', '2014-02-28',
            'TEST_2',
            pays_per_year=12,
            estimated_income=False,
            context=self.context,
        )

        self.assertTrue(res == 500 + 12 * 50)

    def test_sum_deductions_overlapping_dates(self):
        """
        test sum_deductions
        with overlapping dates in an each_pay deduction
        """
        res = self.employee_model.sum_deductions(
            self.cr, self.uid, [self.employee_id],
            self.employee_id,
            '2014-02-01', '2014-03-31',
            'TEST_2',
            pays_per_year=6,
            estimated_income=False,
            context=self.context,
        )

        # One of the deductions is valid in february but not in march
        self.assertTrue(
            round(res, 2) == round(500 + 6 * 50 * 28.0 / (31 + 28), 2))

    def test_sum_deductions_overlapping_dates_annual(self):
        """
        test sum_deductions
        with overlapping dates in an annual deduction
        """
        res = self.employee_model.sum_deductions(
            self.cr, self.uid, [self.employee_id],
            self.employee_id,
            '2014-05-01', '2014-06-30',
            'TEST_3',
            pays_per_year=6,
            estimated_income=False,
            context=self.context,
        )

        # One of the deductions is valid from may 15th to june 30
        self.assertTrue(
            round(res, 2) == round(600 * (17.0 + 30) / (31 + 30), 2))

    def test_sum_deductions_estimated_income(self):
        """
        test sum_deductions
        with deduction excluded from estimated income computation
        """
        self.deduction_category_model.write(
            self.cr, self.uid,
            [self.deductions['D4']],
            {'estimated_income': False},
            context=self.context
        )
        res = self.employee_model.sum_deductions(
            self.cr, self.uid, [self.employee_id],
            self.employee_id,
            '2014-02-01', '2014-02-28',
            'TEST_2',
            pays_per_year=12,
            estimated_income=True,
            context=self.context,
        )

        self.assertTrue(res == 500)

    def test_sum_deductions_multiple_codes(self):
        """
        test sum_deductions
        with a list of deduction codes
        """
        res = self.employee_model.sum_deductions(
            self.cr, self.uid, [self.employee_id],
            self.employee_id,
            '2014-06-01', '2014-06-30',
            ['TEST_1', 'TEST_3'],
            pays_per_year=12,
            estimated_income=True,
            context=self.context,
        )

        self.assertTrue(res == 1000)
