# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class purchases_suppliers_report(osv.osv_memory):
    _name = "purchases.suppliers.report"
    _description = "Purchases Suppliers Report"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    

    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'category_id' : fields.many2one('product.category','Category' ),
        'product_id' : fields.many2one('product.product','Product' ),
        'department_id' : fields.many2one('hr.department','Department' ),
        'company_id' : fields.many2one('res.company','Company' ,readonly=True),
        'supplier_id' : fields.many2one('res.partner','Supplier' ,),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),



    }



    _defaults = {
                
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchases.suppliers.report', context=c),
                'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,

              }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchases_suppliers_report',
            'datas': datas,
            }

    
