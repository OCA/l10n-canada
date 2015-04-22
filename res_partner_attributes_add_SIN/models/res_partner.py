# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import fields, models, api, _, exceptions


class ResPartner(models.Model):
    """
    Add SIN column to partner model
    """
    _inherit = 'res.partner'

    sin = fields.Float(
        'SIN',
        digits=(9, 0),
        help="Social Insurance Number (9 digits)",
    )

    @api.one
    @api.onchange("sin")
    @api.constrains("sin")
    def validate_sin(self):
        """
        Check if SIN is valid when changed or saved
        :return: none
        :raises: exceptions.Warning when SIN is invalid
        """

        def digits_of(n):
            """
            Turn SIN into string and extract digits
            :param n: float representing SIN
            :return: list of SIN digits
            """
            return [int(d) for d in str(int(n))]

        def luhn_checksum(sin):
            """
            Compute SIN checksum
            :param sin: SIN
            :return: SIN checksum
            """
            digits = digits_of(sin)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = 0
            checksum += sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10

        def is_luhn_valid(sin):
            """
            Check if SIN is valid
            :param sin: SIN
            :return: boolean if valid or not
            """
            return luhn_checksum(sin) == 0

        if not is_luhn_valid(self.sin):
            raise exceptions.ValidationError(
                _('The number provided is not a valid SIN number!')
            )
