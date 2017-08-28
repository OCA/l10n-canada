# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import  _, api, fields, models
from odoo.exceptions import ValidationError


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

    @api.multi
    @api.constrains('sin')
    def _check_sin(self):
        """
        Check if SIN is valid when changed or saved
        :return: none
        :raises: ValidationError when SIN is invalid
        """
        self.ensure_one()

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
            raise ValidationError(
                _('The number provided is not a valid SIN number!')
            )
