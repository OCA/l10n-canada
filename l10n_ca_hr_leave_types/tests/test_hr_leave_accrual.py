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


class test_canada_leave_accrual(common.TransactionCase):
    """
    Test the leave accruals of an employee in Canada
    """
    def setUp(self):
        super(test_canada_leave_accrual, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.accrual_model = self.registry("hr.leave.accrual")
        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.employee_id = self.employee_model.create(
            self.cr, self.uid, {'name': 'Employee 1'}, context=self.context)

        self.accrual_id = self.accrual_model.search(
            self.cr, self.uid, [('employee_id', '=', self.employee_id)],
            context=self.context)[0]

        accrual = self.accrual_model.browse(
            cr, uid, self.accrual_id, context=context)
        self.accrual_code = accrual.code

        # Create lines to insert into leave accruals
        accrual_lines = [
            (False, '2014-01-01', -70),
            (True, '2014-12-31', 90),
            (True, '2014-12-31', -100),
            (False, '2014-01-01', 110),
            (False, '2014-12-31', 130),
            (False, '2013-01-01', -15),
            (False, '2012-01-01', -35),
            (False, '2013-01-01', 270),
            (False, '2012-01-01', 290),
            (False, '2015-01-01', -60),
            (False, '2015-01-01', 300)
        ]

        line_ids = [
            (0, 0, {
                'source': 'manual',
                'is_refund': accrual_line[0],
                'date': accrual_line[1],
                'description': 'Test',
                # Change the amount to distinguish each leave type
                'amount': accrual_line[2]
            }) for accrual_line in accrual_lines
        ]
        accrual.write({'line_ids': line_ids})

    def tearDown(self):
        self.employee_model.unlink(
            self.cr, self.uid, [self.employee_id], context=self.context)
        super(test_canada_leave_accrual, self).tearDown()

    def test_employee_default_leave_accruals(self):
        """
        Test if employee created has the 3 required leave accruals
        Vacations, Sick leaves and Compensatory
        """
        employee = self.employee_model.browse(
            self.cr, self.uid, self.employee_id, context=self.context)

        leave_accruals = [
            accrual.code for accrual in employee.leave_accrual_ids
        ]
        for code in ['VAC', 'SL', 'COMP']:
            self.assertIn(code, leave_accruals)

    def test_sum_leave_accruals_returns_dict(self):
        """
        Test that employee method sum_leave_accruals returns a dict
        """
        res = self.employee_model.sum_leave_accruals(
            self.cr, self.uid, [self.employee_id],
            self.employee_id, 'VAC', '2014-01-01', context=self.context)

        self.assertTrue(isinstance(res, dict))

    def test_sum_leave_accruals_return_current_added_ytd(self):
        """
        Test that employee method sum_leave_accruals returns a dict
        containing the right amount for current_added_ytd
        """
        res = self.employee_model.sum_leave_accruals(
            self.cr, self.uid, [self.employee_id], self.employee_id,
            self.accrual_code, '2014-01-01', context=self.context)

        self.assertEqual(
            # Current year added: 110 + 130 - 100 = 240
            res['current_added_ytd'], 140
        )

    def test_sum_leave_accruals_return_current_taken_ytd(self):
        """
        Test that employee method sum_leave_accruals returns a dict
        containing the right amount for current_taken_ytd
        """
        res = self.employee_model.sum_leave_accruals(
            self.cr, self.uid, [self.employee_id], self.employee_id,
            self.accrual_code, '2014-01-01', context=self.context)

        self.assertEqual(
            # Current year taken: 70 - 90 = 160
            res['current_taken_ytd'], -20)

    def test_sum_leave_accruals_return_correct_previous_ytd(self):
        """
        Test that employee method sum_leave_accruals returns a dict
        containing the right amount for previous_ytd
        """
        res = self.employee_model.sum_leave_accruals(
            self.cr, self.uid, [self.employee_id], self.employee_id,
            self.accrual_code, '2014-01-01', context=self.context)

        self.assertEqual(
            # Previous ytd: -15 - 35 + 270 + 290 = 510
            res['previous_ytd'], 510)
