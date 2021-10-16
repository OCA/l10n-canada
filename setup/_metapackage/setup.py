import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-l10n-canada",
    description="Meta package for oca-l10n-canada Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-hr_expense_line_supplier',
        'odoo8-addon-l10n_ca_account_check_writing',
        'odoo8-addon-l10n_ca_qc_account_fiscal_position_rule',
        'odoo8-addon-l10n_ca_toponyms',
        'odoo8-addon-res_currency_print_on_check',
        'odoo8-addon-res_partner_attributes_add_BN',
        'odoo8-addon-res_partner_attributes_add_NEQ',
        'odoo8-addon-res_partner_attributes_add_SIN',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
