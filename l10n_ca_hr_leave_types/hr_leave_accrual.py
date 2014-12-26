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


class hr_leave_accrual(orm.Model):
    _inherit = 'hr.leave.accrual'

    def sum_lines_by_category(
        self, cr, uid, accrual_id, date, context=None
    ):
        """
        Sums over lines in a leave accrual by category

        3 categories are required to compute a payslip in Quebec
            * previous_ytd: the amount accruded for the current year that
              the employee can take.
            * current_added_ytd: the amount accruded during the current year.
            * current_taken_ytd: the amount accruded for the year already
              taken by the employee.
        """
        # Get leave accrual lines entered manually
        # or related to an approved payslip
        approved_lines = self._get_approved_lines(
            cr, uid, [accrual_id], context=context
        )[accrual_id]

        res = {
            'current_added_ytd': 0,
            'current_taken_ytd': 0,
            'previous_ytd': 0,
        }
        year = int(date[0:4])
        for line in approved_lines:

            # Get date whether the line is manually entered
            # or related to a payslip
            line_date = line.payslip_id and \
                line.payslip_id.date_from or line.date
            line_year = int(line_date[0:4])

            # Check if the amount is added or substracted
            if line_year == year:
                if line.substract:
                    res['current_taken_ytd'] += line.amount
                else:
                    res['current_added_ytd'] += line.amount
            elif line_year < year:
                if line.substract:
                    res['previous_ytd'] -= line.amount
                else:
                    res['previous_ytd'] += line.amount

        return res
