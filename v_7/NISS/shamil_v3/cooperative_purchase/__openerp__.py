# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name' : 'Cooperative Purchase Management Custom',
    'version' : '1.0',
    'author' : 'Nctr',
    'category' : 'Cooperative Purchase',
    'description' : "" "Cooperative Purchase" "",
    'website': 'http://www.nctr.sd',
    'depends' : ['base','purchase_contracts','cooperative_stock'],
    'data': [
             'security/co_operative_groups.xml',
             'co_operative_contract_view.xml',  
             'wizard/contracts_info.xml',
             'Purchase_co_operative_report.xml',
             'workflow/purchase_co_operative_contract_workflow.xml', 
             'workflow/purchase_co_operative_contract_fees_workflow.xml',
             ],
    'installable': True,
    'active': False,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
