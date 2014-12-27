# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import time


class hr_canada_fiscal_slip(orm.Model):
    """
    This model contains every standard fields on an employee's fiscal slip
    in Canada
    """
    _name = 'hr.canada.fiscal_slip'
    _description = 'A canada fiscal slip of an employee'

    _columns = {
        'company_id': fields.many2one(
            'res.company',
            'Company',
            required=True,
        ),
        'address_home_id': fields.related(
            'employee_id',
            'address_home_id',
            string='Home Address',
            type="many2one",
            relation="res.partner",
        ),
        'sin': fields.related(
            'employee_id',
            'sin',
            string='Social Security Number',
            type="float",
            digits=(9, 0),
        ),
        'reference': fields.char(
            'Reference'
        ),
        'no_employee': fields.related(
            'employee_id',
            'employee_number',
            string='Employee Number',
            type="char",
        ),
        'lastname': fields.related(
            'employee_id',
            'lastname',
            string='Last Name',
            type="char",
        ),
        'firstname': fields.related(
            'employee_id',
            'firstname',
            string='First Name',
            type="char",
        ),
        'initial': fields.related(
            'employee_id',
            'lastname_initial',
            string='Last Name Initial',
            type="char",
        ),
        'year': fields.integer(
            'Fiscal Year',
            required=True,
        ),
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('confirmed', 'Confirmed'),
                ('sent', 'Sent'),
                ('cancel', 'Cancelled'),
            ],
            'Status',
            select=True,
            readonly=True,
        ),
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True,
        ),
        'street': fields.related(
            'address_home_id',
            'street',
            string='Adress Line 1',
            type="char",
            size=30,
        ),
        'street2': fields.related(
            'address_home_id',
            'street2',
            string='Adress Line 2',
            type="char",
            size=30,
        ),
        'city': fields.related(
            'address_home_id',
            'city',
            string='City',
            type="char",
        ),
        'state_id': fields.related(
            'address_home_id',
            'state_id',
            type="many2one",
            relation="res.country.state",
            string='Province',
        ),
        'zip': fields.related(
            'address_home_id',
            'zip',
            string='Zip',
            type="char",
        ),
        'country_id': fields.related(
            'address_home_id',
            'country_id',
            string='Country',
            type="many2one",
            relation="res.country",
        ),
        'type': fields.selection(
            [
                ('O', 'Original'),
                ('A', 'Amended'),
                ('C', 'Cancel'),
            ],
            'Type',
            required=True,
        ),
    }

    _defaults = {
        'state': 'draft',
        'type': 'O',
        'company_id': lambda self, cr, uid, context:
        self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id,
        'year': lambda *a: int(time.strftime(
            DEFAULT_SERVER_DATE_FORMAT)[0:4]) - 1,
    }
