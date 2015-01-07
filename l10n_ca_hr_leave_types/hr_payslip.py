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

from openerp.osv import orm
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import itertools
strptime = datetime.strptime
strftime = datetime.strftime


class hr_payslip(orm.Model):
    _inherit = 'hr.payslip'

    def sum_leave_category(
        self, cr, uid, ids,
        payslip,
        leave_code,
        multiply_by_rate=False,
        context=None
    ):
        """
        Used in salary rules to sum leave hours from worked_days
        e.g. sum over the hours of vacation (leave_code == 'VAC')

        returns the amount of allowance requested by the employee
        in hours or in cash (multiply_by_rate=True)

        payslip: a payslip BrowsableObject (not a browse record)

            It is only used to get the ids of the worked days.

            Should not be used to sum over the worked days because these
            may change during the payslip computation process.

            No worked days should be added or deleted during the
            payslip computation process, so the worked days ids
            always remain the same.
        """
        res = 0

        if payslip.worked_days_line_ids:
            worked_days_line_ids = [
                wd.id for wd in payslip.worked_days_line_ids
            ]

            worked_days = self.pool['hr.payslip.worked_days'].browse(
                cr, uid, worked_days_line_ids, context=context)

            for wd in worked_days:
                if(
                    wd.activity_id.type == 'leave'
                    and wd.activity_id.code == leave_code
                ):
                    # Case where we need only the number of hours
                    if not multiply_by_rate:
                        res += wd.number_of_hours
                    else:
                        res += wd.total

        return res

    def get_public_holidays(
        self, cr, uid, ids,
        date_from,
        date_to,
        country_code,
        state_code=False,
        context=None
    ):
        """
        This function counts the number of public holidays within
        a period (date_from, date_to) for a country (most likely Canada)
        and a state.

        If state_code is False, every public holidays within a period
        will be summed.
        """
        leave_obj = self.pool['hr.holidays.public']

        # Get the country id.
        country_id = self.pool['res.country'].search(
            cr, uid, [('code', '=', country_code)], context=context)

        # Get the legal leaves for the given country
        legal_leave_ids = leave_obj.search(
            cr, uid,
            [
                ('year', 'in', list({date_from[0:4], date_to[0:4]})),
                ('country_id', 'in', country_id)
            ], context=context)

        legal_leaves = leave_obj.browse(
            cr, uid, legal_leave_ids, context=context)

        if not legal_leaves:
            return []

        # Get all legal leave lines
        legal_leaves = list(itertools.chain(*[
            leave.line_ids for leave in legal_leaves
        ]))

        # Province code could be a US state code if country_code='US'
        if state_code:
            legal_leaves = [
                leave for leave in legal_leaves
                if state_code in [state.code for state in leave.state_ids]
            ]

        # Filter by date
        legal_leaves = [
            leave for leave in legal_leaves
            if date_from <= leave.date <= date_to
        ]

        return legal_leaves

    def reduce_leave_hours(
        self, cr, uid, ids,
        payslip,
        leave_code,
        reduction,
        divide_by_rate=False,
        context=None
    ):
        """
        When the leave hours computed in worked days are greater than the
        available hours from the employee's leave accrual, this method
        is called to reduce the worked days lines related to the leave type.
        """

        # To avoid integers as parameter to mess up with divisions
        reduction = float(reduction)

        # Get the list of worked days in payslip related to the
        # leave type ordered by date desc
        worked_days_line_ids = [
            wd.id for wd in payslip.worked_days_line_ids
            if wd.activity_id.type == 'leave'
            and wd.activity_id.code == leave_code
        ]

        leaves = self.pool['hr.payslip.worked_days'].browse(
            cr, uid, worked_days_line_ids, context=context)

        leaves.sort(key=lambda wd: wd.date_from)
        leaves.reverse()

        for wd in leaves:
            # Apply reductions to worked days until the total reduction
            # has been made
            if reduction == 0:
                break

            # divide_by_rate is True if the given reduction in parameter
            # is given in cash and False if given in hours
            current_reduction = divide_by_rate \
                and reduction / (wd.hourly_rate * wd.rate / 100) \
                or reduction

            # Get the maximum of reduction of the current worked day
            current_reduction = min(wd.number_of_hours, current_reduction)
            current_reduction = max(current_reduction, 0)

            # Apply the reduction to the worked days line
            number_of_hours = wd.number_of_hours - current_reduction
            self.pool['hr.payslip.worked_days'].write(
                cr, uid, [wd.id],
                {'number_of_hours': number_of_hours},
                context=context)

            # substract the amount reduced before next iteration
            reduction -= divide_by_rate \
                and current_reduction * wd.hourly_rate * wd.rate / 100 \
                or current_reduction

    def reduce_payslip_input_amount(
        self, cr, uid, ids,
        payslip,
        input_types,
        reduction,
        context=None
    ):
        """
        When unused leaves requested are lower that those available,
        reduce the related inputs
        """

        input_line_ids = [
            input_line.id for input_line in payslip.input_line_ids
            if input_line.type == input_types
        ]

        input_lines = self.pool['hr.payslip.input'].browse(
            cr, uid, input_line_ids, context=context)

        for input_line in input_lines:
            if reduction == 0:
                break

            if input_line.type == input_types:

                current_reduction = min(input_line.amount, reduction)
                new_amount = input_line.amount - current_reduction

                self.pool['hr.payslip.input'].write(
                    cr, uid, [input_line.id], {'amount': new_amount},
                    context=context)

                reduction = reduction - current_reduction

    def get_4_weeks_of_gross(
        self, cr, uid, ids,
        current_payslip,
        employee_id,
        contract_id,
        leave_date,
        context=None
    ):
        """
        Get the gross salary of an employee within the 4 weeks that
        preceded a public holiday (leave_date).

        The end of the 4 week period depends on the employee's
        week start on contract.

        This method is called by a payslip BrowsableObject. It
        must be included in the computation.
        """
        current_contract = self.pool['hr.contract'].browse(
            cr, uid, contract_id, context=context)

        # Get the number of days passed in the current week
        leave_day = strptime(leave_date, DEFAULT_SERVER_DATE_FORMAT)
        leave_weekday_num = int(strftime(leave_day, '%w'))

        week_start_day_num = int(current_contract.week_start)

        if week_start_day_num > leave_weekday_num:
            week_start_day_num -= 7

        weekdays_passed = leave_weekday_num - week_start_day_num

        # Get the last day of the week that precedes the leave day
        period_end = (
            leave_day.date() - timedelta(days=(weekdays_passed + 1))
        )

        # The periode start is 4 weeks before the period end
        period_start = (
            period_end - timedelta(days=27)
        ).strftime(DEFAULT_SERVER_DATE_FORMAT)

        period_end = period_end.strftime(DEFAULT_SERVER_DATE_FORMAT)

        # Get the payslips that may contain worked days related
        # to the 4 weeks of work
        payslip_ids = self.search(
            cr, uid,
            [
                ('employee_id', '=', employee_id),
                ('date_from', '<=', period_end),
                ('date_to', '>=', period_start),
                ('state', '=', 'done'),
            ]
        )

        payslips = self.browse(cr, uid, payslip_ids, context=context)

        total = 0
        for payslip in payslips:
            worked_days_ids = [wd.id for wd in payslip.worked_days_line_ids]
            res = self._sum_worked_days(
                cr, uid,
                worked_days_ids,
                period_start, period_end,
                context=context)
            total += res

        # Need to add the worked days in the current payslip
        # because they may match the 4 weeks period
        if current_payslip.worked_days_line_ids:
            current_wd_ids = [
                wd.id for wd in current_payslip.worked_days_line_ids
            ]
            res = self._sum_worked_days(
                cr, uid,
                current_wd_ids,
                period_start, period_end,
                context=context)
            total += res

        return round(total, 2)

    def _sum_worked_days(
        self, cr, uid,
        worked_days_ids,
        period_start, period_end,
        context=None
    ):
        """
        Sum over the worked days and filter by an interval of time.

        If a given worked days record overlaps the interval,
        a ratio is multiplied to the result so that the result
        matches the covered period.

        Returns an amount in cash
        """
        worked_days = self.pool['hr.payslip.worked_days'].browse(
            cr, uid, worked_days_ids, context=context)

        res = 0

        for wd in worked_days:
            # if wd is from a refund payslip
            # multiply the amount by -1
            is_refund = wd.payslip_id.credit_note and -1 or 1

            # Normal case where worked days record is 100% included
            # in the given interval
            if period_start <= wd.date_from and \
                    wd.date_to <= period_end:
                ratio = 1

            # Case where the worked days record partially overlaps the given
            # interval
            elif(
                wd.date_from <= period_start <= wd.date_to
                or wd.date_from <= period_end <= wd.date_to
            ):
                # Case where the worked days begin after the period start
                period_date_start = strptime(
                    period_start, DEFAULT_SERVER_DATE_FORMAT).date()
                wd_date_start = strptime(
                    wd.date_from, DEFAULT_SERVER_DATE_FORMAT).date()
                start_offset = max((period_date_start - wd_date_start).days, 0)

                # Case where the worked days begin after the period start
                period_date_end = strptime(
                    period_end, DEFAULT_SERVER_DATE_FORMAT).date()
                wd_date_to = strptime(
                    wd.date_to, DEFAULT_SERVER_DATE_FORMAT).date()
                end_offset = max((wd_date_to - period_date_end).days, 0)

                wd_duration = \
                    (wd_date_to - wd_date_start).days + 1

                ratio = 1 - float(start_offset + end_offset) / wd_duration
            else:
                ratio = 0

            res += wd.total * ratio * is_refund

        return res
