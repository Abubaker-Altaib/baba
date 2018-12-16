# -*- coding: utf-8 -*-
{
    'name': "sale_custom",

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
    'depends': ['base','sale','product','purchase','sale_management','sale_crm'],

    # always loaded
    'data': [
        'security/sale_security.xml',
        'security/ir.model.access.csv',
        'report/quotation_order_customer_template.xml',
        'report/quotation_order_financial_template.xml',
        'views/views.xml',
        'views/templates.xml',
        #'wizard/certificate_invoice_wizard_view.xml',
        'views/certificate_quotation_view.xml',
        'report/action_certificate.xml',
        'report/sale_certificate_quotation_template.xml',
        'report/sale_certificate_invoice_template.xml',
        'report/services_pivot_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
