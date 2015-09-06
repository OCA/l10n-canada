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


class HrDeductionJurisdiction(orm.Model):
    _name = 'hr.deduction.jurisdiction'
    _description = 'Income Tax Deduction Jurisdiction'
    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'deduction_ids': fields.one2many(
            'hr.deduction.category', 'jurisdiction_id',
            'Deduction Categories',
        ),
    }
