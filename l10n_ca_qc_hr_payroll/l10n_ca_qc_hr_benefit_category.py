# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 - 2014 Savoir-faire Linux. All Rights Reserved.
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
    _inherit = 'hr.benefit.category'
    _columns = {
        'qpp_exempt': fields.boolean(
            'QPP Exempt',
            help="Exemption from Quebec Pension Plan"
        ),
        'qpip_exempt': fields.boolean(
            'QPIP Exempt',
            help="Exemption from Quebec Parental Insurance Plan"
        ),
        'qit_exempt': fields.boolean(
            'QIT Exempt',
            help="Exemption from Quebec Income Tax"
        ),
    }
    _defaults = {
        'qpp_exempt': False,
        'qpip_exempt': False,
        'qit_exempt': False,
    }
