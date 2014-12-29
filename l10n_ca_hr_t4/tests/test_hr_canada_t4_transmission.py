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


class test_canada_t4_transmission(common.TransactionCase):
    """
    Test methods of Canada T4 transmission
    """
    def setUp(self):
        super(test_canada_t4_transmission, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.company_model = self.registry("res.company")
        self.transmission_model = self.registry("hr.canada.t4.transmission")

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        # Create a company
        self.company_id = self.company_model.create(
            cr, uid, {
                'name': 'Company 1',
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

        super(test_canada_t4_transmission, self).tearDown()

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
                    't4_original_ids': [],
                    'sbmt_ref_id': '123456',
                }, context=context)

    def test_check_contact_phone_2(self):
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
                    't4_original_ids': [],
                    'sbmt_ref_id': '123456',
                }, context=context)
