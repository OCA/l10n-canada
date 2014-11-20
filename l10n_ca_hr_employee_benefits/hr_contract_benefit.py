# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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
import time


class hr_contract_benefit(orm.Model):
    _name = 'hr.contract.benefit'
    _description = 'Employee Benefit'
    _columns = {
        'name': fields.char(
            'Description',
            required=True
        ),
        'contract_id': fields.many2one(
            'hr.contract',
            'Contract',
            required=True,
            ondelete='cascade',
            select=True
        ),
        'category_id': fields.many2one(
            'hr.benefit.category',
            'Benefit',
            required=True,
            ondelete='cascade',
            select=True
        ),
        'employee_amount': fields.float(
            'Employee Contribution',
            required=True,
        ),
        'employer_amount': fields.float(
            'Employer Contribution',
            required=True,
        ),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date'),
        'periodicity': fields.selection(
            (
                ('each_pay', 'Each Pay'),
                ('annual', 'Annual'),
            ),
            required=True,
            string="Amount Periodicity",
        ),
        'code': fields.related(
            'category_id',
            'code',
            type='char',
            string='Code'
        ),
    }
    _defaults = {
        'date_start': lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        'periodicity': 'each_pay',
    }

    def onchange_category_id(
        self, cr, uid, ids,
        employee_amount=False,
        employer_amount=False,
        name=False,
        category_id=False
    ):
        res = {}
        if category_id:
            category = self.pool.get('hr.benefit.category')
            category = category.browse(cr, uid, category_id)
            res['value'] = {
                'employee_amount': employee_amount or
                category.default_employee_amount,
                'employer_amount': employer_amount or
                category.default_employer_amount,
                'periodicity': category.default_periodicity,
                'name': name or category.name,
            }
        return res
