import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-l10n-canada",
    description="Meta package for oca-l10n-canada Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-l10n_ca_states_translations',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
