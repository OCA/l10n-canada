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

from openerp.osv import orm, fields


PAYS_PER_YEAR = {
    'annually': 1,
    'semi-annually': 2,
    'quaterly': 4,
    'bi-monthly': 6,
    'monthly': 12,
    'semi-monthly': 24,
    'bi-weekly': 26,
    'weekly': 52,
    'daily': 365,
}


class HrPayslip(orm.Model):
    _inherit = 'hr.payslip'

    def _get_pays_per_year(
        self, cr, uid, ids, field_name=False, args=False, context=None
    ):
        res = {}

        for payslip in self.browse(cr, uid, ids, context=context):
            contract = payslip.contract_id

            res[payslip.id] = PAYS_PER_YEAR.get(
                contract.schedule_pay, False)

        return res

    _columns = {
        # Field required to compute deductions based on an annual amount
        'pays_per_year': fields.function(
            _get_pays_per_year,
            string='Number of pays per year', readonly=True, type='integer',
            store={
                'hr.payslip': (
                    lambda self, cr, uid, ids, c=None: ids,
                    ['contract_id'], 10),
            },
        ),
        'deduction_line_ids': fields.one2many(
            'hr.payslip.deduction.line',
            'payslip_id',
            'Income Tax Deductions',
            readonly=True, states={'draft': [('readonly', False)]},
        ),
    }

    def compute_sheet(self, cr, uid, ids, context=None):
        self.compute_deductions(cr, uid, ids, context=context)
        super(HrPayslip, self).compute_sheet(cr, uid, ids, context=context)

    def compute_deductions(self, cr, uid, ids, context=None):
        """
        Compute the deductions on the payslip.
        """
        for payslip in self.browse(cr, uid, ids, context=context):
            for deduction_line in payslip.deduction_line_ids:
                if deduction_line.source == 'employee':
                    deduction_line.unlink()

            pays_per_year = payslip.pays_per_year

            date_reference = payslip.date_payment

            deductions = [
                d for d in payslip.employee_id.deduction_ids
                if d.date_start <= date_reference <= d.date_end
            ]

            payslip.write({
                'deduction_line_ids': [(0, 0, {
                    'category_id': d.category_id.id,
                    'source': 'employee',
                    'amount': d.amount / pays_per_year
                    if d.amount_type == 'annual' else d.amount,
                }) for d in deductions]
            })
