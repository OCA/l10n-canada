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


class HrPayslipWorkedDays(orm.Model):
    _inherit = 'hr.payslip.worked_days'

    _columns = {
        # These fields are not used for the canadian payroll
        # so we make them not required and remove them from the payslip view
        'name': fields.char('Description'),
        'code': fields.char(
            'Code',
            help="The code that can be used in the salary rules"),

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

    def onchange_activity_id(
        self, cr, uid, ids,
        date_from, date_to,
        activity_id, contract_id,
        context=None
    ):
        if(
            not contract_id
            or not activity_id
            or not date_from
            or not date_to
        ):
            return {}

        contract = self.pool['hr.contract'].browse(
            cr, uid, contract_id, context=context
        )

        activity = self.pool['hr.activity'].browse(
            cr, uid, activity_id, context=context
        )

        if contract.salary_computation_method == 'wage':
            if (
                activity.type != 'leave'
                or activity.leave_id.paid_leave
            ):
                hourly_rate = contract.hourly_rate_from_wage
            else:
                hourly_rate = 0

        else:
            if activity.type == 'job':
                hourly_rate = self.pool['hr.contract'].get_job_hourly_rate(
                    cr, uid,
                    date_from, date_to,
                    contract.id,
                    job_id=activity.job_id.id,
                    context=context
                )

            elif activity.type == 'leave' and activity.leave_id.paid_leave \
                    or activity.type != 'leave':
                hourly_rate = self.pool['hr.contract'].get_job_hourly_rate(
                    cr, uid,
                    date_from, date_to,
                    contract.id,
                    main_job=True,
                    context=context
                )
            else:
                hourly_rate = 0

        return {'value': {'hourly_rate': hourly_rate}}
