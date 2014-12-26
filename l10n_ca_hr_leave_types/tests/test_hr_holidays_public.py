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


class test_canada_holidays_public(common.TransactionCase):
    def setUp(self):
        super(test_canada_holidays_public, self).setUp()
        self.payslip_model = self.registry("hr.payslip")
        self.public_holidays_model = self.registry("hr.holidays.public")
        self.country_model = self.registry("res.country")
        self.state_model = self.registry("res.country.state")
        self.user_model = self.registry("res.users")
        self.context = self.user_model.context_get(self.cr, self.uid)

        canada_id = self.registry("res.country").search(
            self.cr, self.uid, [('code', '=', 'CA')], context=self.context
        )[0]
        usa_id = self.registry("res.country").search(
            self.cr, self.uid, [('code', '=', 'US')], context=self.context
        )[0]
        states = {
            state[0]: self.state_model.search(
                self.cr, self.uid,
                [('country_id', '=', state[1]), ('code', '=', state[0])],
                context=self.context
            )[0]

            for state in [
                ('QC', canada_id),
                ('ON', canada_id),
                ('CA', usa_id),
                ('ME', usa_id),
            ]
        }

        self.public_holidays_ids = [
            self.public_holidays_model.create(
                self.cr, self.uid,
                {
                    'year': 2014,
                    'country_id': canada_id,
                    'line_ids': [
                        (0, 0, {
                            'date': '2014-01-02',
                            'name': 'Test',
                            'state_ids': [(6, 0, [states['QC'], states['ON']])]
                        }),
                        (0, 0, {
                            'date': '2014-01-15',
                            'name': 'Test',
                            'state_ids': [(6, 0, [states['QC']])]
                        }),
                        (0, 0, {
                            'date': '2014-01-03',
                            'name': 'Test',
                            'state_ids': [(6, 0, [states['ON']])]
                        }),
                        (0, 0, {
                            'date': '2014-01-16',
                            'name': 'Test',
                            'state_ids': [(6, 0, [states['QC'], states['ON']])]
                        }),
                        (0, 0, {
                            'date': '2014-01-01',
                            'name': 'Test',
                            'state_ids': [(6, 0, [states['QC'], states['ON']])]
                        }),
                    ],
                }, context=self.context
            ),
            self.public_holidays_model.create(
                self.cr, self.uid,
                {
                    'year': 2015,
                    'country_id': canada_id,
                    'line_ids': [(0, 0, {
                        'date': '2015-01-02',
                        'name': 'Test',
                        'state_ids': [(6, 0, [states['QC'], states['ON']])]
                    })]
                }, context=self.context,
            ),
            self.public_holidays_model.create(
                self.cr, self.uid,
                {
                    'year': 2014,
                    'country_id': usa_id,
                    'line_ids': [(0, 0, {
                        'date': '2014-01-02',
                        'name': 'Test',
                        'state_ids': [(6, 0, [states['ME'], states['CA']])]
                    })]
                }, context=self.context,
            )
        ]

    def test_sum_public_holidays(self):
        res = self.payslip_model.get_public_holidays(
            self.cr, self.uid, [],
            '2014-01-02',
            '2014-01-15',
            country_code='CA',
            state_code='QC',
            context=self.context
        )

        self.assertEqual(len(res), 2)
