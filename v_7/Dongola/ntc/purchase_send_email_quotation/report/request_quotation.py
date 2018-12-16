# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

#--------------------------------------------------------------
# class  purchase quotation report 
#--------------------------------------------------------------
import time
from report import report_sxw
import pooler
  
class request_quotation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(request_quotation, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,

        })

   
    
report_sxw.report_sxw('report.request_quotation_form','purchase.requisition','purchase_send_email_quotation/report/request_quotation.rml',parser=request_quotation)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
