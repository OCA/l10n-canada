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

from . import (
    test_hr_leave_accrual,
    test_hr_payslip,
    test_hr_holidays_public,
    test_4_weeks_of_gross,
    test_payroll_structure,
)

checks = [
    test_hr_leave_accrual,
    test_hr_payslip,
    test_hr_holidays_public,
    test_4_weeks_of_gross,
    test_payroll_structure,
]
