# -*- coding: utf-8 -*-
{
    'name': "stock_custom",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','stock_landed_costs','purchase_requisition','hr','stock_account'],

    # always loaded
    'data': [
        
        #'security/ir.model.access.csv',
	'security/stock_groups.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizard/stock_create_requestion_wizard _view.xml',
	'wizard/stock_backorder_wizard_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
