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

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import datetime
strptime = datetime.datetime.strptime


class hr_contract(orm.Model):
    _inherit = 'hr.contract'

    _columns = {
        'benefit_line_ids': fields.one2many(
            'hr.contract.benefit',
            'contract_id',
            'Employee Benefits'
        ),
    }

    def sum_benefits(
        self, cr, uid, ids,
        contract_id, date_from, date_to, grossp,
        exemption=False, benefit_codes=False, employer=False,
        annual=True, pays_per_year=False, context=None
    ):
        """
        Sums over the benefits in an employee contract

        This function is meant to be used in salary rules

        Parameters
        ==========
        exemption:  Filter benefits for those that are not
                    exempted from a source deduction

        benefit_codes: The type of benefit over which to sum

        employer:   If True, sum over the employer contribution.
                    If False, sum over the employee contribution

        annual:     If true, return an annual amount
                    If false, return a periodic amount

        pays_per_year: The number of pays per year for the employee
        """
        # convert string dates to date objects
        payslip_from = strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).date()
        payslip_to = strptime(date_to, DEFAULT_SERVER_DATE_FORMAT).date()
        payslip_duration = (payslip_to - payslip_from).days + 1

        contract = self.browse(cr, uid, contract_id, context=context)

        # Allow to pass a single code string or a list of codes in argument
        if benefit_codes and not isinstance(benefit_codes, list):
            benefit_codes = [benefit_codes]

        res = 0
        for b in contract.benefit_line_ids:
            if(
                (not exemption or not b.category_id[exemption]) and
                (not benefit_codes or b.code in benefit_codes)
            ):
                amount = employer and b.employer_amount or b.employee_amount

                # If the amount type is percentage, we multiply it by the gross
                # salary for the period given in parameter
                if b.amount_type == 'percent':
                    amount = amount * grossp / 100

                # Case where the kind of amount requested by the salary rule
                # is different the amount computed in the benefit record
                if annual and b.amount_type in ['each_pay', 'percent']:
                    amount = pays_per_year * amount
                elif not annual and b.amount_type == 'annual':
                    amount = float(amount) / pays_per_year

                # Case where the deduction begins after the payslip period
                # begins.
                date_start = strptime(
                    b.date_start,
                    DEFAULT_SERVER_DATE_FORMAT
                ).date()
                start_offset = max(
                    (date_start - payslip_from).days,
                    0
                )

                # Case where the deduction ends before the payslip period
                # ends.
                date_end = b.date_end and \
                    strptime(
                        b.date_end,
                        DEFAULT_SERVER_DATE_FORMAT
                    ).date() or False
                end_offset = date_end and \
                    max((payslip_to - date_end).days, 0) or 0

                ratio = 1 - float(start_offset + end_offset) / payslip_duration
                amount = amount * ratio

                res += amount

        return res

    _defaults = {
    }
