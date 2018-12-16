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


class tech_department_tender(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(tech_department_tender, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_quote_count': self.get_quote_count,
            'convert_to_int' : self.convert_to_int,
        })
       
        
    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('ireq.m').browse(self.cr, self.uid, ids):
            if obj.executing_agency != 'tech':
                    raise osv.except_osv(_('Error!'), _('You can not print this report')) 

        return super(tech_department_tender, self).set_context(objects, data, ids, report_type=report_type) 
   
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
report_sxw.report_sxw('report.tech_department_tender','ireq.m','addons/purchase_customization/report/tech_department_tender.rml',parser=tech_department_tender,header=False)


