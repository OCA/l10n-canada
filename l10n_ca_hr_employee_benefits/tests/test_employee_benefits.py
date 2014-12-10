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
        self.category_model = self.registry("hr.benefit.category")
        self.benefit_model = self.registry("hr.contract.benefit")
        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        # Create an employee
        self.employee_id = self.employee_model.create(
            self.cr, self.uid, {'name': 'Employee 1'}, context=self.context)

        # Create benefit categories
        self.category_1_id = self.category_model.create(
            cr, uid, {
                'name': 'Test 1',
                'description': 'Test',
                'code': 'TEST_1',
                'default_employee_amount': 50,
                'default_employer_amount': 100,
                'default_amount_type': 'each_pay',
            })

        self.category_2_id = self.category_model.create(
            cr, uid, {
                'name': 'Test 2',
                'description': 'Test',
                'code': 'TEST_2',
                'default_employee_amount': 1000,
                'default_employer_amount': 2000,
                'default_amount_type': 'annual',
            })

        # Create a contract
        self.contract_id = self.contract_model.create(
            self.cr, self.uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
            }, context=self.context
        )

        # Add employee benefits
        self.benefit_1_id = self.benefit_model.create(
            cr, uid, {
                'contract_id': self.contract_id,
                'category_id': self.category_1_id,
                'employee_amount': 60,
                'employer_amount': 120,
                'date_start': '2014-01-01',
                'date_end': '2014-12-31',
                'amount_type': 'each_pay',
            }, context=context
        )

        self.benefit_2_id = self.benefit_model.create(
            cr, uid, {
                'contract_id': self.contract_id,
                'category_id': self.category_1_id,
                'employee_amount': 0,
                'employer_amount': 0,
                'date_start': '2014-01-01',
                'date_end': '2014-12-31',
                'amount_type': 'each_pay',
            }, context=context
        )

        self.benefit_3_id = self.benefit_model.create(
            cr, uid, {
                'contract_id': self.contract_id,
                'category_id': self.category_2_id,
                'employee_amount': 90,
                'employer_amount': 130,
                'date_start': '2014-01-01',
                'date_end': '2014-12-31',
                'amount_type': 'each_pay',
            }, context=context
        )

        self.benefit_4_id = self.benefit_model.create(
            cr, uid, {
                'contract_id': self.contract_id,
                'category_id': self.category_1_id,
                'employee_amount': 650,
                'employer_amount': 1250,
                'date_start': '2014-01-01',
                'date_end': '2014-06-30',
                'amount_type': 'annual',
            }, context=context
        )

    def test_onchange_category_id_unchanged_amounts(self):
        """
        Test onchange_category_id method on hr.contract.benefit
        model when the record already has computed amounts
        """
        cr, uid, context = self.cr, self.uid, self.context

        res = self.benefit_model.onchange_category_id(
            cr, uid, [self.benefit_1_id],
            employee_amount=60,
            employer_amount=120,
            category_id=self.category_2_id,
            context=context
        )

        self.assertEqual(res['value']['employee_amount'], 60)
        self.assertEqual(res['value']['employer_amount'], 120)
        self.assertEqual(res['value']['amount_type'], 'annual')

    def test_onchange_category_id_changed_amounts(self):
        """
        Test onchange_category_id method on hr.contract.benefit
        model when the record already has no computed amounts
        """
        cr, uid, context = self.cr, self.uid, self.context

        res = self.benefit_model.onchange_category_id(
            cr, uid, [self.benefit_2_id],
            employee_amount=0,
            employer_amount=0,
            category_id=self.category_2_id,
            context=context
        )

        self.assertEqual(res['value']['employee_amount'], 1000)
        self.assertEqual(res['value']['employer_amount'], 2000)
        self.assertEqual(res['value']['amount_type'], 'annual')

    def test_sum_benefits_annual_employee(self):
        """
        Test sum_benefits method on hr.contract model with
            annual=True
            employer=False
        """
        cr, uid, context = self.cr, self.uid, self.context
        res = self.contract_model.sum_benefits(
            cr, uid, [self.contract_id], self.contract_id,
            date_from='2014-01-01', date_to='2014-01-31',
            exemption=False, benefit_code='TEST_1', employer=False,
            annual=True, pays_per_year=12,
            context=context
        )

        # Sums the annual employee amount over benefits 1, 2 and 4
        self.assertEqual(
            res, 60 * 12 + 650
        )

    def test_sum_benefits_annual_employer(self):
        """
        Test sum_benefits method on hr.contract model with
            annual=True
            employer=True
        """
        cr, uid, context = self.cr, self.uid, self.context
        res = self.contract_model.sum_benefits(
            cr, uid, [self.contract_id], self.contract_id,
            date_from='2014-01-01', date_to='2014-01-31',
            exemption=False, benefit_code='TEST_1', employer=True,
            annual=True, pays_per_year=12,
            context=context
        )

        # Sums the annual employer amount over benefits 1, 2 and 4
        self.assertEqual(
            res, 120 * 12 + 1250
        )

    def test_sum_benefits_each_pay_employee(self):
        """
        Test sum_benefits method on hr.contract model with
            annual=False
            employer=False
        """
        cr, uid, context = self.cr, self.uid, self.context
        res = self.contract_model.sum_benefits(
            cr, uid, [self.contract_id], self.contract_id,
            date_from='2014-01-01', date_to='2014-01-31',
            exemption=False, benefit_code='TEST_1', employer=False,
            annual=False, pays_per_year=12,
            context=context
        )

        # Sums the each_pay employee amount over benefits 1, 2 and 4
        self.assertEqual(
            res, 60 + 650.0 / 12
        )

    def test_sum_benefits_each_pay_employer(self):
        """
        Test sum_benefits method on hr.contract model with
            annual=False
            employer=True
        """
        cr, uid, context = self.cr, self.uid, self.context
        res = self.contract_model.sum_benefits(
            cr, uid, [self.contract_id], self.contract_id,
            date_from='2014-01-01', date_to='2014-01-31',
            exemption=False, benefit_code='TEST_1', employer=True,
            annual=False, pays_per_year=12,
            context=context
        )

        # Sums the each_pay employer amount over benefits 1, 2 and 4
        self.assertEqual(
            res, 120 + 1250.0 / 12
        )

    def test_sum_benefits_overlapping_dates(self):
        """
        Test sum_benefits method on hr.contract model with
            overlapping dates
        """
        cr, uid, context = self.cr, self.uid, self.context
        res = self.contract_model.sum_benefits(
            cr, uid, [self.contract_id], self.contract_id,
            date_from='2014-06-15', date_to='2014-07-15',
            exemption=False, benefit_code='TEST_1', employer=True,
            annual=False, pays_per_year=12,
            context=context
        )
        # Sums the each_pay employer amount over benefits 1, 2 and 4
        # benefit 4 ends on 2014-06-30 so it is valid 16 days over 31
        self.assertEqual(
            res, 120 + (1250.0 / 12) * 16.0 / (16 + 15)
        )
