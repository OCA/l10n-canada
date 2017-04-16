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
from openerp.tools.translate import _


class res_company(orm.Model):
    _inherit = 'res.company'

    def get_next_rq_sequential_number(
        self, cr, uid, model, company_id, year, context=None
    ):
        """
        Create a sequential number as required by Revenu Quebec.

        Each number can be used one time each year.

        The range of number is defined in the company model.
        It is assigned to the company by Revenu Quebec.
        """
        company = self.browse(
            cr, uid, company_id, context=context)

        first_number = company.rq_first_slip_number
        last_number = company.rq_last_slip_number

        if not first_number or not last_number:
            raise orm.except_orm(
                _('Error'),
                _("Your sequence number range for Revenu Quebec "
                    "is incorrectly set")
            )

        # Get the model of the required fiscal slip
        slip_obj = self.pool[model]

        slip_ids = slip_obj.search(
            cr, uid, [
                ('company_id', '=', company.id),
                ('year', '=', year),
                ('number', '!=', False),
            ],
            context=context)

        number = first_number

        if slip_ids:
            if isinstance(slip_ids, (int, long)):
                slip_ids = [slip_ids]

            assigned_numbers = [
                # we get the first 8 digits of the number
                # the ninth digit is a validation digit
                # so we remove it
                int((float(slip.number) / 10) // 1) for slip in
                slip_obj.browse(cr, uid, slip_ids, context=context)
            ]

            while number in assigned_numbers:
                # we find a number that is not already assigned
                number += 1

                if number > last_number:
                    raise orm.except_orm(
                        _('Error'),
                        _("You have already used all your sequential "
                            "numbers assigned by Revenu Quebec")
                    )

        num_A = float(number) / 7
        # Here, we need 2 decimals
        # round function do what we need here, because
        # round(2.539, 2) * 7 would give 2.54 * 7
        # we need 2.53 * 7
        num_B = (num_A % 1 - num_A % 0.01) * 7
        num_C = round(num_B, 0)

        return number * 10 + int(num_C)
