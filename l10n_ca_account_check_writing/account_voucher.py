# -*- coding: utf-8 -*-
# #############################################################################
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

from openerp.osv import orm, fields


class account_voucher(orm.Model):
    _inherit = 'account.voucher'

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id,
                        journal_id, currency_id, ttype, date,
                        payment_rate_currency_id, company_id, context=None):
        """ Inherited - add amount_in_word and allow_check_writting in returned value dictionary """
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        default = super(account_voucher, self).onchange_amount(
            cr, uid, ids, amount, rate, partner_id, journal_id, currency_id,
            ttype, date, payment_rate_currency_id, company_id, context=context)

        if 'value' in default:
            if journal_id:
                allow_check_writing = self.pool.get('account.journal').browse(
                    cr, uid, journal_id, context=context).allow_check_writing
                default['value'].update({'allow_check': allow_check_writing})
        return default

    def print_check(self, cr, uid, ids, context=None):
        if not ids:
            return {}

        check_layout_report = {
            'top': 'account.print.check.top',
            'middle': 'account.print.check.middle',
            'bottom': 'account.print.check.bottom',
            'top_ca': 'l10n.ca.account.print.check.top',
            'middle_ca': 'l10n.ca.account.print.check.middle',
        }

        check_layout = self.browse(cr, uid, ids[0],
                                   context=context).company_id.check_layout
        return {
            'type': 'ir.actions.report.xml',
            'report_name': check_layout_report[check_layout],
            'datas': {
                'model': 'account.voucher',
                'id': ids and ids[0] or False,
                'ids': ids and ids or [],
                'report_type': 'pdf'
            },
            'nodestroy': True
        }


# By default, the supplier reference number is not so easily accessible from a voucher line because
# there's no direct link between the voucher and the invoice. Fortunately, there was this recently
# submitted patch from Lorenzo Battistini (Agile) BG at
# https://code.launchpad.net/~elbati/account-payment/adding_account_voucher_supplier_invoice_number_7/+merge/165622
# which solves this exact problem and I shamelessely copied that code, which works well.


class voucher_line(orm.Model):
    _inherit = 'account.voucher.line'

    def get_suppl_inv_num(self, cr, uid, move_line_id, context=None):
        move_line = self.pool.get('account.move.line').browse(cr, uid,
                                                              move_line_id,
                                                              context)
        invoice = move_line.invoice
        return invoice.supplier_invoice_number if invoice else ''

    def _get_supplier_invoice_number(self, cr, uid, ids, name, args,
                                     context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = ''
            if line.move_line_id:
                res[line.id] = self.get_suppl_inv_num(cr, uid,
                                                      line.move_line_id.id,
                                                      context=context)
        return res

    _columns = {
        'supplier_invoice_number': fields.function(
            _get_supplier_invoice_number, type='char',
            size=64, string="Supplier Invoice Number"),
    }
