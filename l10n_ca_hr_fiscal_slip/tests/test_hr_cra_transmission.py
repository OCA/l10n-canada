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
from openerp.osv import orm


class test_cra_transmission(common.TransactionCase):
    def setUp(self):
        super(test_cra_transmission, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.company_model = self.registry("res.company")
        self.transmission_model = self.registry("hr.cra.transmission")
        self.partner_model = self.registry("res.partner")

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.country_id = self.registry("res.country").search(
            cr, uid, [('code', '=', 'CA')], context=context)[0]
        self.state_id = self.registry("res.country.state").search(
            cr, uid, [
                ('code', '=', 'AB'), ('country_id', '=', self.country_id)
            ], context=context)[0]

        # Create a company
        self.company_id = self.company_model.create(
            cr, uid, {
                'name': 'Company 1',
                'street': 'test',
                'street2': 'test',
                'city': 'Regina',
                'zip': 'P1P1P1',
                'country_id': self.country_id,
                'state_id': self.state_id,
            }, context=context)

        # Create an address
        self.address_id = self.partner_model.create(
            cr, uid, {
                'name': 'test',
                'street': 'test',
                'street2': 'test',
                'city': 'Regina',
                'zip': 'P1P1P1',
                'country_id': self.country_id,
                'state_id': self.state_id,
            }, context=context)

        # Create an employee
        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
                'company_id': self.company_id,
            }, context=context)

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        # When checking contraints, records are created in
        # the database
        transmission_ids = self.transmission_model.search(
            cr, uid, [('company_id', '=', self.company_id)],
            context=context)
        self.transmission_model.unlink(
            cr, uid, transmission_ids, context=context)

        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)
        self.company_model.unlink(
            cr, uid, [self.company_id], context=context)
        self.partner_model.unlink(
            cr, uid, [self.address_id], context=context)

        super(test_cra_transmission, self).tearDown()

    def test_check_contact_phone(self):
        """Test the _check_contact_phone returns False when
        the phone number format is not correct"""
        cr, uid, context = self.cr, self.uid, self.context

        for phone_number in [
            '88-8888', '888-888', '888', '8888888', 'aaa-aaaa', '',
        ]:
            self.assertRaises(
                orm.except_orm,
                self.transmission_model.create, cr, uid, {
                    'year': 2014,
                    'company_id': self.company_id,
                    'proprietor_1_id': self.employee_id,
                    'contact_id': self.employee_id,
                    'contact_area_code': 888,
                    'contact_phone': phone_number,
                    'contact_email': 'test@test.com',
                    'contact_extension': 1234,
                    'sbmt_ref_id': '123456',
                }, context=context)

    def test_check_contact_phone_area_code(self):
        """Test the _check_contact_phone returns False when
        the area code format is not correct"""
        cr, uid, context = self.cr, self.uid, self.context

        for area_code in [
            1234, 12, 0,
        ]:
            self.assertRaises(
                orm.except_orm,
                self.transmission_model.create, cr, uid, {
                    'year': 2014,
                    'company_id': self.company_id,
                    'proprietor_1_id': self.employee_id,
                    'contact_id': self.employee_id,
                    'contact_area_code': area_code,
                    'contact_phone': '888-8888',
                    'contact_email': 'test@test.com',
                    'contact_extension': 1234,
                    'sbmt_ref_id': '123456',
                }, context=context)

    def test_make_address_dict_res_partner(self):
        """Test the make_address_dict method computes without error and
        returns a dict when a partner is passed in parameter"""
        cr, uid, context = self.cr, self.uid, self.context

        address = self.partner_model.browse(
            cr, uid, self.address_id, context=context)

        res = self.transmission_model.make_address_dict(
            cr, uid, address, context=context)

        self.assertIsInstance(res, dict)

    def test_make_address_dict_company(self):
        """Test the make_address_dict method computes without error and
        returns a dict when a company is passed in parameter"""
        cr, uid, context = self.cr, self.uid, self.context

        company = self.company_model.browse(
            cr, uid, self.company_id, context=context)

        res = self.transmission_model.make_address_dict(
            cr, uid, company, context=context)

        self.assertIsInstance(res, dict)

    def test_make_T619_xml(self):
        """Test the make_T619_xml method computes without error and
        returns a dict"""
        cr, uid, context = self.cr, self.uid, self.context

        self.trans_id = self.transmission_model.create(
            cr, uid, {
                'year': 2014,
                'company_id': self.company_id,
                'proprietor_1_id': self.employee_id,
                'contact_id': self.employee_id,
                'contact_area_code': 123,
                'contact_phone': '888-8888',
                'contact_email': 'test@test.com',
                'contact_extension': 1234,
                'sbmt_ref_id': '123456',
            }, context=context)

        trans = self.transmission_model.browse(
            cr, uid, self.trans_id, context=context)

        self.transmission_model.make_T619_xml(
            cr, uid, slip_return_xml='', trans=trans, context=context)
