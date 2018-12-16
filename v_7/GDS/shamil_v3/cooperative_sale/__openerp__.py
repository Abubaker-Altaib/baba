# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2012-2013 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Cooperative Sale Management Custom',
    'version': '1.0',
    'category': 'Cooperative Sale Management',
    'description': """
			
		   """,
    'author': 'NCTR',
    'website': 'http://www.nctr.sd',
    'depends': ['sale_stock','hr_loan','hr_custom','hr_payroll_custom','cooperative_account'],
    'init_xml': [],
    'data': [
           'security/co_operative_sales_groups.xml',
           'sale.xml',
           'sale_workflow.xml',
           'sale_report.xml',
           'hr_employee_loan_workflow.xml',
           'wizard/sale_order_all_report.xml',
           'wizard/compute_employee_loan.xml',
           'wizard/sale_order_cancel.xml',
           'wizard/sale_order_representive.xml',
           'wizard/sale_order_representive_sale_fin.xml',
           'wizard/sale_order_all_report_summary.xml',
           'wizard/sale_order_process.xml',
          

    ],
   'test': [],
    
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
