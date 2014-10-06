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


class hr_contract_benefit(orm.Model):
    _inherit = 'hr.contract.benefit'
    _columns = {
        'qpp_exempt': fields.related(
            'category_id', 'qpp_exempt',
            type='char', string='QPP Exempt'
        ),
        'qpip_exempt': fields.related(
            'category_id', 'qpip_exempt',
            type='char', string='QPIP Exempt'
        ),
        'qit_exempt': fields.related(
            'category_id', 'qit_exempt',
            type='char', string='QIT Exempt'
        ),
        'fss_exempt': fields.related(
            'category_id', 'fss_exempt',
            type='char', string='FSS Exempt'
        ),
        'cnt_exempt': fields.related(
            'category_id', 'cnt_exempt',
            type='char', string='CNT Exempt'
        ),
        'csst_exempt': fields.related(
            'category_id', 'csst_exempt',
            type='char', string='CSST Exempt'
        ),
    }
