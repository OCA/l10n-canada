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

from openerp.osv import orm, fields


class hr_payslip_worked_days(orm.Model):
    _inherit = 'hr.payslip.worked_days'

    _columns = {
        # Make contract on worked_days related to the contract payslip
        'contract_id': fields.related(
            'payslip_id',
            'contract_id',
            type='many2one',
            relation='hr.contract',
            string='Contract',
        ),
    }

    _order = 'date_from,activity_id'
