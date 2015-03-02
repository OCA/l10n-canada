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

{
    'name': 'Canada Social Insurance Number (SIN/NAS)',
    'version': '1.2',
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    'license': 'AGPL-3',
    'category': 'Localisation/Canada',
    'depends': ['base'],
    'description': """
Canada Social Insurance Number (SIN/NAS)
========================================

Add the Social Insurance Number (SIN/NAS) to the partner form.

Contributors
------------
* Joao Alfredo Gama Batista <joao.gama@savoirfairelinux.com>
* Marc Cassuto <marc.cassuto@savoirfairelinux.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
* David Dufresne <david.dufresne@savoirfairelinux.com>
""",
    'data': [
        'res_partner_attributes_add_SIN_view.xml',
    ],
    'installable': True,
}
