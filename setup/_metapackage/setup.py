import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-l10n-canada",
    description="Meta package for oca-l10n-canada Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-l10n_ca_toponyms',
        'odoo9-addon-res_partner_attributes_add_BN',
        'odoo9-addon-res_partner_attributes_add_NEQ',
        'odoo9-addon-res_partner_attributes_add_SIN',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
