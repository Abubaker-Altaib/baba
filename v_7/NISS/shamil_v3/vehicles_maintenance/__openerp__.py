# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Vehicles Maintenance',
    'version': '1.1',
    'author': 'NCTR',
    'category': 'Vehicles',
    'website': 'http://www.nctr.sd',
    'summary': 'Vehicles Maintenance',
    'depends': ['admin_affairs', 'stock_inventory','procurment_oc', 'stock_oc'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/stock_return_picking_view.xml',
	    'views/spare_part.xml',
        'views/maintenance_departments.xml',
        'views/maintenance_process.xml',
        'views/stock_exchange_view.xml',
        'reports/maintenance_report.xml',
        'data/sequance.xml',
        'workflows/maintenance_request_workflow.xml',
        'workflows/maintenance_job_workflow.xml',
        'wizards/maintenance_report_wizard_view.xml',
        'wizards/vehicles_report_wizard_view.xml',
        'wizards/spares_report_wizard_view.xml',
        'views/purchase_view.xml',
        'workflows/purchase_workflow.xml',
        'workflows/stock_exchange_workflow.xml',
        'wizards/spare_movements_wizard_view.xml',
        'sequance_definition.xml',
        'wizards/maintenance_stock_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
