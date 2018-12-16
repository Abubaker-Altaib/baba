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

class request_purchase(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(request_purchase, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'dept': self.get_department,
            'convert_to_int' : self.convert_to_int,
        })
    def get_department(self, order_obj):
    	dep = order_obj.department_id.id
    	if order_obj.department_id:
                self.cr.execute("""
                    select
                    dt.name as dept
                    from ireq_m ir
                	left join hr_department dt on (ir.department_id=dt.id)
                    where dt.id=  %s
                    """,(dep,)) 
                res = self.cr.dictfetchone()
    	else:
    	    res = True

        return res
    def convert_to_int(self,num ):
       return int(num)
report_sxw.report_sxw('report.ireq_m_request_purchase_custom','ireq.m','addons/purchase_customization/report/request_purchase.rml',parser=request_purchase,header=False)


