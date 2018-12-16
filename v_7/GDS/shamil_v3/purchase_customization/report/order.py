# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

#--------------------------------------------------------------
# class to customising purchase order report 
#--------------------------------------------------------------
import time
from report import report_sxw
import pooler
  
class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'inv': self.invoice,
            'convert_to_int' : self.convert_to_int,
            #'copy':self.make_copy,
        })
# generate the text of origin and copy
    """def make_copy(self,para):
        return [{'no': 1,'text': 'ORIGINAL'},{'no': 2,'text': 'COPY',}]"""
    
    def invoice(self, order_obj):
        self.pool.get('purchase.order').write(self.cr, self.uid,order_obj.id,{'test_report_print':'printed'})
        pur_inv = [x.id for x in order_obj.invoice_ids]
        invoices=''
        for inv_id in pur_inv:
            inv_ref = self.pool.get('account.invoice').browse(self.cr, self.uid, inv_id).number
            invoices = invoices + '\n' +inv_ref
        return invoices
    def convert_to_int(self,num ):
       return int(num)
report_sxw.report_sxw('report.purchase_order_report','purchase.order','purchase_customization/report/order.rml',parser=order,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
