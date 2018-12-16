
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

class fuel_request_notification(report_sxw.rml_parse):        
        

    def __init__(self, cr, uid, name, context):
        super(fuel_request_notification, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
           
report_sxw.report_sxw('report.fuel_request_notification','fuel.request','addons/fuel_management/report/fuel_request_notification.rml',parser=fuel_request_notification,header='external')


