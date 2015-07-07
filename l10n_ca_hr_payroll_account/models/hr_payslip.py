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

from openerp.osv import orm


class HrPayslip(orm.Model):
    _inherit = 'hr.payslip'

    def _get_default_journal(self, cr, uid, context=None):
        company = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id
        journal = company.payroll_journal_id

        return journal.id if journal else False

    def onchange_contract_id(
        self, cr, uid, ids, date_from, date_to,
        employee_id=False, contract_id=False, context=None
    ):
        """When changing the employee / contract, if the contract has
        no salary journal, take the salary journal on the company
        """
        res = super(HrPayslip, self).onchange_contract_id(
            cr, uid, ids, date_from=date_from, date_to=date_to,
            employee_id=employee_id, contract_id=contract_id, context=context)

        if not res['value'].get('journal_id') and employee_id:
            employee = self.pool['hr.employee'].browse(
                cr, uid, employee_id, context=context)

            journal = employee.company_id.payroll_journal_id
            res['journal_id'] = journal.id if journal else False

        return res

    _defaults = {
        'journal_id': lambda self, *a: self._get_default_journal(*a),
    }
