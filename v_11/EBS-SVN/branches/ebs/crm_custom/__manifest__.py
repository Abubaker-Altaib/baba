# -*- coding: utf-8 -*-
{
    'name': "crm_custom",

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
    'depends': ['base','crm','sale_custom','purchase_requisition','purchase','account','account_invoice_custom','purchase_ebs'],

    # always loaded
    'data': [
        'security/crm_security.xml',
        # 'security/ir.model.access.csv',
        'wizard/customer_invoice_wizard_view.xml',
        'wizard/cancel_pr.xml',
        'report/quotation_order_invoice_report.xml',
        'report/action_customer_invoice_report.xml',
        'report/template_customer_invoice_report.xml',
        'report/template_invoice_details_report.xml',
        'report/action_invoice_details_report.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/certificate_quotation_view.xml',
        'views/card_quotation_view.xml',
        'views/crm_menu_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
