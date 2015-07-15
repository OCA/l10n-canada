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

from itertools import chain
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

strptime = datetime.strptime
strftime = datetime.strftime

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class One2ManyMod2(fields.one2many):
    """
    Get only the lines with amounts that are not equal to 0
    """
    def get(
        self, cr, obj, ids, name,
        user=None, offset=0, context=None, values=None
    ):
        if context is None:
            context = {}

        if not values:
            values = {}
        res = {}

        for payslip in obj.browse(cr, user, ids, context=context):
            res[payslip.id] = [
                line.id for line
                in payslip.details_by_salary_rule_category
                if line.total and line.appears_on_payslip
            ]

        return res


class HrPayslip(orm.Model):
    _inherit = 'hr.payslip'

    _columns = {
        'line_ids': One2ManyMod2(
            'hr.payslip.line', 'slip_id', 'Payslip Lines',
            readonly=True, states={'draft': [('readonly', False)]}),
    }

    def compute_sheet(self, cr, uid, ids, context=None):
        self.check_employee_data(cr, uid, ids, context=context)
        super(HrPayslip, self).compute_sheet(
            cr, uid, ids, context=context)

    def check_employee_data(self, cr, uid, ids, context=None):
        """
        Check that no standard information is missing on the
        employee record. This prevents errors from being raised
        from salary rules.
        """
        employee_ids = [
            slip.employee_id.id for slip in
            self.browse(cr, uid, ids, context=context)
        ]
        self.pool['hr.employee'].check_personal_info(
            cr, uid, employee_ids, context=context)

    def get_payslip(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1, "Expected single record"

        return self.browse(cr, uid, ids[0], context=context)

    def ytd_amount(
        self, cr, uid, ids, code, context=None
    ):
        payslip = self.get_payslip(cr, uid, ids, context=context)
        date_slip = datetime.strptime(
            payslip.date_payment, DEFAULT_SERVER_DATE_FORMAT)

        date_from = datetime(date_slip.year - 1, 12, 31).strftime(
            DEFAULT_SERVER_DATE_FORMAT)

        date_to = (
            datetime(date_slip.year, date_slip.month, date_slip.day) -
            relativedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)

        line_obj = self.pool['hr.payslip.line']

        line_ids = line_obj.search(cr, uid, [
            ('slip_id.state', '=', 'done'),
            ('slip_id.date_payment', '>', date_from),
            ('slip_id.date_payment', '<', date_to),
            ('code', '=', code),
        ])

        lines = line_obj.browse(cr, uid, line_ids, context=context)

        return sum(
            -l.total if l.slip_id.credit_note else l.total
            for l in lines)

    def get_pays_since_beginning(
        self, cr, uid, ids, pays_per_year, context=None
    ):
        """
        Get the number of pay periods since the beginning of the year.
        """
        payslip = self.get_payslip(cr, uid, ids, context=context)

        date_from = datetime.strptime(
            payslip.date_from, DEFAULT_SERVER_DATE_FORMAT).date()

        year_start = datetime(date_from.year, 1, 1).date()
        year_end = datetime(date_from.year, 12, 31).date()

        days_past = float((date_from - year_start).days)
        days_total = (year_end - year_start).days

        return round((days_past / days_total) * pays_per_year, 0) + 1

    def count_unpaid_leaves(
        self, cr, uid, ids, context=None
    ):
        """
        Count unpaid leaves in worked days for a given payslip
        """
        payslip = self.get_payslip(cr, uid, ids, context=context)

        res = 0

        for wd in payslip.worked_days_line_ids:
            activity = wd.activity_id
            if activity.type == 'leave' and not activity.leave_id.paid_leave:
                res += wd.number_of_hours

        return res

    def count_paid_worked_days(
        self, cr, uid, ids, in_cash=False, context=None
    ):
        """
        Count paid worked days for a given payslip
        :param in_cash: multiply hours by rate for overtime
        """
        payslip = self.get_payslip(cr, uid, ids, context=context)

        res = 0

        for wd in payslip.worked_days_line_ids:
            activity = wd.activity_id
            if activity.type != 'leave' or activity.leave_id.paid_leave:
                res += (
                    wd.number_of_hours * wd.hourly_rate * wd.rate / 100
                    if in_cash else wd.number_of_hours
                )

        return res

    def get_job_hourly_rate(
        self, cr, uid, ids, date_from, date_to,
        contract_id, job_id=False, main_job=False, context=None
    ):
        """
        Method that allows to access get_job_hourly_rate method
        from a payslip BrowsableObject.

        It is not possible to call it from a contract BrowsableObject
        because it passes the parameter ids automatically.
        """
        return self.pool['hr.contract'].get_job_hourly_rate(
            cr, uid, date_from, date_to, contract_id,
            job_id=job_id, main_job=main_job, context=context)

    def _check_max_leave_hours(
        self, cr, uid, ids, context=None
    ):
        """
        Check that the number of leave hours computed is lesser than
        the number of worked hours per pay period if the employee is paid
        by wage.
        """
        for payslip in self.browse(cr, uid, ids, context=context):
            if payslip.contract_id.salary_computation_method == 'wage':

                leave_hours = 0
                for wd in payslip.worked_days_line_ids:
                    if wd.activity_id.type == 'leave':
                        leave_hours += wd.number_of_hours

                if leave_hours > payslip.contract_id.\
                        worked_hours_per_pay_period:
                    return False

        return True

    _constraints = [
        (
            _check_max_leave_hours,
            "The leave hours taken by the employee must be lower or equal "
            "to the number of worked hours per pay period on the contract.",
            ['worked_days_line_ids']
        ),
    ]

    def get_public_holidays(self, cr, uid, ids, context=None):
        """
        Return a list of public holidays for the payslip's period
        """
        payslip = self.get_payslip(cr, uid, ids, context=context)

        # Use the working address to determine the country of the
        # leave accruals
        address = payslip.employee_id.address_id

        leave_obj = self.pool['hr.holidays.public.line']

        # Get the public holidays for the given country
        public_holidays_ids = leave_obj.search(cr, uid, [
            ('date', '>=', payslip.date_from),
            ('date', '<=', payslip.date_to),
            '|',
            ('holidays_id.country_id', '=', address.country_id.id),
            ('holidays_id.country_id', '=', False),
            '|',
            ('state_ids', '=', address.state_id.id),
            ('state_ids', '=', False),
        ], context=context)

        return leave_obj.browse(cr, uid, public_holidays_ids, context=context)

    def get_4_weeks_of_gross(
        self, cr, uid, ids, leave_date, context=None
    ):
        """
        Get the gross salary of an employee within the 4 weeks that
        preceded a public holiday (leave_date).

        The end of the 4 week period depends on the employee's
        week start on contract.
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1, "Expected single record"

        payslip = self.browse(cr, uid, ids[0], context=context)

        # Get the number of days passed in the current week
        leave_day = strptime(leave_date, DEFAULT_SERVER_DATE_FORMAT)
        leave_weekday_num = int(strftime(leave_day, '%w'))

        week_start_day_num = int(
            payslip.contract_id.employee_id.company_id.week_start)

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
                ('employee_id', '=', payslip.employee_id.id),
                ('date_from', '<=', period_end),
                ('date_to', '>=', period_start),
                ('state', '=', 'done'),
            ]
        )

        # Need to add the worked days in the current payslip
        # because they may match the 4 weeks period
        payslip_ids.append(payslip.id)

        payslips = self.browse(cr, uid, payslip_ids, context=context)

        worked_days_ids = [
            wd.id for wd in list(chain(*[
                p.worked_days_line_ids for p in payslips
            ]))
        ]

        return self._sum_worked_days(
            cr, uid, worked_days_ids, period_start, period_end, context=context
        )

    def _sum_worked_days(
        self, cr, uid,
        worked_days_ids, period_start, period_end, context=None
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

        return round(res, 2)
