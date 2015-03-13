# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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

from openerp.osv import orm, fields
import itertools


class hr_payslip(orm.Model):
    _inherit = 'hr.payslip'

    _columns = {
        'gross_salary': fields.float(
            'Gross Salary',
            digits=(9, 2),
            readonly=True,
        ),
        'pays_per_year': fields.float(
            'Number of pays per year',
            digits=(2, 0),
            readonly=True,
        ),
        'benefit_line_ids': fields.one2many(
            'hr.payslip.benefit.line',
            'payslip_id',
            'Employee Benefits',
        ),
    }

    def set_values(self, cr, uid, ids, payslip, values, context=None):
        """
        Allow to set payslip fields directly from the salary rules.

        This is required to allow setting fields pays_per_year and
        gross_salary at a precise moment in the salary structure.
        """
        if not isinstance(payslip, orm.browse_record):
            payslip = payslip.dict

        payslip.write(values)

    def compute_benefits(self, cr, uid, ids, payslip, context=None):
        """
        Compute the employee benefits on the payslip.

        This method must be called after the fields gross_salary and
        pays_per_year are set on the payslip.
        """
        if not isinstance(payslip, orm.browse_record):
            payslip = payslip.dict

        payslip.refresh()

        for benefit_line in payslip.benefit_line_ids:
            if benefit_line.source == 'contract':
                benefit_line.unlink()

        # Get all employee benefits related to the contract or each job
        # on the contract
        contract = payslip.contract_id
        benefits = contract.benefit_line_ids + list(itertools.chain(*[
            contract_job.job_id.benefit_line_ids for contract_job
            in contract.contract_job_ids
        ]))
        benefit_ids = [ben.id for ben in benefits]

        # Compute the amounts for each employee benefit
        self.pool['hr.employee.benefit'].compute_amounts(
            cr, uid, benefit_ids, payslip, context=context)

    def sum_benefits(
        self, cr, uid, ids, payslip, rule_id=False,
        exemption=False, benefit_codes=False, category_ids=False,
        annual=False, pays_per_year=False, employer=False,
        context=None
    ):
        """
        Method used to sum the employee benefits computed on the payslip

        Parameters
        ==========
        :param exemption: Get benefits that are not exempted from a
        source deduction

        :param benefit_codes: The type of benefit over which to sum

        :param employer: If True, sum over the employer contribution.
        If False, sum over the employee contribution

        :param annual: If true, return an annual amount
        If false, return a periodic amount
        """
        if not isinstance(payslip, orm.browse_record):
            payslip = payslip.dict

        payslip.refresh()

        benefits = payslip.benefit_line_ids

        if benefit_codes:
            if isinstance(benefit_codes, (int, long)):
                benefit_codes = [benefit_codes]

            benefits = [
                ben for ben in benefits
                if ben.category_id.code in benefit_codes
            ]

        if category_ids:
            benefits = [
                ben for ben in benefits
                if ben.category_id.id in category_ids
            ]

        if exemption:
            benefits = [
                ben for ben in benefits
                if not ben.category_id[exemption]
            ]

        if rule_id:
            salary_rule = self.pool['hr.salary.rule'].browse(
                cr, uid, rule_id, context=context)
            benefits = [
                ben for ben in benefits
                if ben.category_id in salary_rule.employee_benefit_ids
            ]

        if employer:
            res = sum([ben.employer_amount for ben in benefits])
        else:
            res = sum([ben.employee_amount for ben in benefits])

        if annual:
            res *= payslip.pays_per_year

        return res
