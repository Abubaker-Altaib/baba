# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class contracts_info_report(osv.osv_memory):
    _name = "contracts.info.report"
    _description = "Stock Cooperative Delivery Orders Report"

    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'state' : fields.selection([('draft', 'Draft'),
	   			    ('confirmed', 'Confirmed'),
                                    ('done', 'Done'),
                                    ('cancel', 'Cancel'), ] ,'Contract Status'),
        'fees_state': fields.selection([('draft','Draft'),('confirm','Confirmed'),('done','Done'),('cancel','Cancel')],'Bill State'),               
        'picking_policy': fields.selection([('partial','Partial Delivery'),('complete','Complete Delivery')],'Picking Policy'),
        'delivery_method': fields.selection([('air_freight', 'Air Freight'),
					     ('sea_freight', 'Sea Freight'),
					     ('land_freight', 'Land Freight'),], 'Method of dispatch'),
        'supplier_ids' : fields.many2many('res.partner','info_supplier','info_id','supplier_id','Suppliers' ),
        'company_ids' : fields.many2many('res.company','info_company_rel','info_id','company_id','Company' ),
        'contract_ids' : fields.many2many('purchase.contract' , 'info_contract_rel','info_id','contract_id','Contractes',),

  }



    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.contract',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'contracts.info',
            'datas': datas,
            }

    
