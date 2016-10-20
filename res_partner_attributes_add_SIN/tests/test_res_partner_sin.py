# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
