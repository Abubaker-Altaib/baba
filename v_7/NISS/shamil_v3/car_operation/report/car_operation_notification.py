# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw

class car_operation_notification(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(car_operation_notification, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'line':self._getdoc,
            'line2':self._get_car_cost,
        })


    def _getdoc(self,num,num2):

       print ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,," , num
       self.cr.execute("""
           SELECT lc.document as doc FROM car_operation l
		   left join car_operation_line lc on (l.id = lc.operation_id)
		   where l.id = %s and lc.car_id = %s"""%(num,num2))

       res = self.cr.dictfetchall()
       return res
    def _get_car_cost(self,num):
	   self.cr.execute(""" select sum(l.cost) as total from car_operation_line l
                            where l.operation_id =%s"""%(num))

           res = self.cr.dictfetchall()
           return res

        
report_sxw.report_sxw('report.car_operation_notification','car.operation','addons/car_operation/report/car_operation_notification.rml',parser=car_operation_notification, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
