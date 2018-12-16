# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class stock_cooperative_delivery_orders_report(osv.osv_memory):
    _name = "stock.cooperative.delivery.orders.report"
    _description = "Stock Cooperative Delivery Orders Report"

    shippment_status = [
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Transfer'),
            ('done', 'Transferred'),

                      ]

    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'supplier_id' : fields.many2one('res.partner','Supplier' ),
        'product_id' : fields.many2one('product.product','Product',required=True,),
        'company_id' : fields.many2one('res.company','Company',readonly=True ),
        'location_id' : fields.many2one('stock.location' , 'Source',),
        'location_dest_id' : fields.many2one('stock.location' , 'Destination',),
        'state' : fields.selection(shippment_status ,'Shippment Status',select=True),
        'print_order': fields.boolean('order Printed',), 
        'print_finance': fields.boolean('Finance Printed',), 


    }



    _defaults = {
                'state':'done',
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.cooperative.delivery.orders.report', context=c),
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
            'report_name': 'cooperative_stock_delivery_orders_report',
            'datas': datas,
            }
stock_cooperative_delivery_orders_report()
    
