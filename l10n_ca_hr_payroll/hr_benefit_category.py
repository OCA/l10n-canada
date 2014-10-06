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


class hr_benefit_category(orm.Model):
    _name = 'hr.benefit.category'
    _description = 'Categories of employee benefits'
    _columns = {
        'name': fields.char('Benefit Name', required=True),
        'code': fields.char('Code', required=True, help="""\
The code that can be used in the salary rules to identify the benefit"""),
        'description': fields.text(
            'Description',
            required=True,
            help="Brief explanation of which benefits the category contains."
        ),
        'is_cash': fields.boolean('Is Cash', help="""\
True if the benefit is paid in cash to the employee,
False if paid in Kind."""),
        'default_amount': fields.float(
            'Default Employee Contribution',
            required=True,
            help="""\
Default annual amount that the employee contributes"""
        ),
        'default_er_amount': fields.float(
            'Default Employer Contribution',
            required=True,
            help="Default annual amount that the employer contributes"
        ),
        'ei_exempt': fields.boolean('EI Exempt'),
        'fit_exempt': fields.boolean('FIT Exempt'),
    }
    _defaults = {
        'is_cash': True,
        'default_amount': 0.0,
        'ei_exempt': False,
        'fit_exempt': False,
    }
