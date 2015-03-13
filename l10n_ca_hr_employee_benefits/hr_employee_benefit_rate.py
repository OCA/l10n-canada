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

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from itertools import permutations
from datetime import datetime
strptime = datetime.strptime


def get_amount_types(cr, uid, ids, context=None):
    return [
        ('each_pay', 'Each Pay'),
        ('annual', 'Annual'),
        ('percent_gross', 'Percentage of Gross Salary'),
        ('per_hour', 'Amount Per Worked Hour'),
    ]


class hr_employee_benefit_rate(orm.Model):
    _name = 'hr.employee.benefit.rate'
    _decription = 'Employee Benefit Rate'

    def _get_amounts_now(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        for rate in self.browse(cr, uid, ids, context=context):
            res[rate.id] = {
                'employee_amount': rate.get_amount(today),
                'employer_amount': rate.get_amount(
                    today, employer=True),
            }
        return res

    def get_amount(self, cr, uid, ids, date, employer=False, context=None):
        rate = self.browse(cr, uid, ids[0], context=context)
        for line in rate.line_ids:
            if line.date_start <= date and (
                not line.date_end or date <= line.date_end
            ):
                return employer and line.employer_amount or \
                    line.employee_amount
        return False

    def compute_amounts(
        self, cr, uid, ids, payslip, context=None
    ):
        """
        Compute benefit lines that are calculated globally over the payslip.
        These include the following types: each_pay, annual and percent_gross
        """
        payslip_from = strptime(
            payslip.date_from, DEFAULT_SERVER_DATE_FORMAT).date()
        payslip_to = strptime(
            payslip.date_to, DEFAULT_SERVER_DATE_FORMAT).date()
        duration = (payslip_to - payslip_from).days + 1

        for rate in self.browse(cr, uid, ids, context=context):

            rate_lines = [
                line for line in rate.line_ids
                if (
                    not line.date_end or payslip.date_from <= line.date_end
                ) and line.date_start <= payslip.date_to
            ]

            for line in rate_lines:
                ratio = 1.0

                # If the amount type is percentage, we multiply it by the gross
                # salary of the payslip
                if line.amount_type == 'percent_gross':
                    ratio *= payslip.gross_salary / 100

                # Case where the kind of amount requested by the salary rule
                # is different the amount computed in the benefit record
                elif line.amount_type == 'annual':
                    ratio /= payslip.pays_per_year

                # Case where the benefit begins after the payslip period
                # begins.
                date_start = strptime(
                    line.date_start, DEFAULT_SERVER_DATE_FORMAT).date()
                start_offset = max((date_start - payslip_from).days, 0)

                # Case where the benefit ends before the payslip period
                # ends.
                date_end = line.date_end and strptime(
                    line.date_end, DEFAULT_SERVER_DATE_FORMAT).date() or False
                end_offset = date_end and max(
                    (payslip_to - date_end).days, 0) or 0

                duration_ratio = 1 - float(
                    start_offset + end_offset) / duration
                ratio *= duration_ratio

                self.pool['hr.payslip.benefit.line'].create(
                    cr, uid, {
                        'payslip_id': payslip.id,
                        'employer_amount': ratio * line.employer_amount,
                        'employee_amount': ratio * line.employee_amount,
                        'category_id': line.category_id.id,
                        'source': 'contract',
                    }, context=context)

    def compute_amounts_per_hour(
        self, cr, uid, ids, wd, context=None
    ):
        """
        Compute the amounts of benefit that are calculated over worked hours.
        """
        wd_from = strptime(wd.date_from, DEFAULT_SERVER_DATE_FORMAT).date()
        wd_to = strptime(wd.date_to, DEFAULT_SERVER_DATE_FORMAT).date()
        duration = (wd_to - wd_from).days + 1

        for rate in self.browse(cr, uid, ids, context=context):

            rate_lines = [
                line for line in rate.line_ids
                if (
                    not line.date_end or wd.date_from <= line.date_end
                ) and line.date_start <= wd.date_to
            ]

            for line in rate_lines:
                # Case where the benefit begins after the worked days
                date_start = strptime(
                    line.date_start, DEFAULT_SERVER_DATE_FORMAT).date()
                start_offset = max((date_start - wd_from).days, 0)

                # Case where the benefit ends before the worked days
                date_end = line.date_end and strptime(
                    line.date_end, DEFAULT_SERVER_DATE_FORMAT).date() or False

                end_offset = date_end and max((wd_to - date_end).days, 0) or 0

                ratio = 1 - float(start_offset + end_offset) / duration

                self.pool['hr.payslip.benefit.line'].create(
                    cr, uid, {
                        'payslip_id': wd.payslip_id.id,
                        'employer_amount': ratio * line.employer_amount *
                        wd.number_of_hours,
                        'employee_amount': ratio * line.employee_amount *
                        wd.number_of_hours,
                        'category_id': line.category_id.id,
                        'source': 'contract',
                    }, context=context)

    _columns = {
        'category_id': fields.many2one(
            'hr.employee.benefit.category',
            'Benefit Category',
            required=True,
        ),
        'name': fields.char('Name', required=True),
        'line_ids': fields.one2many(
            'hr.employee.benefit.rate.line',
            'parent_id',
            'Rates',
        ),
        'amount_type': fields.selection(
            get_amount_types,
            required=True,
            string="Amount Type",
        ),
        'employee_amount': fields.function(
            _get_amounts_now,
            string='Employee Contribution',
            multi=True,
            readonly=True,
        ),
        'employer_amount': fields.function(
            _get_amounts_now,
            string='Employer Contribution',
            multi=True,
            readonly=True,
        ),
    }

    _defaults = {
        'amount_type': 'each_hour',
    }

    def _check_overlapping_rates(self, cr, uid, ids, context=None):
        """
        Checks if a rate has two lines that overlap in time.
        """
        for rate in self.browse(cr, uid, ids, context):

            for r1, r2 in permutations(rate.line_ids, 2):
                if r1.date_end and (
                        r1.date_start <= r2.date_start <= r1.date_end):
                    return False
                elif not r1.date_end and (r1.date_start <= r2.date_start):
                    return False

        return True

    _constraints = [(
        _check_overlapping_rates,
        'Error! You cannot have overlapping rates',
        ['line_ids']
    )]
