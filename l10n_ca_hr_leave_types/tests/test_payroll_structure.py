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


class test_canada_payroll_structure_leave(common.TransactionCase):
    def get_payslip_lines(self, payslip_id):
        """
        Get a dict of payslip lines
        """
        payslip = self.payslip_model.browse(
            self.cr, self.uid, payslip_id, context=self.context)

        return {
            line.code: line.total
            for line in payslip.details_by_salary_rule_category
        }

    def setUp(self):
        super(test_canada_payroll_structure_leave, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.worked_days_model = self.registry("hr.payslip.worked_days")
        self.contract_model = self.registry("hr.contract")
        self.job_model = self.registry("hr.job")
        self.activity_model = self.registry("hr.activity")
        self.structure_model = self.registry("hr.payroll.structure")
        self.deduction_model = self.registry("hr.deduction.category")
        self.benefit_model = self.registry("hr.benefit.category")
        self.accrual_model = self.registry("hr.leave.accrual")
        self.accrual_line_model = self.registry("hr.leave.accrual.line")
        self.public_holidays_model = self.registry("hr.holidays.public")
        self.country_model = self.registry("res.country")
        self.input_model = self.registry("hr.payslip.input")

        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        # Create an employee and all his deductions
        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
            }, context=context
        )

        # Get the canadian payroll structure
        self.structure_id = self.structure_model.search(
            cr, uid, [('code', '=', 'CA')], context=context)[0]

        # Create a contract
        self.contract_id = self.contract_model.create(
            cr, uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 52000,
                'schedule_pay': 'weekly',
                'struct_id': self.structure_id,
                'worked_hours_per_pay_period': 40,
                'week_start': '3',
                'weeks_of_vacation': 4,
                'salary_computation_method': 'wage',
            }, context=context)

        # Create a job for the employee
        self.job_id = self.job_model.create(
            cr, uid, {'name': 'job_id 1'}, context=context)

        # Get the id of the activity for job 1
        self.job_activity_id = self.job_model.browse(
            cr, uid, self.job_id, context=context
        ).activity_ids[0].id

        # Get the employee's leave accruals
        self.vac_accrual_id = self.accrual_model.search(
            cr, uid, [
                ('employee_id', '=', self.employee_id),
                ('code', '=', 'VAC'),
            ], context=context)[0]

        self.sick_accrual_id = self.accrual_model.search(
            cr, uid, [
                ('employee_id', '=', self.employee_id),
                ('code', '=', 'SL'),
            ], context=context)[0]

        self.comp_accrual_id = self.accrual_model.search(
            cr, uid, [
                ('employee_id', '=', self.employee_id),
                ('code', '=', 'COMP'),
            ], context=context)[0]

        for line in [
            (self.vac_accrual_id, 1500, '2014-12-31', False),
            (self.vac_accrual_id, 500, '2014-12-31', True),
            (self.vac_accrual_id, 1700, '2015-01-01', False),
            (self.sick_accrual_id, 20, '2014-12-31', False),
            (self.sick_accrual_id, 5, '2015-01-01', True),
            (self.comp_accrual_id, 600, '2014-12-31', False),
            (self.comp_accrual_id, 200, '2015-01-01', True),
        ]:
            self.accrual_line_model.create(
                cr, uid, {
                    'accrual_id': line[0],
                    'description': 'test',
                    'source': 'manual',
                    'amount': line[1],
                    'date': line[2],
                    'substract': line[3],
                })

        # Get the activity related to each leave type
        self.vac_activity_id = self.activity_model.search(
            cr, uid, [('code', '=', 'VAC')], context=context)[0]

        self.sl_activity_id = self.activity_model.search(
            cr, uid, [('code', '=', 'SL')], context=context)[0]

        self.comp_activity_id = self.activity_model.search(
            cr, uid, [('code', '=', 'COMP')], context=context)[0]

        self.legal_activity_id = self.activity_model.search(
            cr, uid, [('code', '=', 'LEGAL')], context=context)[0]

        canada_id = self.registry("res.country").search(
            self.cr, self.uid, [('code', '=', 'CA')], context=self.context
        )[0]

        self.public_holidays_model.create(
            self.cr, self.uid, {
                'year': 2015,
                'country_id': canada_id,
                'line_ids': [
                    (0, 0, {
                        'date': '2015-01-01',
                        'name': 'New Year',
                    }),
                    (0, 0, {
                        'date': '2015-01-02',
                        'name': 'Other Public Holidays',
                    }),
                ],
            }, context=self.context),

        self.public_holidays_model.create(
            self.cr, self.uid, {
                'year': 2014,
                'country_id': canada_id,
                'line_ids': [
                    (0, 0, {
                        'date': '2014-12-25',
                        'name': 'Christmas',
                    }),
                ],
            }, context=self.context),

        # Create 2 payslips (one in 2014, two in 2015)
        self.payslip_ids = {
            ps[0]: self.payslip_model.create(
                cr, uid, {
                    'employee_id': self.employee_id,
                    'contract_id': self.contract_id,
                    'date_from': ps[1],
                    'date_to': ps[2],
                    'struct_id': self.structure_id,
                }, context=context)
            for ps in [
                (1, '2014-12-01', '2014-12-31'),
                (2, '2015-01-01', '2015-01-31'),
            ]
        }

        # Create the worked_days records
        for wd in [
            # (date_from, date_to, activity_id, nb_hours, hourly_rate)
            ('2014-12-01', '2014-12-15', self.job_activity_id, 80, 40, 1),
            ('2014-12-16', '2014-12-31', self.job_activity_id, 80, 40, 1),

            ('2015-01-01', '2015-01-01', self.legal_activity_id, 8, 40, 2),
            ('2015-01-02', '2015-01-02', self.legal_activity_id, 8, 40, 2),
            ('2015-01-04', '2015-01-04', self.vac_activity_id, 8, 40, 2),
            ('2015-01-05', '2015-01-05', self.vac_activity_id, 8, 40, 2),
            ('2015-01-06', '2015-01-06', self.sl_activity_id, 8, 40, 2),
            ('2015-01-07', '2015-01-07', self.vac_activity_id, 8, 40, 2),
            ('2015-01-08', '2015-01-08', self.vac_activity_id, 8, 40, 2),
            ('2015-01-09', '2015-01-09', self.comp_activity_id, 8, 40, 2),
            ('2015-01-10', '2015-01-10', self.comp_activity_id, 8, 40, 2),
            ('2015-01-11', '2015-01-11', self.comp_activity_id, 8, 40, 2),
            ('2015-01-12', '2015-01-12', self.comp_activity_id, 8, 40, 2),

            ('2015-01-16', '2015-01-31', self.vac_activity_id, 20, 40, 2),

        ]:
            self.worked_days_model.create(
                cr, uid, {
                    'date_from': wd[0],
                    'date_to': wd[1],
                    'activity_id': wd[2],
                    'number_of_hours': wd[3],
                    'hourly_rate': wd[4],
                    'payslip_id': self.payslip_ids[wd[5]],
                }, context=context)

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.write(
            cr, uid, self.payslip_ids.values(), {'state': 'draft'},
            context=context)
        self.payslip_model.unlink(
            cr, uid, self.payslip_ids.values(), context=context)

        self.job_model.unlink(
            cr, uid, [self.job_id], context=context)
        self.contract_model.unlink(
            cr, uid, [self.contract_id], context=context)
        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)

        super(test_canada_payroll_structure_leave, self).tearDown()

    def test_leaves_in_payslip_worked_days(self):
        """
        Test how the leaves in payslip worked days are computed in
        the Canada payroll structure
        """
        cr, uid, context = self.cr, self.uid, self.context
        payslips = self.payslip_ids

        for payslip in [payslips[1], payslips[2]]:
            self.payslip_model.compute_sheet(
                cr, uid, [payslip], context=context)

            self.payslip_model.write(
                cr, uid, [payslip], {'state': 'done'}, context=context)

        payslip_1 = self.get_payslip_lines(payslips[1])
        payslip_2 = self.get_payslip_lines(payslips[2])

        # Check Vacations
        self.assertEqual(
            round(payslip_2['VAC_AVAIL'], 2),
            round(1500 - 500 + 40 * 160 * 0.08, 2))

        self.assertEqual(
            round(payslip_2['VAC_REQ'], 2),
            round((4 * 8 + 20) * 40, 2))

        self.assertEqual(payslip_2['VAC_TAKEN'], payslip_2['VAC_AVAIL'])

        # Check Sick leaves
        self.assertEqual(payslip_2['SL_AVAIL'], 20 - 5)
        self.assertEqual(payslip_2['SL_REQ'], 8)
        self.assertEqual(payslip_2['SL_TAKEN_CASH'], 8 * 40)
        self.assertEqual(payslip_2['SL_TAKEN'], 8)

        # Check legal days
        self.assertEqual(
            round(payslip_1['LEGAL_AVAIL'], 2),
            round((80 + 80 * 8 / 16) * 40.0 / 20), 2)

        self.assertEqual(
            round(payslip_2['LEGAL_AVAIL'], 2),
            round((80.0 * 13 / 15 + 80.0 * 15 / 16) * 2 * 40.0 / 20, 2))

        self.assertEqual(
            round(payslip_2['LEGAL_REQ'], 2),
            round((8 + 8) * 40, 2))

        self.assertEqual(
            payslip_2['LEGAL_TAKEN'],
            payslip_2['LEGAL_AVAIL'])

        # Check Compensatory days
        self.assertEqual(payslip_1['COMP_ADDED'], payslip_1['LEGAL_AVAIL'])
        self.assertEqual(payslip_2['COMP_ADDED'], 0)

        self.assertEqual(
            round(payslip_2['COMP_AVAIL'], 2),
            round(600 - 200 + payslip_1['COMP_ADDED'], 2))

        self.assertEqual(payslip_2['COMP_REQ'], 4 * 8 * 40)
        self.assertEqual(payslip_2['COMP_TAKEN'], payslip_2['COMP_AVAIL'])
        self.assertEqual(payslip_2['OTHER_WAGE'], 0)

        self.assertEqual(
            payslip_2['GROSSP'],
            payslip_2['COMP_TAKEN'] + payslip_2['VAC_TAKEN']
            + payslip_2['SL_TAKEN_CASH'] + payslip_2['LEGAL_TAKEN'])

    def test_leaves_in_payslip_input(self):
        """
        Test how the leaves in payslip inputs are computed in
        the Canada payroll structure

        This method tests the salary rules
        VAC_UNUSED, SL_UNUSED, COMP_UNUSED, OTHER_WAGE
        """
        cr, uid, context = self.cr, self.uid, self.context
        payslips = self.payslip_ids

        for line in [
            (self.vac_accrual_id, 2000, '2014-12-31'),
            (self.comp_accrual_id, 1000, '2014-12-31'),
        ]:
            self.accrual_line_model.create(
                cr, uid, {
                    'accrual_id': line[0],
                    'description': 'test',
                    'source': 'manual',
                    'substract': False,
                    'amount': line[1],
                    'date': line[2],
                })

        for input_line in [
            ('VAC_UNUSED', 1100),
            ('COMP_UNUSED', 330),
            ('SL_UNUSED', 400),
        ]:
            self.input_model.create(
                cr, uid, {
                    'name': 'Test',
                    'type': input_line[0],
                    'amount': input_line[1],
                    'payslip_id': payslips[2],
                }, context=context)

        # Only compute payslip 2. The impact of payslip 1 is already
        # tested in test_leaves_in_payslip_worked_days
        for payslip in [payslips[2]]:
            self.payslip_model.compute_sheet(
                cr, uid, [payslip], context=context)

            self.payslip_model.write(
                cr, uid, [payslip], {'state': 'done'}, context=context)

        payslip_2 = self.get_payslip_lines(payslips[2])
        payslip_browse = self.payslip_model.browse(
            cr, uid, payslips[2], context=context)

        # Check Unused Vacations
        self.assertEqual(payslip_2['VAC_AVAIL'], 1500 - 500 + 2000)

        # (4 * 8 + 20) * 40 = 2080
        self.assertEqual(payslip_2['VAC_REQ'], 2080)

        self.assertEqual(payslip_2['VAC_TAKEN'], payslip_2['VAC_REQ'])
        self.assertEqual(payslip_2['VAC_UNUSED'], 1500 - 500 + 2000 - 2080)

        # Test that the vacations were correctly reduced
        unused_vac = self.payslip_model.sum_payslip_input(
            cr, uid, [payslips[2]], payslip=payslip_browse,
            input_types=['VAC_UNUSED'], context=context)

        self.assertEqual(unused_vac, payslip_2['VAC_UNUSED'])

        # Check Unused Sick leaves
        self.assertEqual(payslip_2['SL_AVAIL'], 20 - 5)
        self.assertEqual(payslip_2['SL_REQ'], 8)
        self.assertEqual(payslip_2['SL_TAKEN'], 8)

        # Hourly_rate_from_wage = 52000 / 52 / 40 = 25
        self.assertEqual(payslip_2['HOURLY_RATE'], 25)
        self.assertEqual(payslip_2['SL_UNUSED_CASH'], 7 * 25)
        self.assertEqual(payslip_2['SL_UNUSED'], 7)

        # Check Unused Compensatory days
        self.assertEqual(payslip_2['COMP_AVAIL'], 1000 + 600 - 200)

        # 4 * 8 * 40 = 1280
        self.assertEqual(payslip_2['COMP_REQ'], 1280)
        self.assertEqual(payslip_2['COMP_TAKEN'], payslip_2['COMP_REQ'])
        self.assertEqual(
            payslip_2['COMP_UNUSED'],
            payslip_2['COMP_AVAIL'] - payslip_2['COMP_TAKEN'])

        self.assertEqual(
            payslip_2['OTHER_WAGE'],
            payslip_2['VAC_UNUSED'] + payslip_2['COMP_UNUSED']
            + payslip_2['SL_UNUSED_CASH'])

        sl_accrual = self.employee_model.sum_leave_accruals(
            cr, uid, [payslips[2]],
            self.employee_id, 'SL', payslip_browse.date_to,
            context=context)

        self.assertEqual(sl_accrual['current_taken_ytd'], 20)

        comp_accrual = self.employee_model.sum_leave_accruals(
            cr, uid, [payslips[2]],
            self.employee_id, 'COMP', payslip_browse.date_to,
            context=context)

        self.assertEqual(comp_accrual['current_taken_ytd'], 1000 + 600)

        vac_accrual = self.employee_model.sum_leave_accruals(
            cr, uid, [payslips[2]],
            self.employee_id, 'VAC', payslip_browse.date_to,
            context=context)

        self.assertEqual(vac_accrual['current_taken_ytd'], 1500 - 500 + 2000)
