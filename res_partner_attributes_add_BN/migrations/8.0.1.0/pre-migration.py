# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import release
import logging
logger = logging.getLogger('upgrade')
logger.setLevel(logging.DEBUG)

column_spec = {
    'res_partner': [
        ("ne", "bn"),
    ],
}


def get_legacy_name(original_name):
    """
    Returns a versioned name for legacy tables/columns/etc
    Use this function instead of some custom name to avoid
    collisions with future or past legacy tables/columns/etc
    :param original_name: the original name of the column
    :param version: current version as passed to migrate()
    """
    return 'openupgrade_legacy_'+('_').join(
        map(str, release.version_info[0:2]))+'_'+original_name


def rename_columns(cr, column_spec):
    """
    Rename table columns. Typically called in the pre script.
    :param column_spec: a hash with table keys, with lists of tuples as \
    values. Tuples consist of (old_name, new_name). Use None for new_name \
    to trigger a conversion of old_name using get_legacy_name()
    """
    for table in column_spec.keys():
        for (old, new) in column_spec[table]:
            if new is None:
                new = get_legacy_name(old)
            logger.info("table %s, column %s: renaming to %s",
                        table, old, new)
            cr.execute(
                'ALTER TABLE "%s" RENAME "%s" TO "%s"' % (table, old, new,))
            cr.execute('DROP INDEX IF EXISTS "%s_%s_index"' % (table, old))


def migrate(cr, version):
    if version is None:
        return
    rename_columns(cr, column_spec)
