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

class sale_order_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_order_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert_to_int' : self.convert_to_int,
        })
    
    def convert_to_int(self,num ):
       return int(num)
report_sxw.report_sxw('report.sale_order_form','sale.order','addons/cooperative_sale/report/sale_order_form.rml',parser=sale_order_form,header=False)


