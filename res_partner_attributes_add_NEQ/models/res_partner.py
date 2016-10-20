# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResPartner(models.Model):
    """
    Add NEQ column to partner model
    """
    _inherit = 'res.partner'
    neq = fields.Float(
        'NEQ',
        digits=(10, 0),
        help="Quebec Enterprise Number (10 digits)"
    )
