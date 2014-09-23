# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Amura Consulting. All Rights Reserved.
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
import time


class hr_contract_benefit(orm.Model):
    _name = 'hr.contract.benefit'
    _description = 'The benefits in an employee contract'
    _columns = {
        'name': fields.char(
            'Deduction Name',
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
        'amount': fields.float(
            'Employee Contribution',
            required=True,
            help="""\
Enter the amount that you would pay for a complete year,
even if the duration is lower that a year.""",
        ),
        'er_amount': fields.float(
            'Employer Contribution',
            required=True,
            help="""\
Enter the amount that you would pay for a complete year,
even if the duration is lower that a year.""",
        ),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date'),
        'is_annual': fields.boolean(
            'Annual',
            help="""\
True if the entered amounts of contribution for employee and
employer are annual, False if they are entered for the period."""
        ),
        'ei_exempt': fields.related(
            'category_id',
            'ei_exempt',
            type='char',
            string='EI Exempt'
        ),
        'fit_exempt': fields.related(
            'category_id',
            'fit_exempt',
            type='char',
            string='FIT Exempt'
        ),
        'code': fields.related(
            'category_id',
            'code',
            type='char',
            string='Code'
        ),
    }
    _defaults = {
        'amount': 0,
        'er_amount': 0,
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'is_annual': True,
    }

    def onchange_category_id(self, cr, uid, ids, category_id=False):
        res = {'value': {'amount': 0.0}}
        if category_id:
            category = self.pool.get('hr.benefit.category')
            category = category.browse(cr, uid, category_id)
            res['value']['amount'] = category.default_amount
            res['value']['er_amount'] = category.default_er_amount
            res['value']['name'] = category.name
        return res
