
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

class fuel_receive_notification(report_sxw.rml_parse):        
        

    def __init__(self, cr, uid, name, context):
        super(fuel_receive_notification, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })


    def _getdata(self,data):
	   num = data 
           self.cr.execute("""
                 select v.name as car_name , 
			r.purpose as purpose , 
			m.name as product , 
			m.product_qty as qty ,
			u.name as uom 


		from fuel_picking f 

			left join stock_move m on (m.fuel_picking_id = f.id)

			left join fuel_request r on (r.id = f.fuel_request_id)

			left join product_uom u on (m.product_uom = u.id)

			left join fuel_request_lines l on (l.fuel_id = r.id)

			left join fleet_vehicle v on (v.id = r.car_id)

		where f.id =%s and f.type='out' """%num) 
           res = self.cr.dictfetchall()
           return res
           
report_sxw.report_sxw('report.fuel_receive_notification.report','fuel.picking','addons/fuel_management/report/fuel_receive_notification.rml',parser=fuel_receive_notification,header='external')


