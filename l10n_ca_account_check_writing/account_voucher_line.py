# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp import api, models, fields


class VoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    @api.multi
    def get_suppl_inv_num(self):
        for rec in self:
            move_line = rec.move_line_id
            rec.supplier_invoice_number = (
                move_line.invoice and
                move_line.invoice.supplier_invoice_number or ''
            )

    supplier_invoice_number = fields.Char(size=64,
                                          string="Supplier Invoice Number",
                                          compute=get_suppl_inv_num)
