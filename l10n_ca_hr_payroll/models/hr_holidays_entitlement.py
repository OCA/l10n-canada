# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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

from openerp.osv import orm, fields


class HrHolidaysEntitlement(orm.Model):
    """
    In Canada, most legislations define entilement periods for vacations.
    The rules are different from a province to another.

    These rules define when the employee is allowed to take his vacations
    and/or to receive the related allowance if he does not take them.
    """
    _name = 'hr.holidays.entitlement'
    _description = 'Holidays Entitlement'

    _columns = {
        'name': fields.char('Name', required=True),
        'month_start': fields.selection(
            [
                ('1', 'January'),
                ('2', 'February'),
                ('3', 'March'),
                ('4', 'April'),
                ('5', 'May'),
                ('6', 'June'),
                ('7', 'July'),
                ('8', 'August'),
                ('9', 'September'),
                ('10', 'October'),
                ('11', 'November'),
                ('12', 'December'),
            ], required=True, type='char', string='Month Start'),
        'day_start': fields.integer('Day Start', required=True),
        'leave_id': fields.many2one(
            'hr.holidays.status',
            'Leave Type',
            required=True,
        ),
    }

    _defaults = {
        'month_start': '1',
        'day_start': 1,
    }
