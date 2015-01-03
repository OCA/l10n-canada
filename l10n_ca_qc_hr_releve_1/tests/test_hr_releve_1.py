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


class test_releve_1(common.TransactionCase):
    """
    Test the Releve 1 methods
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
        super(test_releve_1, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.worked_days_model = self.registry("hr.payslip.worked_days")
        self.contract_model = self.registry("hr.contract")
        self.activity_model = self.registry("hr.activity")
        self.structure_model = self.registry("hr.payroll.structure")
        self.job_model = self.registry("hr.job")
        self.releve_1_model = self.registry("hr.releve_1")
        self.company_model = self.registry("res.company")
        self.partner_model = self.registry("res.partner")
        self.benefit_model = self.registry("hr.benefit.category")
        self.other_info_model = self.registry(
            "hr.releve_1.other_info.source")

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.country_id = self.registry("res.country").search(
            cr, uid, [('code', '=', 'CA')], context=context)[0]
        self.state_id = self.registry("res.country.state").search(
            cr, uid, [
                ('code', '=', 'QC'), ('country_id', '=', self.country_id)
            ], context=context)[0]

        # Create a company
        self.company_id = self.company_model.create(
            cr, uid, {
                'name': 'Company 1',
                'street': 'test',
                'street2': 'test',
                'city': 'Québec',
                'zip': 'P1P1P1',
                'country_id': self.country_id,
                'state_id': self.state_id,
                'rq_first_slip_number': 71997012,
                'rq_last_slip_number': 71997020,
                'rq_preparator_number': 'NP999999',
            }, context=context)

        self.address_home_id = self.partner_model.create(
            cr, uid, {
                'name': 'test',
                'street': 'test',
                'street2': 'test',
                'city': 'Québec',
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
            cr, uid, [('code', '=', 'QC')], context=context)[0]

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
                        'category_id': self.get_benefit_id('RPP'),
                        'date_start': '2014-01-01',
                        'date_end': '2014-12-31',
                        'amount_type': 'each_pay',
                        'employee_amount': 50,
                        'employer_amount': 100,
                    })
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

        self.releve_1_id = self.releve_1_model.create(
            cr, uid, {
                'year': 2014,
                'employee_id': self.employee_id,
                'company_id': self.company_id,
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
        self.releve_1_model.unlink(
            cr, uid, [self.releve_1_id], context=context)
        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)

        self.partner_model.unlink(
            cr, uid, [self.address_home_id], context=context)
        self.company_model.unlink(
            cr, uid, [self.company_id], context=context)

        super(test_releve_1, self).tearDown()

    def test_compute_amounts(self):
        """Test that the compute_amounts method on releve_1
        sums over the payslipsamounts properly"""
        cr, uid, context = self.cr, self.uid, self.context

        for payslip_id in self.payslip_ids.values():
            self.payslip_model.compute_sheet(
                cr, uid, [payslip_id], context=context)

            self.payslip_model.write(
                cr, uid, [payslip_id], {'state': 'done'},
                context=context)

        self.releve_1_model.compute_amounts(
            cr, uid, [self.releve_1_id], context=context)

        slip = self.releve_1_model.browse(
            cr, uid, self.releve_1_id, context=context)

        # The 3 payslips must have the same value, so we get the values
        # in the first and multiply by 3
        payslip_1 = self.get_payslip_lines(self.payslip_ids[1])

        self.assertEqual(
            slip.a_revenu_emploi,
            round(payslip_1['QIT_G'] * 3, 2)),
        self.assertEqual(
            slip.b_cotisation_rrq,
            round(payslip_1['QPP_EE_C'] * 3, 2)),
        self.assertEqual(
            slip.c_cotisation_ass_emploi,
            round(payslip_1['EI_EE_C'] * 3, 2)),
        self.assertEqual(
            slip.d_cotisation_rpa,
            round(payslip_1['RPP_EE_C'] * 3, 2)),
        self.assertEqual(
            slip.e_impot_que,
            round(payslip_1['QIT_A'] * 3, 2)),
        self.assertEqual(
            slip.g_salaire_admis_rrq,
            round(payslip_1['QPP_EE_MAXIE'] * 3, 2)),
        self.assertEqual(
            slip.h_cotisation_rqap,
            round(payslip_1['PPIP_EE_C'] * 3, 2)),
        self.assertEqual(
            slip.i_salaire_admis_rqap,
            round(payslip_1['PPIP_EE_MAXIE'] * 3, 2)),

    def test_check_other_info_same_source(self):
        """Test _check_other_info raises an error when 2 other amounts
        have the same source"""
        cr, uid, context = self.cr, self.uid, self.context

        releve_1 = self.releve_1_model.browse(
            cr, uid, self.releve_1_id, context=context)

        source_id = self.other_info_model.search(
            cr, uid, [('code', '=', 'A-1')], context=context)[0]

        self.assertRaises(
            orm.except_orm,
            releve_1.write, {
                'other_info_ids': [
                    (0, 0, {'amount': 100, 'source': source_id}),
                    (0, 0, {'amount': 200, 'source': source_id}),
                ],
            }
        )

    def test_check_other_info_too_many_sources(self):
        """Test _check_other_info raises an error when 5 other amounts
        are computed
        """
        cr, uid, context = self.cr, self.uid, self.context

        releve_1 = self.releve_1_model.browse(
            cr, uid, self.releve_1_id, context=context)

        source_ids = self.other_info_model.search(
            cr, uid, [], context=context)

        self.assertRaises(
            orm.except_orm,
            releve_1.write, {
                'other_info_ids': [
                    (0, 0, {'amount': 100, 'source': source_ids[0]}),
                    (0, 0, {'amount': 200, 'source': source_ids[1]}),
                    (0, 0, {'amount': 300, 'source': source_ids[2]}),
                    (0, 0, {'amount': 400, 'source': source_ids[3]}),
                    (0, 0, {'amount': 500, 'source': source_ids[4]}),
                ],
            }
        )

    def test_make_dtmx_barcode(self):
        """Test make_dtmx_barcode method computes without error
        and creates a datamatrix string with the proper size"""
        cr, uid, context = self.cr, self.uid, self.context

        self.releve_1_model.make_dtmx_barcode(
            cr, uid, [self.releve_1_id], context=context)

        releve_1 = self.releve_1_model.browse(
            cr, uid, self.releve_1_id, context=context)

        # In all cases, the bar code string must have 688 chars
        self.assertEqual(len(releve_1.dtmx_barcode_string), 688)
