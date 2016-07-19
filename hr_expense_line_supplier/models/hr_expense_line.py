# -*- coding: utf-8 -*-
# Copyright (C) 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class HrExpenseLine(models.Model):
    _inherit = 'hr.expense.line'
    partner_id = fields.Many2one('res.partner', 'Supplier')
