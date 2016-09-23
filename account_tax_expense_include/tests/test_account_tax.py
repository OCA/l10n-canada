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

        # Create a tax
        self.tax_id = self.tax_model.create(
            cr, uid, {
                'name': 'test',
                'amount': 0.15,
                'expense_include': True,
            }, context=self.context
        )

        # Create a product
        self.product_id = self.product_model.create(
            cr, uid, {
                'name': 'test',
                'taxes_id': [(6, 0, [self.tax_id])],
                'supplier_taxes_id': [(6, 0, [self.tax_id])],
            }, context=self.context
        )

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)
        self.product_model.unlink(
            cr, uid, [self.product_id], context=context)
        self.tax_model.unlink(
            cr, uid, [self.tax_id], context=context)
        self.partner_model.unlink(
            cr, uid, [self.address_id, self.supplier_id], context=context)

        super(test_account_tax, self).tearDown()

    def test_compute_all_expense_tax_included(self):
        """Test the compute_all method when is_expense is True
        and tax is included"""
        cr, uid, context = self.cr, self.uid, self.context

        tax = self.tax_model.browse(cr, uid, self.tax_id, context=context)

        res = self.tax_model.compute_all(
            cr, uid, [tax], 100, 1, product=self.product_id,
            partner=self.supplier_id, force_excluded=False, is_expense=True)

        self.assertEqual(res['total'], 86.96)
        self.assertEqual(res['total_included'], 100)

    def test_compute_all_expense_tax_excluded(self):
        """Test the compute_all method when is_expense is True
        and tax is excluded"""
        cr, uid, context = self.cr, self.uid, self.context

        tax = self.tax_model.browse(cr, uid, self.tax_id, context=context)

        tax.write({'expense_include': False})
        tax.refresh()

        res = self.tax_model.compute_all(
            cr, uid, [tax], 100, 1, product=self.product_id,
            partner=self.supplier_id, force_excluded=False, is_expense=True)

        self.assertEqual(res['total'], 100)
        self.assertEqual(res['total_included'], 115)

    def test_compute_all_expense_force_exclude(self):
        """Test the compute_all method when is_expense is True
        and tax is excluded"""
        cr, uid, context = self.cr, self.uid, self.context

        tax = self.tax_model.browse(cr, uid, self.tax_id, context=context)

        res = self.tax_model.compute_all(
            cr, uid, [tax], 100, 1, product=self.product_id,
            partner=self.supplier_id, force_excluded=True, is_expense=True)

        self.assertEqual(res['total'], 100)
        self.assertEqual(res['total_included'], 115)

    def test_compute_all_not_expense_tax_included(self):
        """Test the compute_all method when is_expense is False
        and tax is included"""
        cr, uid, context = self.cr, self.uid, self.context

        tax = self.tax_model.browse(cr, uid, self.tax_id, context=context)

        res = self.tax_model.compute_all(
            cr, uid, [tax], 100, 1, product=self.product_id,
            partner=self.supplier_id, force_excluded=False, is_expense=False)

        self.assertEqual(res['total'], 100)
        self.assertEqual(res['total_included'], 115)
