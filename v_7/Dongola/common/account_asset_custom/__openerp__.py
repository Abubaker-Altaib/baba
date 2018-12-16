# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

{
    'name': 'Assets Management',
    'version': '1.0',
    'author': 'OpenERP S.A.',
    'description': """
Financial and accounting asset management.
==========================================

This Module add feature:
Sale
Abandon
Initial
Revalue.

    """,
    'website': 'http://www.nctr.sd',
    'category': 'Accounting & Finance',
    'sequence': 32,
    "depends" : ["account_asset","account_custom"],
    'demo': [],
    'test': [],
    'data': [
        'wizard/account_asset_reversed_view.xml',
        'views/account_asset_view.xml',
        'views/account_asset_config.xml',
        'wizard/account_report_asset_operation_view.xml',
        'wizard/asset_depreciation_wizard.xml',
        'wizard/account_asset_operation_view.xml',
        'wizard/account_data_migration_view.xml',
        'views/account_asset_location_view.xml',
        'wizard/asset_report.xml',


    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
