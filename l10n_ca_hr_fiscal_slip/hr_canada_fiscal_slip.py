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
from openerp.tools.translate import _
import time


def get_states(self, cr, uid, context=None):
    return [
        ('draft', _('Draft')),
        ('confirmed', _('Confirmed')),
        ('sent', _('Sent')),
    ]


class hr_canada_fiscal_slip(orm.Model):
    """
    This model contains every standard fields on an employee's fiscal slip
    in Canada
    """
    _name = 'hr.canada.fiscal_slip'
    _description = 'Canada Fiscal Slip'

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
        'nas': fields.related(
            'employee_id',
            'nas',
            string='Social Insurance Number',
            type="float",
            digits=(9, 0),
        ),
        'reference': fields.char(
            'Reference',
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
            get_states,
            'Status',
            select=True,
            required=True,
        ),
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True,
        ),
        'street': fields.related(
            'address_home_id',
            'street',
            string='Address Line 1',
            type="char",
            size=30,
        ),
        'street2': fields.related(
            'address_home_id',
            'street2',
            string='Address Line 2',
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
    }

    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, context:
        self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id,
        'year': lambda *a: int(time.strftime(
            DEFAULT_SERVER_DATE_FORMAT)[0:4]) - 1,
    }
