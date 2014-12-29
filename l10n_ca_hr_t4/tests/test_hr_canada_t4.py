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


class test_canada_t4_slip(common.TransactionCase):
    """
    Test the Canada T4 slip and method to generate the transmission XML
    """
    def get_payslip_lines(self, payslip_id):
        """
        Get a dict of payslip lines
        """
        payslip = self.payslip_model.browse(
            self.cr, self.uid, payslip_id, context=self.context)

        return {
            line.code: line.total
            for line in payslip.details_by_salary_rule_category
        }

    def get_benefit_id(self, code):
        """
        Gets an employee benefit category id from a given code
        """
        return self.benefit_model.search(
            self.cr, self.uid, [('code', '=', code)],
            context=self.context)[0]

    def setUp(self):
        super(test_canada_t4_slip, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.worked_days_model = self.registry("hr.payslip.worked_days")
        self.contract_model = self.registry("hr.contract")
        self.activity_model = self.registry("hr.activity")
        self.structure_model = self.registry("hr.payroll.structure")
        self.job_model = self.registry("hr.job")
        self.t4_model = self.registry("hr.canada.t4")
        self.company_model = self.registry("res.company")
        self.partner_model = self.registry("res.partner")
        self.benefit_model = self.registry("hr.benefit.category")
        self.transmission_model = self.registry("hr.canada.t4.transmission")
        self.other_amount_model = self.registry(
            "hr.canada.t4.other_amount.source")

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

        self.address_home_id = self.partner_model.create(
            cr, uid, {
                'name': 'test',
                'street': 'test',
                'street2': 'test',
                'city': 'Regina',
                'zip': 'P1P1P1',
                'country_id': self.country_id,
                'state_id': self.state_id,
                'nas': 684242680,
            }, context=context)

        # Create an employee
        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
                'firstname': 'John',
                'lastname': 'Doe',
                'company_id': self.company_id,
                'address_home_id': self.address_home_id,
            }, context=context)

        # Get the canadian payroll structure
        self.structure_id = self.structure_model.search(
            cr, uid, [('code', '=', 'CA')], context=context)[0]

        # Create a contract
        self.contract_id = self.contract_model.create(
            cr, uid, {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 52000,
                'schedule_pay': 'monthly',
                'struct_id': self.structure_id,
                'benefit_line_ids': [
                    (0, 0, {
                        'category_id': self.get_benefit_id(ben[0]),
                        'date_start': '2014-01-01',
                        'date_end': '2014-12-31',
                        'amount_type': 'each_pay',
                        'employee_amount': ben[1],
                        'employer_amount': ben[2],
                    }) for ben in [
                        ('RPP', 50, 100),
                        ('RCA', 75, 150),
                    ]
                ]
            }, context=context)

        # Create a job for the employee
        self.job_id = self.job_model.create(
            cr, uid, {'name': 'job_id 1'}, context=context)

        # Get the id of the activity for job 1
        self.job_activity_id = self.job_model.browse(
            cr, uid, self.job_id, context=context
        ).activity_ids[0].id

        # Create a payslip
        self.payslip_ids = {
            payslip[0]: self.payslip_model.create(
                cr, uid, {
                    'employee_id': self.employee_id,
                    'contract_id': self.contract_id,
                    'date_from': payslip[1],
                    'date_to': payslip[2],
                    'struct_id': self.structure_id,
                }, context=context)
            for payslip in [
                (1, '2014-01-01', '2014-01-31'),
                (2, '2014-06-01', '2014-06-30'),
                (3, '2014-12-01', '2014-12-31'),

                # payslip that will be excluded from
                # the computation because the dates don't match
                (4, '2015-01-01', '2015-01-31'),
            ]
        }

        # Create the worked_days records
        for wd in [
            # (date_from, date_to, payslip)
            ('2014-01-01', '2014-01-31', 1),
            ('2014-06-01', '2014-06-30', 2),
            ('2014-12-01', '2014-12-31', 3),
            ('2015-01-01', '2015-01-31', 4),
        ]:
            self.worked_days_model.create(
                cr, uid, {
                    'date_from': wd[0],
                    'date_to': wd[1],
                    'activity_id': self.job_activity_id,
                    'number_of_hours': 160,
                    'hourly_rate': 50,
                    'payslip_id': self.payslip_ids[wd[2]],
                }, context=context)

        self.t4_id = self.t4_model.create(
            cr, uid, {
                'year': 2014,
                'employee_id': self.employee_id,
                'empt_prov_cd': 'AB',
            }, context=context)

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.payslip_model.write(
            cr, uid, self.payslip_ids.values(),
            {'state': 'draft'}, context=context)
        self.payslip_model.unlink(
            cr, uid, self.payslip_ids.values(), context=context)

        self.job_model.unlink(
            cr, uid, [self.job_id], context=context)
        self.contract_model.unlink(
            cr, uid, [self.contract_id], context=context)
        self.t4_model.unlink(
            cr, uid, [self.t4_id], context=context)
        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)

        self.partner_model.unlink(
            cr, uid, [self.address_home_id], context=context)
        self.company_model.unlink(
            cr, uid, [self.company_id], context=context)

        super(test_canada_t4_slip, self).tearDown()

    def test_compute_amounts(self):
        """Test that the compute_amounts method on T4 sums over the payslips
        amounts properly"""
        cr, uid, context = self.cr, self.uid, self.context

        for payslip_id in self.payslip_ids.values():
            self.payslip_model.compute_sheet(
                cr, uid, [payslip_id], context=context)

            self.payslip_model.write(
                cr, uid, [payslip_id], {'state': 'done'},
                context=context)

        self.t4_model.compute_amounts(
            cr, uid, [self.t4_id], context=context)

        t4 = self.t4_model.browse(cr, uid, self.t4_id, context=context)

        # The 3 payslips must have the same value, so we get the values
        # in the first and multiply by 3
        payslip_1 = self.get_payslip_lines(self.payslip_ids[1])

        self.assertEqual(
            t4.empt_incamt, round(payslip_1['FIT_I_OTHER_WAGE'] * 3, 2))
        self.assertEqual(t4.cpp_cntrb_amt, round(payslip_1['CPP_EE_C'] * 3, 2))
        self.assertEqual(t4.qpp_cntrb_amt, 0)
        self.assertEqual(
            t4.empe_eip_amt, round(payslip_1['EI_EE_C'] * 3, 2))
        self.assertEqual(t4.itx_ddct_amt, round(payslip_1['FIT_T'] * 3, 2))
        self.assertEqual(
            t4.ei_insu_ern_amt, round(payslip_1['EI_EE_MAXIE'] * 3, 2))
        self.assertEqual(
            t4.cpp_qpp_ern_amt, round(payslip_1['CPP_EE_MAXIE'] * 3, 2))
        self.assertEqual(t4.prov_pip_amt, 0)
        self.assertEqual(t4.prov_insu_ern_amt, 0)
        self.assertEqual(t4.empr_cpp_amt, round(payslip_1['CPP_ER_C'] * 3, 2))
        self.assertEqual(t4.empr_eip_amt, round(payslip_1['EI_ER_C'] * 3, 2))
        self.assertEqual(t4.rpp_cntrb_amt, (50 + 75) * 3)

    def test_create_transmission_xml(self):
        """Test that the T4 transmision xml is generated without error
        and the xml attibute is not blank after the computation"""
        cr, uid, context = self.cr, self.uid, self.context

        for payslip_id in self.payslip_ids.values():
            self.payslip_model.compute_sheet(
                cr, uid, [payslip_id], context=context)

            self.payslip_model.write(
                cr, uid, [payslip_id], {'state': 'done'},
                context=context)

        self.t4_model.compute_amounts(
            cr, uid, [self.t4_id], context=context)

        self.trans_id = self.transmission_model.create(
            cr, uid, {
                'year': 2014,
                'company_id': self.company_id,
                'proprietor_1_id': self.employee_id,
                'contact_id': self.employee_id,
                'contact_area_code': 888,
                'contact_phone': '888-8888',
                'contact_email': 'test@test.com',
                'contact_extension': 1234,
                't4_original_ids': [(6, 0, [self.t4_id])],
                'sbmt_ref_id': '123456',
            }, context=context)

        self.transmission_model.generate_xml(
            cr, uid, [self.trans_id], context=context)

        trans = self.transmission_model.browse(
            cr, uid, self.trans_id, context=context)

        self.assertNotEqual(trans.xml, '')

        trans.unlink()

    def test_t4_check_other_amounts_same_source(self):
        """Test _check_other_amounts when 2 other amounts
        have the same source"""
        t4 = self.t4_model.browse(cr, uid, [self.t4_id], context=context)

        source = self.other_amount_model.search(
            cr, uid, [('box_number', '=', 30)], context=context)

        t4.write({
            'other_amount_ids': []
        })
