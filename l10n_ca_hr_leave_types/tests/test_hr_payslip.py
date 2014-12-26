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


class test_canada_payslip(common.TransactionCase):
    def setUp(self):
        super(test_canada_payslip, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.worked_days_model = self.registry("hr.payslip.worked_days")
        self.contract_model = self.registry("hr.contract")
        self.job_model = self.registry("hr.job")
        self.activity_model = self.registry("hr.activity")
        self.input_model = self.registry("hr.payslip.input")

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        # Create an employee
        self.employee_id = self.employee_model.create(
            cr, uid, {'name': 'Employee 1'}, context=context)

        # Create a job for the employee
        job_id = self.job_model.create(
            cr, uid, {'name': 'job_id 1'}, context=context)

        # Get the id of the activity for job 1
        self.job_activity_id = self.job_model.browse(
            cr, uid, job_id, context=context).activity_ids[0].id

        self.vac_id = self.activity_model.search(
            cr, uid, [('code', '=', 'VAC')], context=context)[0]

        self.legal_id = self.activity_model.search(
            cr, uid, [('code', '=', 'LEGAL')], context=context)[0]

        self.sl_id = self.activity_model.search(
            cr, uid, [('code', '=', 'SL')], context=context)[0]

        self.comp_id = self.activity_model.search(
            cr, uid, [('code', '=', 'COMP')], context=context)[0]

        # Create a contract for the employee
        self.contract_id = self.contract_model.create(
            cr, uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
            }, context=context)

        # Create a payslip
        self.payslip_id = self.payslip_model.create(
            cr, uid, {
                'employee_id': self.employee_id,
                'contract_id': self.contract_id,
                'date_from': '2014-01-01',
                'date_to': '2014-01-31',
            }, context=context,)

        for line in [
            # date_from, date_to, nb_hours, activity_id, hourly_rate, rate (%)
            ('2014-01-01', '2014-01-01', 111, self.job_activity_id, 20, 100),
            ('2014-01-02', '2014-01-10', 113, self.job_activity_id, 20, 100),
            ('2014-01-31', '2014-01-31', 117, self.job_activity_id, 20, 100),

            ('2014-01-01', '2014-01-01', 11, self.vac_id, 15, 90),
            ('2014-01-02', '2014-01-10', 13, self.vac_id, 10, 100),
            ('2014-01-31', '2014-01-31', 17, self.vac_id, 25, 150),

            ('2014-01-01', '2014-01-01', 111, self.sl_id, 20, 100),
            ('2014-01-02', '2014-01-10', 113, self.comp_id, 20, 100),
            ('2014-01-31', '2014-01-31', 117, self.legal_id, 20, 100),
        ]:
            self.worked_days_model.create(
                cr, uid, {
                    'date_from': line[0],
                    'date_to': line[1],
                    'number_of_hours': line[2],
                    'activity_id': line[3],
                    'hourly_rate': line[4],
                    'rate': line[5],
                    'payslip_id': self.payslip_id,
                    'code': 'ddd',
                    'name': 'ddd',
                    'contract_id': self.contract_id,
                }, context=context)

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.unlink(
            cr, uid, [self.payslip_id], context=context)
        self.contract_model.unlink(
            cr, uid, [self.contract_id], context=context)
        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)

        super(test_canada_payslip, self).tearDown()

    def test_sum_leave_category_nb_hours(self):
        cr, uid, context = self.cr, self.uid, self.context

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        res = self.payslip_model.sum_leave_category(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            leave_code='VAC',
            multiply_by_rate=False,
            context=context
        )

        self.assertEqual(res, 11 + 13 + 17)

    def test_sum_leave_category_cash(self):
        cr, uid, context = self.cr, self.uid, self.context

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        res = self.payslip_model.sum_leave_category(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            leave_code='VAC',
            multiply_by_rate=True,
            context=context
        )

        self.assertEqual(
            res, 11 * 15 * 0.90
            + 13 * 10 * 1.0
            + 17 * 25 * 1.5
        )

    def test_reduce_leave_hours(self):
        """
        Test reduce_leave_hours with divide_by_rate=False
        """
        cr, uid, context = self.cr, self.uid, self.context

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        # Reduce the leave hours
        self.payslip_model.reduce_leave_hours(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            leave_code='VAC', reduction=20,
            context=context
        )

        # Validate how many hours are left in the worked days
        res = self.payslip_model.sum_leave_category(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            leave_code='VAC',
            multiply_by_rate=False,
            context=context
        )

        self.assertEqual(res, 11 + 13 + 17 - 20)

    def test_reduce_leave_hours_cash(self):
        """
        Test reduce_leave_hours with divide_by_rate=True
        """
        cr, uid, context = self.cr, self.uid, self.context

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        # Reduce the leave hours
        self.payslip_model.reduce_leave_hours(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            leave_code='VAC', reduction=700,
            divide_by_rate=True,
            context=context
        )

        # Validate how much cash is left in the worked days
        res = self.payslip_model.sum_leave_category(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            leave_code='VAC',
            multiply_by_rate=True,
            context=context
        )

        self.assertEqual(
            res, 11 * 15 * 0.90
            + 13 * 10 * 1.0
            + 17 * 25 * 1.5
            - 700
        )

        # Validate how many hours are left in the worked days
        res = self.payslip_model.sum_leave_category(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            leave_code='VAC',
            multiply_by_rate=False,
            context=context
        )

        # The method should reduce the worked days with the highest
        # date first
        reduce_jan_31 = 17 * 25 * 1.5
        reduction = 17 + (700 - reduce_jan_31) / (10 * 1.0)
        self.assertEqual(res, 11 + 13 + 17 - reduction)

    def test_reduce_payslip_input(self):
        """
        Test test_reduce_payslip_input
        """
        cr, uid, context = self.cr, self.uid, self.context

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        for input_line in [
            ('VAC_UNUSED', 200),
            ('BONUS', 300),
            ('RETRO_PAY', 400),
            ('VAC_UNUSED', 150),
        ]:
            self.input_model.create(
                cr, uid, {
                    'name': 'Test',
                    'type': input_line[0],
                    'amount': input_line[1],
                    'payslip_id': self.payslip_id,
                }, context=context)

        # Reduce the input amounts
        self.payslip_model.reduce_payslip_input_amount(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            input_types='VAC_UNUSED', reduction=20,
            context=context
        )

        # Validate how much is left in the inputs
        res = self.payslip_model.sum_payslip_input(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            input_types='VAC_UNUSED',
            context=context
        )

        self.assertEqual(res, 200 + 150 - 20)

        # Reduce the input amounts
        self.payslip_model.reduce_payslip_input_amount(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            input_types='VAC_UNUSED', reduction=400,
            context=context
        )

        # Validate how much is left in the inputs
        res = self.payslip_model.sum_payslip_input(
            cr, uid, [self.payslip_id],
            payslip=payslip,
            input_types='VAC_UNUSED',
            context=context
        )

        self.assertEqual(res, 0)
