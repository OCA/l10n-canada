# -*- coding: utf-8 -*-
# Copyright (C) 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Supplier on Expense Line",
    "version": "8.0.1.0.0",
    "category": "Human Resources",
    "author": (
        "Savoir-faire Linux,"
        "Odoo Community Association (OCA)"
    ),
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "depends": ['hr_expense'],
    "data": [
        'views/hr_expense_line.xml',
    ],
    "demo": [
        'demo/hr_expense_line.xml',
    ],
    "installable": True,
}
