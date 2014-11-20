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


class hr_benefit_category(orm.Model):
    _name = 'hr.benefit.category'
    _description = 'Category of employee benefits'
    _columns = {
        'name': fields.char('Benefit Name', required=True),
        'code': fields.char('Code', required=True, help="""\
The code that can be used in the salary rules to identify the benefit"""),
        'description': fields.text(
            'Description',
            required=True,
            help="Brief explanation of which benefits the category contains."
        ),
        'default_employee_amount': fields.float(
            'Default Employee Contribution',
            required=True,
        ),
        'default_employer_amount': fields.float(
            'Default Employer Contribution',
            required=True,
        ),
        'default_periodicity': fields.selection(
            (
                ('each_pay', 'Each Pay'),
                ('annual', 'Annual'),
            ),
            required=True,
            string="Default Amount Periodicity",
        ),
        'ei_exempt': fields.boolean('Employment Insurance Exempt'),
        'fit_exempt': fields.boolean('Federal Income Tax Exempt'),
        'cpp_exempt': fields.boolean('CPP/QPP Exempt'),
        'pip_exempt': fields.boolean('Parental Insurance Plan Exempt'),
        'pit_exempt': fields.boolean('Provincial Income Tax Exempt'),
    }
