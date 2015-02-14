# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
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

from openerp.tools.translate import _
from openerp.osv import orm

from .parser.td_canada import CSVParser


class AccountStatementProfile(orm.Model):
    _inherit = "account.statement.profile"

    def _get_import_type_selection(self, cr, uid, context=None):
        """Inherited from parent to add parser."""
        selection = super(AccountStatementProfile, self
                          )._get_import_type_selection(cr, uid,
                                                       context=context)
        selection.append((CSVParser.PARSER_NAME, _('CSV - TD Canada')))
        return selection
