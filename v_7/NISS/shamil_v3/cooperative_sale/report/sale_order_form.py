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


class sale_order_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_order_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert_to_int' : self.convert_to_int,
        })


    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('sale.order').browse(self.cr, self.uid, ids):
            if obj.state != 'done' or obj.print_order == True:
                    raise osv.except_osv(_('Error!'), _('You can not print this Receipt'))
	    else :
		notes =""
        	note =""
        	if obj.note :
		 	note = obj.note
		u = self.pool.get('res.users').browse(self.cr, self.uid,self.uid).name
		notes = note +'\n'+'Sale Order Printed at : '+time.strftime('%Y-%m-%d %H:%M:%S') + ' by '+ u
		self.pool.get('sale.order').write(self.cr ,self.uid , obj.id , {'print_order':True,'note':notes}) 

        return super(sale_order_form, self).set_context(objects, data, ids, report_type=report_type) 
    
    def convert_to_int(self,num):         
        return int(num)

report_sxw.report_sxw('report.sale_order_form','sale.order','addons/cooperative_sale/report/sale_order_form.rml',parser=sale_order_form,header=False)


