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

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class HrLeaveAccrual(orm.Model):
    _inherit = 'hr.leave.accrual'

    def sum_leaves_available(
        self, cr, uid, ids, date, in_cash=False, context=None
    ):
        """
        Sum the leave days that the employee is allowed to take
        for a given type of leave.

        If the leave uses holidays entitlements, the employee will be
        allowed to consume his leaves accruded before the date
        of entitlement.

        Example
        -------
        If the payslip is paid on March 15th 2015 and the day of
        entitlement is the 1rst of May, then the employee is allowed
        to consume his leaves accruded before the 1rst of May 2014.
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1, "Expected single record"

        accrual = self.browse(cr, uid, ids[0], context=context)

        approved_lines = accrual._get_approved_lines()[ids[0]]

        amount_type = 'cash' if in_cash else 'hours'
        approved_lines = [
            line for line in approved_lines
            if line.amount_type == amount_type
        ]

        leave_type = accrual.leave_type_id

        entitlement = False
        if leave_type.uses_entitlement:
            date_slip = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)

            # Get the date of entitlement
            contract = accrual.employee_id.contract_id
            entitlement = contract.get_entitlement(leave_type)

        if entitlement:
            entitlement_date = datetime(
                date_slip.year,
                int(entitlement.month_start),
                entitlement.day_start)

            entitlement_date -= relativedelta(days=1)

            if entitlement_date >= date_slip:
                entitlement_date -= relativedelta(years=1)

            entitlement_date = entitlement_date.strftime(
                DEFAULT_SERVER_DATE_FORMAT)

            res = 0

            for line in approved_lines:

                # Get date whether the line is manually entered
                # or related to a payslip
                line_date = (
                    line.payslip_id.date_from if line.payslip_id else line.date
                )

                # Amounts available at the date of entitlement
                if line_date <= entitlement_date:
                    res += line.amount

                # If amounts were withdrawn from the accrual during the
                # the current year, they need to be removed from the amount
                # available
                elif line_date <= date:
                    # Check if the amount is added or taken
                    if (
                        (line.is_refund and line.amount >= 0) or
                        (not line.is_refund and line.amount < 0)
                    ):
                        res += line.amount

            return res

        return sum(
            line.amount for line in approved_lines
            if line.date <= date)
