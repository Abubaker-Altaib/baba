import time
import re
import pooler
from report import report_sxw
import calendar
import datetime


class service_duration(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(service_duration, self).__init__(cr, uid, name, context)
        self.localcontext.update({
        	'line': self._get_data,
                          
        })
#------------------------------- line----------------------------------   
    def _get_data(self,data):
        res=[]
        days=0
        years=0
        months=0

        res_days=0
        res_months=0
        res_years=0

        sdays=data.separated_service_days
        smonths=data.separated_service_months
        syears=data.separated_service_years

        cday=data.connected_service_days
        cmonths=data.connected_service_months
        cyears=data.connected_service_years

        res_years=syears+cyears
        days=sdays+cdays
        if days > 30:
        	res_days=days%30
        	res_months=days/30
        else:
        	res_days=days

        months=smonths+cmonths
        if months >12:
        	res_months=months%12
        	res_years=months/12
        else:
        	res_months=months

        res = {'add_days':res_days,'add_months':res_months,'add_years':res_years}
        print">>>>>>>>>>>>>>>>>>>>>>>>>res",res
        return res
   
 
report_sxw.report_sxw('report.service_duration', 'hr.employee', 'hr_custom/report/service_duration.rml' ,parser=service_duration ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
