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


class TestQcPayrollAccountBase(object):
    """ Mixin for testing qc payroll accounting """

    def setUp_qc_payroll_accounting(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.hsf_payable = self.create_account('payable', 2000001)
        self.hsf_expense = self.create_account('other', 5000001)

        hsf_rule_id = self.ref('l10n_ca_qc_hr_payroll.rule_qc_hsf_er_c')

        self.rule_model.write(cr, uid, [hsf_rule_id], {
            'account_debit': self.hsf_expense.id,
            'account_credit': self.hsf_payable.id,
        }, context=context)

        self.cnt_payable = self.create_account('payable', 2000002)
        self.cnt_expense = self.create_account('other', 5000002)

        self.csst_payable = self.create_account('payable', 2000003)
        self.csst_expense = self.create_account('other', 5000003)

        self.wsdrf_payable = self.create_account('payable', 2000004)
        self.wsdrf_expense = self.create_account('other', 5000004)
        self.wsdrf_reported = self.create_account('other', 1000004)

        self.company_model.write(cr, uid, [self.company_id], {
            'payroll_journal_id': self.journal_id,

            'qc_cnt_debit_account': self.cnt_expense.id,
            'qc_cnt_credit_account': self.cnt_payable.id,

            'qc_wsdrf_debit_account': self.wsdrf_expense.id,
            'qc_wsdrf_credit_account': self.wsdrf_payable.id,
            'qc_wsdrf_reported_account': self.wsdrf_reported.id,
        }, context=context)

    def create_account(self, account_type, code):
        cr, uid, context = self.cr, self.uid, self.context

        account_id = self.account_model.create(cr, uid, {
            'name': 'Test',
            'type': account_type,
            'code': code,
            'user_type': self.payable_type if account_type == 'payable'
            else self.expense_type,
            'company_id': self.company_id,
        })

        return self.account_model.browse(
            cr, uid, account_id, context=context)

    def get_account_move_line(self, move, account):
        lines = [
            line for line in move.line_id
            if line.account_id == account
        ]

        self.assertEqual(len(lines), 1)
        return lines[0]
