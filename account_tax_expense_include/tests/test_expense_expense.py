# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.tests import common


class test_account_tax(common.TransactionCase):
    def setUp(self):
        super(test_account_tax, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.partner_model = self.registry("res.partner")
        self.product_model = self.registry("product.product")
        self.tax_model = self.registry("account.tax")
        self.expense_model = self.registry("hr.expense.expense")
        self.position_model = self.registry("account.fiscal.position")
        self.account_model = self.registry("account.account")
        self.tax_code_model = self.registry("account.tax.code")
        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        country_id = self.registry("res.country").search(
            cr, uid, [('code', '=', 'US')], context=context)[0]

        state_id = self.registry("res.country.state").search(
            cr, uid, [('code', '=', 'AK'), ('country_id', '=', country_id)],
            context=context)[0]

        self.address_id = self.partner_model.create(
            cr, uid, {
                'name': 'test',
                'street': 'test',
                'street2': 'test',
                'city': 'test',
                'state_id': state_id,
                'country_id': country_id,
                'zip': 'test',
            }, context=self.context
        )

        # Create an employee
        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
                'address_home_id': self.address_id
            }, context=self.context)

        # Create a supplier
        self.supplier_id = self.partner_model.create(
            cr, uid, {
                'name': 'test',
                'supplier': True,
            }, context=self.context
        )

        # Get 2 accounts
        self.account_ids = self.account_model.search(
            cr, uid, [], limit=2, context=context)

        # Create tax codes
        self.tax_code_id = self.tax_code_model.create(
            cr, uid, {'name': 'test'}, context=self.context)
        self.tax_code_2_id = self.tax_code_model.create(
            cr, uid, {'name': 'test 2'}, context=self.context)

        # Create a tax
        self.tax_src_id = self.tax_model.create(
            cr, uid, {
                'name': 'Tax Source',
                'amount': 0.15,
                'base_code_id': self.tax_code_id,
            }, context=self.context
        )

        # Create a second tax
        self.tax_dest_id = self.tax_model.create(
            cr, uid, {
                'name': 'Tax Destination',
                'amount': 0.20,
                'base_code_id': self.tax_code_2_id,
            }, context=self.context
        )

        # Create a fiscal position
        self.position_id = self.position_model.create(
            cr, uid, {
                'name': 'test',
                'tax_ids': [(0, 0, {
                    'tax_src_id': self.tax_src_id,
                    'tax_dest_id': self.tax_dest_id,
                })],
                'account_ids': [(0, 0, {
                    'account_src_id': self.account_ids[0],
                    'account_dest_id': self.account_ids[1],
                })]
            })

        # Create a product
        self.product_id = self.product_model.create(
            cr, uid, {
                'name': 'test',
                'taxes_id': [(6, 0, [self.tax_src_id])],
                'supplier_taxes_id': [(6, 0, [self.tax_src_id])],
            }, context=self.context
        )

        # Create an expense
        self.expense_id = self.expense_model.create(
            cr, uid, {
                'name': 'test',
                'employee_id': self.employee_id,
                'line_ids': [(0, 0, {
                    'name': 'test',
                    'partner_id': self.supplier_id,
                    'unit_amount': 100,
                    'unit_quantity': 1,
                    'product_id': self.product_id,
                })],
            }, context=context)

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.expense_model.unlink(
            cr, uid, [self.expense_id], context=context)
        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)
        self.product_model.unlink(
            cr, uid, [self.product_id], context=context)
        self.position_model.unlink(
            cr, uid, [self.position_id], context=context)
        self.tax_model.unlink(
            cr, uid, [self.tax_src_id, self.tax_dest_id], context=context)
        self.partner_model.unlink(
            cr, uid, [self.address_id, self.supplier_id], context=context)

        super(test_account_tax, self).tearDown()

    def test_move_line_get_no_position(self):
        """Test fiscal positions are mapped correctly
        in method move_line_get when supplier has no fiscal position"""
        cr, uid, context = self.cr, self.uid, self.context

        res = self.expense_model.move_line_get(
            cr, uid, self.expense_id, context=context)

        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        tax_move = res[1]
        self.assertEqual(tax_move['tax_amount'], 15)

    def test_move_line_get_with_position(self):
        """Test fiscal positions are mapped correctly
        in method move_line_get when supplier has a fiscal position"""
        cr, uid, context = self.cr, self.uid, self.context

        self.partner_model.write(
            cr, uid, [self.supplier_id], {
                'property_account_position': self.position_id,
            }, context=self.context)

        res = self.expense_model.move_line_get(
            cr, uid, self.expense_id, context=context)

        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        tax_move = res[1]
        self.assertEqual(tax_move['tax_amount'], 20)
