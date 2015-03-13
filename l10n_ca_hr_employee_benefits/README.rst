Canada Employee Benefits
========================

This module implements an employee benefits in order to produce employee payslips.

Employee benefits are computed automatically at a specific point in a payroll structure.
They are set at the job level or directly on each employee contract.

Also, they can be added manually on a payslip.

Benefits may be computed from the gross salary of the payslip or from the number of hours done on each specific job from the worked days. They also can be fixed amount (annual or periodic).

If a benefit has 2 different rates in the same payslip period, the 2 rates will be weighted by the fraction of the payslip over which they apply.


Installation
============

Only install the module.


Usage
=====

* Go to Human Resources -> Configuration -> Payroll -> Employee Benefit Categories
* Create your own employee benefit.
* Select the salary rules over which the benefit will be summed.
* Add exemption if it is exempted from one or many income taxes.
* Add as many different rates as needed.

* On a job or contract of an employee, add employee benefits
* Select the category of benefit, the rate and dates between which the benefit will be activated.


Known issues / Roadmap
======================

An employee benefit line on a contract or a job must be active during the full period of the payslip to be computed. Otherwise, it will be ignored.


Credits
=======

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
