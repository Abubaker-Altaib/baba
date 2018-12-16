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
            'copy':self.make_copy,
        })
# generate the text of origin and copy
    def make_copy(self,para):
        return [{'no': 1,'text': 'ORIGINAL'},{'no': 2,'text': 'COPY',}]
    
report_sxw.report_sxw('report.purchase.order.report','purchase.order','purchase_wafi/report/order.rml',parser=order)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
