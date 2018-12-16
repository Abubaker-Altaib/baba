# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class exchange_position_statistic(osv.osv_memory):
    _name = "exchange.position.statistic"
    _description = "Exchange Position Statistic Report"
    
    

    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'product_id' : fields.many2one('product.product','Product' ),
        'category_id' : fields.many2one('product.category','Category' ),
        'department_id' : fields.many2one('hr.department','Department' ),
        'location_id' : fields.many2one('stock.location' , 'Stock' ),
        'with_childern' : fields.boolean( 'With Childern' , ),
        'company_id' : fields.many2one('res.company','Company' ,readonly=True),


    }



    _defaults = {
                
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'exchange.position.statistic', context=c),

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
            'report_name': 'exchange_position_statistic_report',
            'datas': datas,
            }

    