# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Odoo Canada. All Rights Reserved.
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

from openerp.osv import fields, orm


class HrSalaryRule(orm.Model):
    _inherit = 'hr.salary.rule'
    _columns = {
        'deduction_ids': fields.many2many(
            'hr.deduction.category',
            string='Income Tax Deductions',
        )
    }

    def sum_deductions(self, cr, uid, ids, payslip, context=None):
        """ Sum over an employee's income tax deductions
        """
        if not isinstance(payslip, orm.browse_record):
            payslip = payslip.dict

        payslip.refresh()

        if isinstance(ids, (int, long)):
            ids = [ids]

        assert(len(ids) == 1)

        salary_rule = self.browse(cr, uid, ids[0], context=context)

        categories = salary_rule.deduction_ids

        deductions = [
            d for d in payslip.deduction_line_ids
            if d.category_id in categories
        ]

        return sum(d.amount for d in deductions)
