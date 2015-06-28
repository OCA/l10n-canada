# -*- coding:utf-8 -*-#########################################################
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


class HrQcRate(orm.Model):

    _name = 'hr.qc.rate'
    _description = 'Quebec Contribution Rate'

    _columns = {
        'date_from': fields.date(
            'Date From',
            required=True,
        ),
        'date_to': fields.date(
            'Date To',
            required=True,
        ),
        'company_id': fields.many2one(
            'res.company',
            'Company',
            required=True,
        ),
        'rate': fields.float(
            'Rate',
            digits=(2, 2),
            required=True,
            help="Enter 2.5 for a rate of 2.5 %."
        ),
        'type': fields.selection(
            [
                ('csst', 'CSST'),
                ('hsf', 'Health Services Fund'),
            ],
            required=True,
            type='char',
            string='Type',
        ),
    }
