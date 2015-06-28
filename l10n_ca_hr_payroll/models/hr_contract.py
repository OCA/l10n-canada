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

from itertools import permutations

from openerp.osv import fields, orm


class HrContract(orm.Model):
    _inherit = 'hr.contract'

    def _get_pays_per_year(self, cr, uid, ids, names, arg, context=None):
        """
        :param ids: ID of contract
        :return: The number of pays per year
        """
        res = {}
        schedule_pay = {
            'daily': 365,
            'weekly': 52,
            'bi-weekly': 26,
            'semi-monthly': 24,
            'monthly': 12,
            'bi-monthly': 6,
            'quarterly': 4,
            'semi-annually': 2,
            'annually': 1,
        }
        for contract in self.browse(cr, uid, ids, context):
            if contract.schedule_pay and schedule_pay.get(
                contract.schedule_pay, False
            ):
                res[contract.id] = schedule_pay[contract.schedule_pay]
        return res

    def _get_hourly_rate_from_wage(
        self, cr, uid, ids, field_name, arg=None, context=None
    ):
        """
        :param ids: ID of contract
        :return: The hourly rate computed from the wage of an employee.
        """
        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            res[contract.id] = contract.wage / (
                contract.pays_per_year * contract.worked_hours_per_pay_period
            )
        return res

    _columns = {
        'weeks_of_vacation': fields.float(
            'Number of weeks of vacation',
        ),
        'holidays_entitlement_ids': fields.many2many(
            'hr.holidays.entitlement',
            'hr_contract_holidays_entitlement_rel',
            string='Leave Entitlement Periods',
        ),
        'worked_hours_per_pay_period': fields.float(
            'Worked Hours per Pay Period',
        ),
        'hourly_rate_from_wage': fields.function(
            _get_hourly_rate_from_wage,
            type="float",
            method=True,
            string="Estimated Hourly Rate",
        ),
        'pays_per_year': fields.function(
            _get_pays_per_year,
            method=True,
            string='Pays Per Year',
            type='float',
            readonly=True,
        ),
    }

    _defaults = {
        'weeks_of_vacation': 2,
        'worked_hours_per_pay_period': 40,
    }

    def _check_leave_entitlement(
        self, cr, uid, ids, context=None
    ):
        """
        Check that the employee has maximum one leave entitlement
        per leave type
        """
        for contract in self.browse(cr, uid, ids, context=context):
            for e1, e2 in permutations(contract.holidays_entitlement_ids, 2):
                if e1.leave_id == e2.leave_id:
                    return False

        return True

    _constraints = [
        (
            _check_leave_entitlement,
            "A contract can not have more than one holidays entitlement "
            "per leave type.",
            ['holidays_entitlement_ids']
        ),
    ]

    def get_entitlement(self, cr, uid, ids, leave_type, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1

        contract = self.browse(cr, uid, ids[0], context=context)

        entitlement = next((
            e for e in contract.holidays_entitlement_ids
            if e.leave_id == leave_type), False)

        if not entitlement:
            company = contract.employee_id.company_id
            entitlement = next((
                e for e in company.holidays_entitlement_ids
                if e.leave_id == leave_type), False)

        return entitlement
