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


class HrDeductionCategory(orm.Model):
    _name = 'hr.deduction.category'
    _description = 'Income Tax Deduction Category'
    _columns = {
        'name': fields.char('Category Name', required=True),
        'description': fields.text(
            'Description',
            required=True,
            help="Brief explanation of which benefits the category contains."
        ),
        'default_amount': fields.float(
            'Default Amount',
            required=True
        ),
        'amount_type': fields.selection(
            [
                ('each_pay', 'Each Pay'),
                ('annual', 'Annual'),
            ],
            required=True,
            string="Amount Type",
        ),
        'jurisdiction_id': fields.many2one(
            'hr.deduction.jurisdiction',
            'Jurisdiction',
            required=True,
        ),
        'salary_rule_ids': fields.many2many(
            'hr.salary.rule',
            string='Salary Rules',
            help='Salary Rules in which the deduction will be added',
        ),
        'active': fields.boolean('active'),
    }
    _defaults = {
        'default_amount': 0.0,
        'amount_type': 'annual',
        'active': True,
    }
