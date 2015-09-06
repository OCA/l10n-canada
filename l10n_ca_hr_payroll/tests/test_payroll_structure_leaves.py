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

from .test_payroll_structure import TestPayrollStructureBase


class TestPayrollStructureLeaves(TestPayrollStructureBase):
    """
    Test the integration of salary rules related to leaves in the Canada
    payroll structure
    """

    def setUp(self):
        super(TestPayrollStructureLeaves, self).setUp()
        self.accrual_model = self.registry("hr.leave.accrual")
        self.accrual_line_model = self.registry("hr.leave.accrual.line")
        self.public_holidays_model = self.registry("hr.holidays.public")

        cr, uid, context = self.cr, self.uid, self.context

        self.contract_model.write(cr, uid, [self.contract_id], {
            'schedule_pay': 'monthly',
            'worked_hours_per_pay_period': 160,
        }, context=context)

        # Searching the employee accrual creates the accrual if
        # if does not exist
        for reference in [
            'hr_worked_days_activity.holiday_status_vacation',
            'hr_holidays.holiday_status_sl',
            'hr_holidays.holiday_status_comp',
        ]:
            self.employee_model.get_leave_accrual_id(
                cr, uid, self.employee_id, leave_type_id=self.ref(reference),
                context=context)

        # Get the employee's leave accruals
        self.vac_accrual_id = self.accrual_model.search(cr, uid, [
            ('employee_id', '=', self.employee_id),
            ('leave_type_id', '=', self.ref(
                'hr_worked_days_activity.holiday_status_vacation')),
        ], context=context)[0]

        self.sl_accrual_id = self.accrual_model.search(cr, uid, [
            ('employee_id', '=', self.employee_id),
            ('leave_type_id', '=', self.ref(
                'hr_holidays.holiday_status_sl')),
        ], context=context)[0]

        self.comp_accrual_id = self.accrual_model.search(cr, uid, [
            ('employee_id', '=', self.employee_id),
            ('leave_type_id', '=', self.ref(
                'hr_holidays.holiday_status_comp')),
        ], context=context)[0]

        for line in [
            (self.vac_accrual_id, 1500, '2014-12-31', 'cash'),
            (self.vac_accrual_id, -500, '2014-12-31', 'cash'),
            (self.vac_accrual_id, 1700, '2015-01-01', 'cash'),
            (self.vac_accrual_id, 40, '2014-12-31', 'hours'),
            (self.vac_accrual_id, -10, '2014-12-31', 'hours'),
            (self.vac_accrual_id, 45, '2015-01-01', 'hours'),
            (self.sl_accrual_id, 20, '2014-12-31', 'hours'),
            (self.sl_accrual_id, -5, '2015-01-01', 'hours'),
            (self.comp_accrual_id, 600, '2014-12-31', 'cash'),
            (self.comp_accrual_id, -200, '2015-01-01', 'cash'),
        ]:
            self.accrual_line_model.create(
                cr, uid, {
                    'accrual_id': line[0],
                    'description': 'test',
                    'source': 'manual',
                    'amount': line[1],
                    'date': line[2],
                    'amount_type': line[3],
                })

        # Remove the current public holidays record for 2015
        # So we can make a new one for testing
        holidays_public_ids = self.public_holidays_model.search(
            cr, uid, [
                ('year', '=', 2015),
                ('country_id', '=', self.canada_id)],
            context=context)

        if holidays_public_ids:
            self.public_holidays_model.unlink(
                cr, uid, holidays_public_ids, context=context)

        self.public_leave_id = self.public_holidays_model.create(
            self.cr, self.uid, {
                'year': 2015,
                'country_id': self.canada_id,
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
            }, context=context)

        self.public_leave_2_id = self.public_holidays_model.create(
            self.cr, self.uid, {
                'year': 2014,
                'country_id': self.canada_id,
                'line_ids': [
                    (0, 0, {
                        'date': '2014-12-25',
                        'name': 'Christmas',
                    }),
                ],
            }, context=context)

        # Create 2 payslips (one in 2014, two in 2015)
        self.payslip_ids = {
            ps[0]: self.create_payslip({
                'employee_id': self.employee_id,
                'company_id': self.company_id,
                'contract_id': self.contract_id,
                'date_from': ps[1],
                'date_to': ps[2],
                'struct_id': self.structure_id,
            }) for ps in [
                (1, '2014-12-01', '2014-12-31'),
                (2, '2015-01-01', '2015-01-31'),
            ]
        }

        # Create the worked_days records
        for wd in [
            # (date_from, date_to, activity_id, nb_hours, hourly_rate)
            ('2014-12-01', '2014-12-15', self.job_activity_id, 80, 40, 1),
            ('2014-12-16', '2014-12-31', self.job_activity_id, 80, 40, 1),

            ('2015-01-01', '2015-01-01', self.public_activity_id, 8, 40, 2),
            ('2015-01-02', '2015-01-02', self.public_activity_id, 8, 40, 2),
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
            round(payslip_2['VAC_AVAIL_HOURS'], 2),
            round(40 - 10 + 160 * 0.08, 2))

        self.assertEqual(
            round(payslip_2['VAC_REQ'], 2),
            round((4 * 8 + 20) * 40, 2))

        self.assertEqual(payslip_2['VAC_TAKEN'], payslip_2['VAC_AVAIL'])
        self.assertEqual(
            payslip_2['VAC_TAKEN_HOURS'], payslip_2['VAC_AVAIL_HOURS'])

        # Check Sick leaves
        self.assertEqual(payslip_2['SL_AVAIL'], 20 - 5)
        self.assertEqual(payslip_2['SL_REQ'], 8)
        self.assertEqual(payslip_2['SL_TAKEN_CASH'], 8 * 40)
        self.assertEqual(payslip_2['SL_TAKEN'], 8)

        # Check public days
        self.assertEqual(
            round(payslip_1['PUBLIC_AVAIL'], 2),
            round((80 + 80 * 8 / 16) * 40.0 / 20), 2)

        self.assertEqual(
            round(payslip_2['PUBLIC_AVAIL'], 2),
            round((80.0 * 13 / 15 + 80.0 * 15 / 16) * 2 * 40.0 / 20, 2))

        self.assertEqual(
            round(payslip_2['PUBLIC_REQ'], 2),
            round((8 + 8) * 40, 2))

        self.assertEqual(
            payslip_2['PUBLIC_TAKEN'],
            payslip_2['PUBLIC_AVAIL'])

        # Check Compensatory days
        self.assertEqual(payslip_1['COMP_ADDED'], payslip_1['PUBLIC_AVAIL'])
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
            + payslip_2['SL_TAKEN_CASH'] + payslip_2['PUBLIC_TAKEN'])

    def test_leaves_in_payslip_worked_days_wage(self):
        """
        Test how the leaves in payslip worked days are computed in
        the Canada payroll structure when employee is paid by wage
        """
        cr, uid, context = self.cr, self.uid, self.context

        self.contract_model.write(
            cr, uid, [self.contract_id], {
                'salary_computation_method': 'wage',
            }, context=context)

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
            round(1500 - 500 + payslip_1['VAC_ADDED'], 2))

        self.assertEqual(
            round(payslip_2['VAC_AVAIL_HOURS'], 2),
            round(40 - 10 + 160 * 0.08, 2))

        self.assertEqual(
            round(payslip_2['VAC_REQ'], 2),
            round((4 * 8 + 20) * 40, 2))

        self.assertEqual(payslip_2['VAC_TAKEN'], payslip_2['VAC_AVAIL'])
        self.assertEqual(
            payslip_2['VAC_TAKEN_HOURS'], payslip_2['VAC_AVAIL_HOURS'])

        # Check Sick leaves
        self.assertEqual(payslip_2['SL_AVAIL'], 20 - 5)
        self.assertEqual(payslip_2['SL_REQ'], 8)
        self.assertEqual(payslip_2['SL_TAKEN_CASH'], 8 * 40)
        self.assertEqual(payslip_2['SL_TAKEN'], 8)

        # Check public days
        self.assertEqual(payslip_2['PUBLIC_AVAIL'], 0)
        self.assertEqual(payslip_2['PUBLIC_REQ'], 0)
        self.assertEqual(payslip_2['PUBLIC_TAKEN'], 0)

        # Check Compensatory days
        self.assertEqual(payslip_1['COMP_ADDED'], payslip_1['PUBLIC_AVAIL'])
        self.assertEqual(payslip_2['COMP_ADDED'], 0)

        self.assertEqual(payslip_2['COMP_AVAIL'], 600 - 200)

        self.assertEqual(payslip_2['COMP_REQ'], 4 * 8 * 40)
        self.assertEqual(payslip_2['COMP_TAKEN'], payslip_2['COMP_AVAIL'])

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
            (self.vac_accrual_id, 2000, '2014-12-31', 'cash'),
            (self.vac_accrual_id, 50, '2014-12-31', 'hours'),
            (self.comp_accrual_id, 1000, '2014-12-31', 'cash'),
        ]:
            self.accrual_line_model.create(
                cr, uid, {
                    'accrual_id': line[0],
                    'description': 'test',
                    'source': 'manual',
                    'amount': line[1],
                    'date': line[2],
                    'amount_type': line[3],
                })

        for input_line in [
            (self.ref('payslip_input_unused_vac'), 1100),
            (self.ref('payslip_input_unused_comp'), 330),
            (self.ref('payslip_input_unused_sl'), 400),
        ]:
            self.input_model.create(
                cr, uid, {
                    'name': 'Test',
                    'category_id': input_line[0],
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

        # Check Unused Vacations
        self.assertEqual(payslip_2['VAC_AVAIL'], 1500 - 500 + 2000)
        self.assertEqual(payslip_2['VAC_AVAIL_HOURS'], 40 - 10 + 50)

        self.assertEqual(payslip_2['VAC_TAKEN_HOURS'], 4 * 8 + 20)
        self.assertEqual(
            payslip_2['VAC_REQ'], payslip_2['VAC_TAKEN_HOURS'] * 40)

        self.assertEqual(payslip_2['VAC_TAKEN'], payslip_2['VAC_REQ'])
        self.assertEqual(
            payslip_2['VAC_UNUSED'],
            1500 - 500 + 2000 - payslip_2['VAC_TAKEN'])

        self.assertEqual(
            payslip_2['VAC_UNUSED_HOURS'], payslip_2['VAC_UNUSED'] / 40)

        # Check Unused Sick leaves
        self.assertEqual(payslip_2['SL_AVAIL'], 20 - 5)
        self.assertEqual(payslip_2['SL_REQ'], 8)
        self.assertEqual(payslip_2['SL_TAKEN'], 8)

        self.assertEqual(payslip_2['HOURLY_RATE'], 40)
        self.assertEqual(payslip_2['SL_UNUSED_CASH'], 7 * 40)
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
