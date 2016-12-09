# -*- coding:utf-8 -*-#########################################################
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class hr_releve_1_summary(orm.Model):
    _inherit = 'hr.releve_1.summary'

    _columns = {
        'move_id': fields.many2one(
            'account.move',
            'Accounting Entry',
            readonly=True,
        ),
    }

    def button_confirm(self, cr, uid, ids, context=None):
        super(hr_releve_1_summary, self).button_confirm(
            cr, uid, ids, context=context)
        self._cancel_account_move(cr, uid, ids, context=context)
        self._create_account_move(cr, uid, ids, context=context)

    def button_cancel(self, cr, uid, ids, context=None):
        super(hr_releve_1_summary, self).button_cancel(
            cr, uid, ids, context=context)
        self._cancel_account_move(cr, uid, ids, context=context)

    def _cancel_account_move(self, cr, uid, ids, context=None):
        for summary in self.browse(cr, uid, ids, context=context):
            if summary.move_id:
                summary.move_id.button_cancel()

    def _create_account_move(self, cr, uid, ids, context=None):

        for summary in self.browse(cr, uid, ids, context=context):
            company = summary.company_id
            if not company.payroll_journal_id:
                raise orm.except_orm(
                    _("Error"),
                    _("The payroll journal is not set for company %s.") %
                    company.name)

            hsf_rule_id = self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'l10n_ca_qc_hr_payroll', 'rule_qc_hsf_er_c')[1]

            rule_model = self.pool['hr.salary.rule']
            rule_hsf = rule_model.browse(cr, uid, hsf_rule_id, context=context)

            hsf_debit = rule_hsf.account_debit
            hsf_credit = rule_hsf.account_credit

            if not hsf_debit or not hsf_credit:
                raise orm.except_orm(
                    _("Error"),
                    _("You have not correctly set the "
                        "accounts for salary rule %s.") % rule_hsf.name)

            cnt_debit = company.qc_cnt_debit_account
            cnt_credit = company.qc_cnt_credit_account

            if not cnt_debit or not cnt_credit:
                raise orm.except_orm(
                    _("Error"),
                    _("You have not correctly set the CNT "
                        "accounts for %s.")
                    % company.name)

            hsf_entry_name = _("HSF Contribution")
            cnt_entry_name = _("CNT Contribution")

            hsf_payable = summary.hsf_amount_payable
            cnt_payable = summary.cnt_amount_payable

            move_lines = [
                (0, 0, {
                    'name': hsf_entry_name,
                    'account_id': hsf_debit.id,
                    'debit': hsf_payable if hsf_payable > 0 else 0,
                    'credit': -hsf_payable if hsf_payable < 0 else 0,
                }),
                (0, 0, {
                    'name': hsf_entry_name,
                    'account_id': hsf_credit.id,
                    'debit': -hsf_payable if hsf_payable < 0 else 0,
                    'credit': hsf_payable if hsf_payable > 0 else 0,
                }),
                (0, 0, {
                    'name': cnt_entry_name,
                    'account_id': cnt_debit.id,
                    'debit': cnt_payable if cnt_payable > 0 else 0,
                    'credit': -cnt_payable if cnt_payable < 0 else 0,
                }),
                (0, 0, {
                    'name': cnt_entry_name,
                    'account_id': cnt_credit.id,
                    'debit': -cnt_payable if cnt_payable < 0 else 0,
                    'credit': cnt_payable if cnt_payable > 0 else 0,
                }),
            ]

            wsdrf_debit = company.qc_wsdrf_debit_account
            wsdrf_credit = company.qc_wsdrf_credit_account
            wsdrf_reported_account = company.qc_wsdrf_reported_account

            if summary.wsdrf_salaries:

                if (
                    not wsdrf_debit or not wsdrf_credit or
                    not wsdrf_reported_account
                ):
                    raise orm.except_orm(
                        _("Error"),
                        _("You have not correctly set the WSDRF "
                            "accounts for %s.")
                        % company.name)

                wsdrf_entry_name = _("WSDRF Contribution")

                wsdrf_reported = (
                    summary.wsdrf_reported - summary.wsdrf_previous_reported)
                wsdrf_payable = summary.wsdrf_contribution
                wsdrf_expense = summary.wsdrf_contribution - wsdrf_reported

                move_lines += [
                    (0, 0, {
                        'name': wsdrf_entry_name,
                        'account_id': wsdrf_debit.id,
                        'debit': wsdrf_expense if wsdrf_expense > 0 else 0,
                        'credit': -wsdrf_expense if wsdrf_expense < 0 else 0,
                    }),
                    (0, 0, {
                        'name': wsdrf_entry_name,
                        'account_id': wsdrf_credit.id,
                        'debit': -wsdrf_payable if wsdrf_payable < 0 else 0,
                        'credit': wsdrf_payable if wsdrf_payable > 0 else 0,
                    }),
                    (0, 0, {
                        'name': wsdrf_entry_name,
                        'account_id': wsdrf_reported_account.id,
                        'debit': wsdrf_reported if wsdrf_reported > 0 else 0,
                        'credit': -wsdrf_reported if wsdrf_reported < 0 else 0,
                    }),
                ]

            move_obj = self.pool['account.move']
            period_obj = self.pool['account.period']

            if context is None:
                context = {}

            # period_obj.find needs to have the company id in the context
            # to work properly
            context['company_id'] = company.id

            move_id = move_obj.create(
                cr, uid, {
                    'company_id': company.id,
                    'journal_id': company.payroll_journal_id.id,
                    'period_id': period_obj.find(
                        cr, uid, summary.date, context=context)[0],
                    'ref': _("Summary 1 - Year %s") % summary.year,
                    'date': summary.date,
                    'line_id': move_lines,
                }, context=context)

            summary.write({'move_id': move_id})
