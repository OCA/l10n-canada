import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-l10n-canada",
    description="Meta package for oca-l10n-canada Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-res_country_state_translations_canada',
        'odoo10-addon-res_country_state_translations_us',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
