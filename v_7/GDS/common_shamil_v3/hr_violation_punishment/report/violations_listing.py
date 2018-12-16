import time
import re
import pooler
from report import report_sxw
import calendar
import datetime


class violations_listing(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(violations_listing, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'lines2':self._getpunishment,
            'line':self._getShop,
            
        })
    
    
    def _getShop(self,data,p):
                  periods=[]
                  self.cr.execute('SELECT v.code as code  ,v.name as vio From hr_violation AS v where v.id=%s '%(p))
                  res = self.cr.dictfetchall()
                  return res

    def _getpunishment(self,data,p):
                  periods=[] ###violation_punish_id
                  self.cr.execute('select p.name as pun from hr_violation_punishment as vp left join hr_punishment as p on (punishment_id=p.id) where vp.violation_id=%s'%(p))
                  res = self.cr.dictfetchall()
                  return res
                     
                    
                

report_sxw.report_sxw('report.violations_listing', 'hr.violation', 'hr_violation_punishment/report/violations_listing.rml' ,parser=violations_listing,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

