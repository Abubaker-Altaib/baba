import time
from report import report_sxw
from openerp.osv import osv
import pooler

class transportation_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(transportation_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
       	    'line4':self._getdata4,
       	    'line3':self._getdata3,
       	    'line2':self._getdata2,

        })
# Driver
    def _getdata3(self,data):
	   num=data
           self.cr.execute(""" SELECT a.driver_name as driver FROM transportation_driver a where a.transportation_id  =%d """%num) 
           res = self.cr.dictfetchall()
           return res
#Supplier

    def _getdata4(self,data):
	   num=data
           self.cr.execute(""" SELECT a.street as street FROM res_partner a where a.id  =%d """%num) 
           res = self.cr.dictfetchall()
           return res
# Quota
    def _getdata2(self,data):
	   num=data
           self.cr.execute(""" SELECT a.name as quote FROM transportation_quotes a where a.transportation_id  =%d and a.state='done' """%num) 
           res = self.cr.dictfetchall()
           return res


report_sxw.report_sxw('report.transportation_report','transportation.order','purchase_transportation/report/transportation_report.rml',parser=transportation_report,header=False)

