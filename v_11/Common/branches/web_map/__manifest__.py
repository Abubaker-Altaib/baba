# -*- coding: utf-8 -*-
{
    'name': 'Web Map',
    'version': '0.1',
    'category': 'Extra Tools',
    'summary': 'Map widget',
    'description': """
Odoo Web Map view
==========================
Support following feature:
    * Google Maps widget
    * Add multiple maps to form view
    * Readonly mode
    * Edit mode
    """,
    'author': 'CodUP',
    'license': 'AGPL-3',
    'website': 'http://codup.com',
    'sequence': 0,
    'depends': ['base_setup','web', 'website_google_map'],
    'data': [
        'views/web_map_templates.xml',
        #'views/res_config_views.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: