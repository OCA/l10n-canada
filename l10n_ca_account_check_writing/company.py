# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

from openerp.osv import orm, fields


class res_company(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'check_layout': fields.selection([
            ('top', 'Check on Top'),
            ('middle', 'Check in middle'),
            ('bottom', 'Check on bottom'),
            ('top_ca', 'Check on top (CA)'),
            ('middle_ca', 'Check in middle (CA)'),
            ## ('bottom_ca', 'Check on bottom (CA)'),
            ],
            "Choose Check layout",
        )
    }
