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

    nas = fields.Float(
        'SIN',
        digits=(9, 0),
        help="Social Insurance Number (9 digits)",
    )

    @api.one
    @api.onchange("nas")
    @api.constrains("nas")
    def validate_nas(self):
        """
        Check if NAS is valid when changed or saved
        :return: none
        :raises: exceptions.Warning when NAS is invalid
        """

        def digits_of(n):
            """
            Turn NAS into string and extract digits
            :param n: float representing NAS
            :return: list of NAS digits
            """
            return [int(d) for d in str(int(n))]

        def luhn_checksum(nas):
            """
            Compute NAS checksum
            :param nas: NAS
            :return: NAS checksum
            """
            digits = digits_of(nas)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = 0
            checksum += sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10

        def is_luhn_valid(nas):
            """
            Check if NAS is valid
            :param nas: NAS
            :return: boolean if valid or not
            """
            return luhn_checksum(nas) == 0

        if not is_luhn_valid(self.nas):
            raise exceptions.ValidationError(
                _('The number provided is not a valid SIN number!')
            )
