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

from openerp.osv import orm
from dict2xml import dict2xml
from openerp.tools.translate import _
import iso3166


def make_address_dict(cr, uid, address, context=None):
    for field in [
        ('street', _('Street Line 1')),
        ('city', _('City')),
        ('state_id', _('Province')),
        ('country_id', _('Country')),
        ('zip', _('Postal Code')),
    ]:
        if not address[field[0]]:
            raise orm.except_orm(
                _('Error'),
                _('The field %s for %s is missing')
                % (field[1], address.name)
            )

    # Country code is in iso-3166-2, we need iso-3166-3
    country_code = address.country_id.code
    country = iso3166.countries.get(country_code)
    country_code = country.alpha3

    return {
        'addr_l1_txt': address.street[0:30],
        'addr_l2_txt': address.street2[0:30],
        'cty_nm': address.city[0:28],
        'prov_cd': address.state_id.code,
        'cntry_cd': country_code,
        'pstl_cd': address.zip,
    }


def make_T619_xml(
    cr, uid,
    slip_return_xml,
    trans,
    context=None
):
    # Here, we suppose the company is the transmitter
    transmitter = trans.company_id

    # The working address of the transmitter
    transmitter_address_dict = make_address_dict(
        cr, uid, transmitter, context=context
    )

    contact_dict = {
        'cntc_nm': trans.contact_id.name[0:22],
        'cntc_area_cd': trans.contact_area_code,
        'cntc_phn_nbr': trans.contact_phone,
        'cntc_email_area': trans.contact_email,
    }
    if trans.contact_extension:
        contact_dict['cntc_extn_nbr'] = \
            trans.contact_extension

    T619_dict = {
        'sbmt_ref_id': trans.sbmt_ref_id,
        'rpt_tcd': trans.type,
        'trnmtr_nbr': trans.trnmtr_nbr,
        'trnmtr_tcd': 3,
        'summ_cnt': len(trans.t4_slip_ids),
        'lang_cd': trans.lang_cd,
        'TRNMTR_NM': {
            'l1_nm': transmitter.name[0:30],
            'l2_nm': transmitter.name[30:60],
        },
        'TRNMTR_ADDR': transmitter_address_dict,
        'CNTC': contact_dict,
    }

    T619_xml = dict2xml(T619_dict, 'T619')

    return """\
<?xml version="1.0" encoding="UTF-8"?>
<Submission xmlns:ccms="http://www.cra-arc.gc.ca/xmlns/ccms/1-0-0"
xmlns:sdt="http://www.cra-arc.gc.ca/xmlns/sdt/2-2-0"
xmlns:ols="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols/1-0-1"
xmlns:ols1="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols1/1-0-1"
xmlns:ols10="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols10/1-0-1"
xmlns:ols100="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols100/1-0-1"
xmlns:ols12="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols12/1-0-1"
xmlns:ols125="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols125/1-0-1"
xmlns:ols140="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols140/1-0-1"
xmlns:ols141="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols141/1-0-1"
xmlns:ols2="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols2/1-0-1"
xmlns:ols5="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols5/1-0-1"
xmlns:ols50="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols50/1-0-1"
xmlns:ols52="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols52/1-0-1"
xmlns:ols6="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols6/1-0-1"
xmlns:ols8="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols8/1-0-1"
xmlns:ols9="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/ols9/1-0-1"
xmlns:olsbr="http://www.cra-arc.gc.ca/enov/ol/interfaces/efile/\
partnership/olsbr/1-0-1"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:noNamespaceSchemaLocation="layout-topologie.xsd">
%s
%s</Submission>""" % (T619_xml, slip_return_xml)
