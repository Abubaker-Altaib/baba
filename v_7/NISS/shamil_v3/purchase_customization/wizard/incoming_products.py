# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class incoming_products_report(osv.osv_memory):
    _name = "incoming.products"
    _description = "Incoming Products Report"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    report_type = [
            ('amounts', 'Amounts'),
            ('quantities', 'Quantities'),
            ('both', 'Amounts & Quantities'),
            

                      ]

    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'category_id' : fields.many2one('product.category','Category' ),
        'product_id' : fields.many2one('product.product','Product' ),
        'department_id' : fields.many2one('hr.department','Department' ),
        'with_childern' : fields.boolean( 'With Childern' , ),
        'location_id' : fields.many2one('stock.location' , 'Stock' ),
        'company_id' : fields.many2one('res.company','Company' ,readonly=True),
        'supplier_id' : fields.many2one('res.partner','Supplier'),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
        'report_type' : fields.selection(report_type ,'Report Type ',select=True,required=True),


    }



    _defaults = {
                
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'incoming.products', context=c),
                'report_type' : 'both',  
                'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,

              }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'stock.picking',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'incoming_products_report',
            'datas': datas,
            }

    
