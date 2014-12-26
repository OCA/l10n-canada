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
        self.accrual_model = self.registry("hr.leave.accrual")
        self.payslip_model = self.registry("hr.payslip")
        self.worked_days_model = self.registry("hr.payslip.worked_days")
        self.contract_model = self.registry("hr.contract")
        self.job_model = self.registry("hr.job")
        self.activity_model = self.registry("hr.activity")
        self.context = self.user_model.context_get(self.cr, self.uid)

        # Create an employee
        self.employee_1_id = self.employee_model.create(
            self.cr, self.uid, {'name': 'Employee 1'}, context=self.context
        )
        self.employee_2_id = self.employee_model.create(
            self.cr, self.uid, {'name': 'Employee 1'}, context=self.context
        )

        # Create a job for the employee
        job_id = self.job_model.create(
            self.cr, self.uid, {'name': 'job_id 1'}, context=self.context
        )
        # Get the id of the activity for job 1
        self.job_activity_id = self.job_model.browse(
            self.cr, self.uid, job_id, context=self.context
        ).activity_ids[0].id

        # Create 2 contracts for the employees
        self.contract_1_id = self.contract_model.create(
            self.cr, self.uid,
            {
                'employee_id': self.employee_1_id,
                'name': 'Contract 1',
                'wage': 50000,
                # Week of work starts monday
                'week_start': '1',
            },
            context=self.context
        )
        self.contract_2_id = self.contract_model.create(
            self.cr, self.uid,
            {
                'employee_id': self.employee_2_id,
                'name': 'Contract 2',
                'wage': 50000,
                'week_start': '1',
            },
            context=self.context
        )

        # Create payslips
        self.payslip_ids = {
            line[0]: self.payslip_model.create(
                self.cr, self.uid,
                {
                    'employee_id': line[1],
                    'contract_id': line[2],
                    'date_from': line[3],
                    'date_to': line[4],
                },
                context=self.context,
            ) for line in [
                (1, self.employee_1_id, self.contract_1_id,
                    '2014-01-01', '2014-01-15'),
                (2, self.employee_1_id, self.contract_1_id,
                    '2014-01-16', '2014-01-31'),
                (3, self.employee_1_id, self.contract_1_id,
                    '2014-02-01', '2014-02-15'),
                (4, self.employee_1_id, self.contract_1_id,
                    '2014-02-16', '2014-02-28'),

                (5, self.employee_2_id, self.contract_2_id,
                    '2014-02-01', '2014-02-15'),
            ]
        }

        # Need to assign 'state': 'done' after the payslip is created
        # hr_payslip has a workflow start node that does
        # write({'state': 'draft'})
        self.payslip_model.write(
            self.cr, self.uid,
            [self.payslip_ids[n] for n in [1, 2, 3, 5]],
            {'state': 'done'},
        )

        for line in [
            # date_from, date_to, nb_hours, hourly_rate, rate (%), payslip_id,
            # contract_id

            # 100% excluded from the interval
            ('2014-01-01', '2014-01-15', 5, 20, 100, self.payslip_ids[1],
                self.contract_1_id),
            ('2014-01-19', '2014-01-19', 7, 20, 100, self.payslip_ids[2],
                self.contract_1_id),

            # 60% included
            ('2014-01-18', '2014-01-22', 11, 20, 100, self.payslip_ids[2],
                self.contract_1_id),

            # 100% included
            ('2014-01-20', '2014-01-21', 13, 20, 110, self.payslip_ids[2],
                self.contract_1_id),
            ('2014-02-04', '2014-02-10', 17, 25, 90, self.payslip_ids[3],
                self.contract_1_id),
            ('2014-02-16', '2014-02-16', 21, 35, 70, self.payslip_ids[4],
                self.contract_1_id),

            # 50% included
            ('2014-02-16', '2014-02-17', 29, 20, 100, self.payslip_ids[4],
                self.contract_1_id),

            # 100% excluded
            ('2014-02-17', '2014-02-28', 31, 20, 100, self.payslip_ids[4],
                self.contract_1_id),

            # 100% excluded - Not the required employee
            ('2014-02-04', '2014-02-10', 17, 20, 100, self.payslip_ids[5],
                self.contract_2_id),
        ]:
            self.worked_days_model.create(
                self.cr, self.uid,
                {
                    'date_from': line[0],
                    'date_to': line[1],
                    'number_of_hours': line[2],
                    'activity_id': self.job_activity_id,
                    'hourly_rate': line[3],
                    'rate': line[4],
                    'payslip_id': line[5],
                    'code': 'ddd',
                    'name': 'ddd',
                    'contract_id': line[6],
                },
                context=self.context,
            )

    def tearDown(self):
        payslip_ids = [self.payslip_ids[n] for n in self.payslip_ids]

        self.payslip_model.write(
            self.cr, self.uid,
            payslip_ids,
            {'state': 'draft'},
            context=self.context,
        )

        self.payslip_model.unlink(
            self.cr, self.uid, payslip_ids, context=self.context)

        self.contract_model.unlink(
            self.cr, self.uid,
            [self.contract_1_id, self.contract_2_id], context=self.context)

        self.employee_model.unlink(
            self.cr, self.uid,
            [self.employee_1_id, self.employee_2_id], context=self.context)

        super(test_canada_payslip, self).tearDown()

    def test_get_4_weeks_of_gross(self):
        """
        Tests the method get_4_weeks_of_gross
        used to get the allocation of an employee for a public holiday
        (legal leaves)
        """
        payslip = self.payslip_model.browse(
            self.cr, self.uid, self.payslip_ids[4], context=self.context)

        res = self.payslip_model.get_4_weeks_of_gross(
            self.cr, self.uid, [self.payslip_ids[4]],
            payslip,
            self.employee_1_id,
            self.contract_1_id,
            leave_date='2014-02-20',
            context=None
        )

        self.assertTrue(
            res ==
            11 * 20 * 1.0 * 0.60
            + 13 * 20 * 1.1
            + 17 * 25 * 0.9
            + 21 * 35 * 0.7
            + 29 * 20 * 1.0 * 0.50
        )

    def test_get_4_weeks_of_gross_with_refunds(self):
        """
        Tests the method get_4_weeks_of_gross
        When there is a credit note.
        """
        self.payslip_model.write(
            self.cr, self.uid,
            [self.payslip_ids[2], self.payslip_ids[3]],
            {'credit_note': True},
            context=self.context,
        )

        payslip = self.payslip_model.browse(
            self.cr, self.uid, self.payslip_ids[4], context=self.context)

        res = self.payslip_model.get_4_weeks_of_gross(
            self.cr, self.uid, [self.payslip_ids[4]],
            payslip,
            self.employee_1_id,
            self.contract_1_id,
            leave_date='2014-02-20',
            context=None
        )

        # Amounts in payslips no 2 and 3 are multiplied by -1
        self.assertTrue(
            res ==
            11 * 20 * 1.0 * 0.60 * -1
            + 13 * 20 * 1.1 * -1
            + 17 * 25 * 0.9 * -1
            + 21 * 35 * 0.7
            + 29 * 20 * 1.0 * 0.50
        )
