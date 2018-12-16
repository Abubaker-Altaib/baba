# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler
from tools.translate import _



class sale_receipt(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_receipt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_sum' : self.get_sum,
            #'print_log' : self.print_log,
        })
    



    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('sale.order').browse(self.cr, self.uid, ids):
            if obj.state != 'done' or obj.print_order == True:
                    raise osv.except_osv(_('Error!'), _('You can not print this Receipt')) 

        return super(sale_receipt, self).set_context(objects, data, ids, report_type=report_type) 

    def get_sum(self,order_id):
        sale_rec = self.pool.get('sale.order').browse(self.cr,self.uid,[order_id])[0]
        sum_qty = 0
        sum_advance = 0
        sum_installment = 0
        sum_period = 0
        res = {}
        if sale_rec.order_line:
           for line in sale_rec.order_line :
                sum_qty += line.product_uom_qty
                sum_advance += line.up_front
                sum_installment += line.installment_value
                sum_period += line.period

           res = {

                'sum_qty' :  int(sum_qty),
                'sum_advance' : int(sum_advance),
                'sum_installment' : int(sum_installment),
                'sum_period' : int(sum_period),




                }
	notes =""
        note =""	              
        if sale_rec.note :
		 note = sale_rec.note
	u = self.pool.get('res.users').browse(self.cr, self.uid,self.uid).name
	notes = note +'\n'+'Sale Order Printed at : '+time.strftime('%Y-%m-%d %H:%M:%S') + ' by '+ u
	self.pool.get('sale.order').write(self.cr ,self.uid , sale_rec.id , {'print_order':True,'note':notes})
                
        return res

      

         
report_sxw.report_sxw('report.sale_receipt','sale.order','addons/cooperative_sale/report/sale_receipt.rml',parser=sale_receipt,header=False)


