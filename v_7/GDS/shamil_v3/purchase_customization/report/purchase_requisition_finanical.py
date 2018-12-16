# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2016 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw
from osv import osv
import pooler
import string


class purchase_requisition_finanical(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(purchase_requisition_finanical, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_quote_count': self.get_quote_count,
            'convert_to_int' : self.convert_to_int,
        })
       

    def get_quote_count(self, order_obj):
        """ It Returns The Count Of Quote for Particular Order """
        self.cr.execute("""
                    select
                    count(quote.id) as num
                    from pur_quote quote
                    left join ireq_m ir on (ir.id=quote.pq_ir_ref)
                    where quote.pq_ir_ref=  %s
                    """,(order_obj.id,)) 
        res = self.cr.dictfetchone()
        
        return res
    
    
    def convert_to_int(self,num ):
       return int(num)




report_sxw.report_sxw('report.purchase_requisition_finanical', 'ireq.m' , 'addons/purchase_customization/report/purchase_requisition_finanical.rml', parser=purchase_requisition_finanical,header=False)

