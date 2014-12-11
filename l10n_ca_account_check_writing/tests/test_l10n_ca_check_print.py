# -*- encoding: utf-8 -*-
#
# OpenERP, Open Source Management Solution
# This module copyright (C) 2014 Savoir-faire Linux
# (<http://www.savoirfairelinux.com>).
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


from openerp.addons.l10n_ca_account_check_writing.report.l10n_ca_check_print import report_print_check  # noqa
from openerp.tests import common


class test_l10n_ca_check_print(common.TransactionCase):
    def setUp(self):
        super(test_l10n_ca_check_print, self).setUp()
        self.ref = self.registry('ir.model.data')
        self.report = report_print_check
        self.cad = self.ref.get_object(self.cr, self.uid, 'base', 'CAD')
        self.get_amount_line = self.report._get_amount_line

    def test_get_amount_line_returns(self):
        self.assertEqual(
            self.get_amount_line(666, self.cad, 'en'),
            ('***********************Six Hundred Sixty-Six '
             'And 0/100 Canadian Dollars ')
        )

        self.assertEqual(
            self.get_amount_line(666.00, self.cad, 'en'),
            ('***********************Six Hundred Sixty-Six '
             'And 0/100 Canadian Dollars ')
        )

        self.assertEqual(
            self.get_amount_line(666.11, self.cad, 'en'),
            ('**********************Six Hundred Sixty-Six '
             'And 11/100 Canadian Dollars ')
        )

        # testing French also, as it is also an official language in Canada.
        # We call the method directly, without running all the process of odoo,
        # that why only num2word words are translated here.
        self.assertEqual(
            self.get_amount_line(666.11, self.cad, 'fr'),
            ('**********************Six Cent Soixante-Six Canadian Dollars '
             'And 11/100 ')
        )

    def test_get_amount_line_returns_72_chars(self):
        """ To no break the check layout, the amount should always be 72
        characters. Too small lines are filled with stars.
        """
        self.assertEqual(len(self.get_amount_line(666, self.cad, 'en')), 72)
        self.assertEqual(len(self.get_amount_line(666.11, self.cad, 'en')), 72)
        self.assertEqual(len(self.get_amount_line(666.11, self.cad, 'fr')), 72)
