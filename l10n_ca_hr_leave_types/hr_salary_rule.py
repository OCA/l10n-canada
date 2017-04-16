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

from openerp.osv import orm, fields


class hr_salary_rule(orm.Model):
    """
    Make the structure to salary rule many2many field bidirectionnal to enable
    adding salary rules to the structure by xml files.
    """
    _inherit = 'hr.salary.rule'
    _columns = {
        'structure_id': fields.many2many(
            'hr.payroll.structure',
            'hr_structure_salary_rule_rel',
            'rule_id',
            'struct_id',
            'Salary Structures',
        ),
    }
