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

from openerp.addons.l10n_ca_qc_hr_payroll.tests.test_hr_releve_1_summary \
    import TestHrReleve1SummaryBase

from .test_qc_payroll_account_base import TestQcPayrollAccountBase


class TestHrReleve1SummaryAccount(
    TestHrReleve1SummaryBase, TestQcPayrollAccountBase
):

    def setUp_payroll_accounting(self):

        super(TestHrReleve1SummaryAccount, self).setUp_payroll_accounting()
        super(TestHrReleve1SummaryAccount, self).setUp_qc_payroll_accounting()

        self.vals = {
            'hsf_salaries': 100000,
            'hsf_exemption_code': '06',
            'hsf_exemption_amount': 20000,
            'hsf_contribution_rate': 4.0,
            'hsf_reduction_basis': 25000,
            'hsf_reduction_rate': 2.0,
            'hsf_amount_remitted': 2000,

            'cnt_salaries': 200000,
            'cnt_rate': 0.08,

            'wsdrf_salaries': 700000,
            'wsdrf_rate': 1.0,
            'wsdrf_previous_reported': 1000,
            'wsdrf_expenses_current': 2250,
            'wsdrf_expenses': 3000,
        }

    def prepare_summary(self):
        self.compute_payslips()

        summary = self.create_summary()
        summary.generate_slips()

        summary.write(self.vals)

        summary.button_confirm_slips()
        summary.button_confirm()
        summary.refresh()
        move = summary.move_id

        self.hsf_payable_line = self.get_account_move_line(
            move, self.hsf_payable)
        self.hsf_expense_line = self.get_account_move_line(
            move, self.hsf_expense)
        self.cnt_payable_line = self.get_account_move_line(
            move, self.cnt_payable)
        self.cnt_expense_line = self.get_account_move_line(
            move, self.cnt_expense)
        self.wsdrf_payable_line = self.get_account_move_line(
            move, self.wsdrf_payable)
        self.wsdrf_expense_line = self.get_account_move_line(
            move, self.wsdrf_expense)
        self.wsdrf_reported_line = self.get_account_move_line(
            move, self.wsdrf_reported)

    def test_releve_1_summary_account_entry(self):
        self.prepare_summary()

        # (100000 - 20000) * 4.0 % - 25000 * 2.0 % - 2000 = 700
        self.assertEqual(self.hsf_payable_line.credit, 700)
        self.assertEqual(self.hsf_expense_line.debit, 700)

        # 200000 * 0.08 % = 160
        self.assertEqual(self.cnt_payable_line.credit, 160)
        self.assertEqual(self.cnt_expense_line.debit, 160)

        # 700000 * 1.0 % - 3000 = 4000
        self.assertEqual(self.wsdrf_payable_line.credit, 4000)

        # 2250 - 3000
        self.assertEqual(self.wsdrf_reported_line.credit, 750)

        # 4000 + 750 = 4750
        self.assertEqual(self.wsdrf_expense_line.debit, 4750)

    def test_releve_1_summary_account_entry_2(self):
        self.vals['hsf_amount_remitted'] = 12000
        self.vals['wsdrf_expenses_current'] = 7500

        self.prepare_summary()

        # (100000 - 20000) * 4.0 % - 25000 * 2.0 % - 12000 = -9300
        self.assertEqual(self.hsf_payable_line.debit, 9300)
        self.assertEqual(self.hsf_expense_line.credit, 9300)

        # 700000 * 1.0 % - 3000 = 4000
        self.assertEqual(self.wsdrf_payable_line.credit, 4000)

        # 7500 - 3000 = 4500
        self.assertEqual(self.wsdrf_reported_line.debit, 4500)

        # 4000 - 4500 = -500
        self.assertEqual(self.wsdrf_expense_line.credit, 500)
