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


class hr_employee(orm.Model):
    _inherit = 'hr.employee'

    def _get_nas_from_address(
        self, cr, uid, ids, field_name, arg=None, context=None
    ):
        res = {}
        for employee in self.browse(cr, uid, ids, context=context):
            if employee.address_home_id:
                res[employee.id] = employee.address_home_id.nas
            else:
                res[employee.id] = False
        return res

    _columns = {
        # The two following fields are not mandatory in fiscal slips.
        # They must exist in the employee model so that the slips will
        # compute properly.
        # TODO: hr modules that would implement these fields
        'employee_number': fields.char(
            'Employee Number',
        ),
        'lastname_initial': fields.char(
            'Last Name initial',
            size=1
        ),

        'nas': fields.function(
            _get_nas_from_address,
            method=True,
            string='Social Insurance Number',
            type="float",
            digits=(9, 0),
        ),
    }
