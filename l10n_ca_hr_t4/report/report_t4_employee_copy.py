# -*- coding:utf-8 -*-#########################################################
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

from openerp.report import report_sxw


class report_t4_employee_copy(report_sxw.rml_parse):
    """
    This report is a T4 slip for the employee.
    It is not a copy to be sent to the CRA.
    """
    def __init__(self, cr, uid, name, context):
        super(report_t4_employee_copy, self).__init__(cr, uid, name, context)

report_sxw.report_sxw(
    'report.t4_employee_copy',
    'hr.cra.t4',
    'l10n_ca_hr_t4/report/report_t4_employee_copy.rml',
    parser=report_t4_employee_copy,
    header=False
)
