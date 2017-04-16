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


def display_address_no_blank_line(partner, name):
    """
    Return a string containing the address with no blank lines
    """
    address = '%s\n' % name

    if partner.street:
        address += '%s\n' % partner.street

    if partner.street2:
        address += '%s\n' % partner.street2

    if partner.city:
        address += '%s, ' % partner.city

    if partner.state_id:
        address += '%s ' % partner.state_id.code

    if partner.zip:
        address += '%s' % partner.zip

    if partner.city or partner.state_id or partner.zip:
        address += '\n'

    if partner.country_id:
        address += '%s' % partner.country_id.name

    return address


class report_releve_1_copy_1(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_releve_1_copy_1, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'content_qr_bar_code': True,
            'releve_type': '12EE',
            'display_address_no_blank_line': display_address_no_blank_line,
        })


report_sxw.report_sxw(
    'report.releve_1_copy_1',
    'hr.releve_1',
    'l10n_ca_qc_hr_releve_1/report/report_releve_1.rml',
    parser=report_releve_1_copy_1,
    header=False
)


class report_releve_1_copy_2(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_releve_1_copy_2, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'content_qr_bar_code': False,
            'releve_type': '12EF',
            'display_address_no_blank_line': display_address_no_blank_line,
        })


report_sxw.report_sxw(
    'report.releve_1_copy_2',
    'hr.releve_1',
    'l10n_ca_qc_hr_releve_1/report/report_releve_1.rml',
    parser=report_releve_1_copy_2,
    header=False
)
