#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Savoir-faire Linux. All Rights Reserved.
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

from osv import fields, osv

class hr_employee(osv.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
        'tp10153': fields.float('Source Deductions Return (TP-1015.3)', digits=(16,2), required=True, help="Source Deductions Return"),
            }

    _defaults = {
        'tp10153': 11195.00,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
