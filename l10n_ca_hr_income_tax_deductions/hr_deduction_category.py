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


def get_jurisdiction(self, cursor, user_id, context=None):
    return (
        ('federal', 'Federal'),
        ('provincial', 'Provincial'))


class hr_deduction_category(orm.Model):
    _name = 'hr.deduction.category'
    _description = 'Categories of employee deductions used for salary rules'
    _columns = {
        'name': fields.char('Category Name', required=True),
        'code': fields.char('Code', required=True, help="""\
The code that can be used in the salary rules to identify thededuction"""),
        'description': fields.text(
            'Description',
            required=True,
            help="""\
Brief explanation of which benefits the category contains."""),
        'default_amount': fields.float('Default Amount', required=True),
        'jurisdiction': fields.selection(
            get_jurisdiction,
            'Jurisdiction',
            required=True
        ),
        'note': fields.text('Note'),
    }
    _defaults = {
        'default_amount': 0.0,
        'jurisdiction': 'federal',
    }
