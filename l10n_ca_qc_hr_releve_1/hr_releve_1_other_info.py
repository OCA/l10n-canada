# -*- coding:utf-8 -*-#########################################################
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

from openerp.osv import orm, fields


class hr_releve_1_other_info(orm.Model):
    """
    Used to enter the additional information on Releve 1
    """
    _name = 'hr.releve_1.other_info'
    _description = 'Additional Information on Releve 1'
    _columns = {
        'slip_id': fields.many2one(
            'hr.releve_1',
            required=True,
            ondelete='cascade',
        ),
        'source': fields.many2one(
            'hr.releve_1.other_info.source',
            'Source',
            required=True,
        ),
        'amount': fields.float(
            'Amount',
            digits=(15, 2),
            required=True,
        ),
    }


class hr_releve_1_other_info_source(orm.Model):
    """
    The source of an other information on Releve 1
    """
    _name = 'hr.releve_1.other_info.source'
    _description = 'Additional Information Source on Releve 1'
    _columns = {
        'name': fields.char(
            'Description',
            required=True,
        ),
        'code': fields.char(
            'Code',
            required=True,
            help="Code that appears Releve 1",
        ),
        'is_other_revenue': fields.boolean('Is Other Revenu'),
    }
