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
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar
from tools.translate import _


class ratification_request(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ratification_request, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_amount' : self.get_amount,
            'get_amount_written' : self.convert,
            
        })
        
        
    def get_amount(self,record):
        total = 0.0
        if not record.multi :
           raise osv.except_osv(('Printing Error !'),('The Request Not Arrived in Quotes State Yet ...'))
        else :
            for quote in record.q_ids :
                if quote.state == 'done' :
                    total += quote.amount_total
        return total
    
    
    def convert(self, amount_total):
        return amount_to_text_ar(amount_total)
    
    
    


report_sxw.report_sxw('report.ratification_request', 'ireq.m', 'purchase_customization/report/ratification_request.rml', parser=ratification_request,header=False)

