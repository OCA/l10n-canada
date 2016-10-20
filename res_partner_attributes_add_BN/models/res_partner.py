# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResPartner(models.Model):
    """
    Add BN column to partner model
    """
    _inherit = 'res.partner'
    bn = fields.Float(
        'BN',
        digits=(9, 0),
        help="Canada Business Identification Number (9 digits)"
    )
