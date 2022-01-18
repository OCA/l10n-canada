Taxes included in expense
=========================
This module adds a checkbox to tax to include tax in expense invoices.
It is useful if your taxes are not included in the price, but you
want to ease the life of your employees by allowing them to enter
their expenses with the taxes included.

The tax calculation doesn't work in v7 and v8 for an expense. The expense now
create a voucher that only has one tax rate by voucher and we can't
safely select one tax rate per expense form. To fix this situation the
expense form should suport the taxes like a supplier invoice form and a
the end of the workflow produce a voucher and the journal entries like
what is done when a supplier invoice is open.

Contributors
------------
* Jonatan Cloutier <jonatan.cloutier@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
