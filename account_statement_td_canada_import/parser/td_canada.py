# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from csv import DictReader
from cStringIO import StringIO
from datetime import datetime

from openerp.addons.account_statement_base_import.parser import (
    BankStatementImportParser,
)
from openerp.addons.account_statement_base_import.parser.file_parser import (
    float_or_zero
)

TD_CANADA_CSV_FIELDS = [
    "date", "label", "credit", "debit", "balance",
]
TD_DATE_FORMAT = '%m/%d/%Y'


class CSVParser(BankStatementImportParser):
    """ Parser for TD Canada CSV format """
    PARSER_NAME = 'csv_td_canada'

    @classmethod
    def parser_for(cls, parser_name):
        """ Return if this parser is suitable for parser_name """
        return parser_name == cls.PARSER_NAME

    def _parse(self, *args, **kwargs):
        self.result_row_list = [
            row
            for row in DictReader(
                StringIO(self.filebuffer),
                TD_CANADA_CSV_FIELDS,
            )
        ]

    def _post(self, *args, **kwargs):
        for line in self.result_row_list:
            del line["balance"]
            credit = float_or_zero(line.pop('credit'))
            debit = float_or_zero(line.pop('debit'))
            line['amount'] = debit - credit
            line['date'] = datetime.strptime(
                line['date'], TD_DATE_FORMAT,
            ).date()

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the
        responsibility of every parser to give this dict of vals, so each one
        can implement his own way of recording the lines.
            :param:  line: a dict of vals that represent a line of
              result_row_list
            :return: dict of values to give to the create method of statement
              line, it MUST contain at least:
                {
                    'name':value,
                    'date':value,
                    'amount':value,
                    'ref':value,
                    'label':value,
                }
        """
        return {
            'name': line.get('label', line.get('ref', '/')),
            'date': line.get('date', datetime.now().date()),
            'amount': line.get('amount', 0.0),
            'ref': line.get('ref', '/'),
            'label': line.get('label', ''),
        }
