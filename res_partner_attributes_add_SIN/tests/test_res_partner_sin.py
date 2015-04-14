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
from openerp import exceptions
from openerp.tests import TransactionCase


class TestPartnerSin(TransactionCase):

    def setUp(self):
        super(TestPartnerSin, self).setUp()
        self.partner = self.env["res.partner"].create({
            "name": "Test Partner",
            "is_company": False
        })

    def test_valid_sin(self):
        """
        Test SIN from fake SIN generator
        :return:
        """
        self.partner.sin = 252646757

    def test_invalid_sin(self):
        with self.assertRaises(exceptions.ValidationError):
            self.partner.sin = 100000000
