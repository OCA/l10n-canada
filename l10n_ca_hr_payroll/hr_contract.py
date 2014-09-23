# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Amura Consulting. All Rights Reserved.
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
import datetime
strptime = datetime.datetime.strptime


class hr_contract(orm.Model):
    _inherit = 'hr.contract'

    def _get_pays_per_year(self, cr, uid, ids, names, arg, context=None):
        """
        @param ids: ID of contract
        @return: The number of pays per year
        """
        res = {}
        # FIXME: Should likely pull these values from somewhere else,
        # depending on whether a 52 or 53 year week is used
        schedule_pay = {
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

    _columns = {
        'pays_per_year': fields.function(
            _get_pays_per_year, method=True, string='Pays Per Year',
            type='float', readonly=True,
        ),
        'weeks_of_vacation': fields.integer(
            'Number of weeks of vacation',
            required=True
        ),
        'benefit_line_ids': fields.one2many(
            'hr.contract.benefit',
            'contract_id',
            'Employee Benefits'
        ),
    }

    _defaults = {
        'weeks_of_vacation': 2,
    }

    def sum_benefits(
        self, cr, uid, ids, contract_id, date_from, date_to,
        exemption=False, benefit_code=False, employer=False,
        annual=True, pays_per_year=False, context=None
    ):

        # convert string dates to date objects
        payslip_from = strptime(date_from, "%Y-%m-%d").date()
        payslip_to = strptime(date_to, "%Y-%m-%d").date()

        payslip_duration = (payslip_to - payslip_from).days + 1

        contract = self.read(
            cr, uid, contract_id,
            ['benefit_line_ids'],
            context
        )
        benefit_ids = contract['benefit_line_ids']

        attrs = [
            'code', 'amount', 'er_amount', 'category_id',
            'date_start', 'date_end', 'is_annual'
        ]
        if exemption:
            attrs.append(exemption)

        benefits = self.pool.get(
            'hr.contract.benefit'
        ).read(
            cr, uid, benefit_ids, attrs, context
        )

        res = 0
        for b in benefits:
            if (not exemption or not b[exemption]) and (
                not benefit_code or b['code'] == benefit_code
            ):

                # convert string dates to date objects
                b['date_start'] = strptime(b['date_start'], "%Y-%m-%d").date()
                b['date_end'] = b['date_end'] and \
                    strptime(b['date_end'], "%Y-%m-%d").date()

                amount = employer and b['er_amount'] or b['amount']

                # some calculations need annual benefit amounts,
                # other need the periodic amount
                # benefits can have an annual amount or a periodic amount
                if annual and not b['is_annual']:
                    amount = pays_per_year * amount
                elif not annual and b['is_annual']:
                    amount = amount / pays_per_year

                # Ponderate the amount of benefit in regard
                # to the payslip dates
                if b['is_annual']:
                    start_offset = max(
                        (b['date_start'] - payslip_from).days,
                        0
                    )
                    end_offset = b['date_end'] and \
                        max((payslip_to - b['date_end']).days, 0) or 0
                else:
                    start_offset = max(
                        (payslip_from - b['date_start']).days,
                        0
                    )
                    end_offset = max((b['date_end'] - payslip_to).days, 0)

                ratio = 1 - (start_offset + end_offset) / payslip_duration
                amount = amount * ratio

                res += amount

        return res

    _defaults = {
    }
