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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class HrEmployeeDeduction(orm.Model):
    _name = 'hr.employee.deduction'
    _description = 'Income Tax Deduction'
    _columns = {
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True,
            readonly=True,
            ondelete='cascade',
        ),
        'category_id': fields.many2one(
            'hr.deduction.category',
            'Deduction',
            required=True,
            ondelete='cascade',
        ),
        'amount': fields.float(
            'Amount',
            required=True,
            help="It is used in computation of the payslip. "
            "May be an annual or periodic amount depending on the category. "
            "The deduction may be a tax credit."
        ),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date'),

        'amount_type': fields.related(
            'category_id',
            'amount_type',
            type='selection',
            selection=[
                ('each_pay', 'Each Pay'),
                ('annual', 'Annual'),
            ],
            readonly=True,
            string="Amount Type",
        ),
        'jurisdiction_id': fields.related(
            'category_id',
            'jurisdiction_id',
            type='many2one',
            relation='hr.deduction.jurisdiction',
            string='Jurisdiction',
            readonly=True,
        ),
    }
    _defaults = {
        'amount': 0.0,
        'date_start': lambda *a: datetime.now().strftime(
            DEFAULT_SERVER_DATE_FORMAT),
    }

    def onchange_category_id(self, cr, uid, ids, category_id, amount):
        res = {'value': {}}
        if category_id:
            category = self.pool.get('hr.deduction.category')
            category = category.browse(cr, uid, category_id)
            res['value'].update({
                'amount': amount or category.default_amount,
                'amount_type': category.amount_type,
                'jurisdiction_id': category.jurisdiction_id.id,
            })

        return res
