# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class sale_order_all_report(osv.osv_memory):
    _name = "sale.order.all.report"
    _description = "Sale Order All"
    
    report_type = [
            ('police', 'Police'),
            ('individual', 'Individual'),
            ('both', 'Both'),
            

                      ]

    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'category_id' : fields.many2one('sale.category','Category' ),
        'location_id' : fields.many2one('sale.shop' , 'Stock' ),
        'company_id' : fields.many2one('res.company','Company' ,readonly=True),
        'scale_id' : fields.many2one('hr.salary.scale' ,'Report Type',select=True,required=True),
        'payment_type': fields.selection([('cash', 'Cash'),('installment', ' Installment'),('up_cash', 'Upfront only')], 'Payment type', required=True,select=True),
        'receive_state': fields.selection([('done', 'Done'),('not', 'Not Done'),], 'Receive state',select=True),
        'emp_id' : fields.many2one('hr.employee','Employee'),
        'report_type': fields.selection([('deliver', 'Delivery Report'),('statistical', 'Statistical Report'),('deduction', 'Deduction Report'),], 'Report type', required=True,select=True,readonly=True),


    }
    _defaults = {
		'report_type':'deduction',
		'receive_state':'done',                                
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'incoming.products', context=c),
               

              }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'sale.order',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sale_order_all_report',
            'datas': datas,
            }

    
