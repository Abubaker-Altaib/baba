import time
from datetime import datetime
import re
import pooler
from report import report_sxw
import calendar
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _



class holi_certificate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(holi_certificate, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'line':self._get_holi,
                'line1':self._get_pars,
                'line2':self._get_pars_datetime,
        })
        self.cr = cr
        self.uid = uid
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        c='oo'
        for obj in self.pool.get('hr.holidays').browse(self.cr, self.uid, ids, self.context):
           c=obj.state
           absence=obj.holiday_status_id.absence
           #print">>>>>>>>>>>>>>>>>>>>>" ,obj.holiday_status_id.absence
        if (absence==True):
		   raise osv.except_osv(_('Error!'), _('You can not print the certificate. This is ABSENCE not Holiday!'))
        if (c!='validate'):
		    raise osv.except_osv(_('Error!'), _('You can not print the certificate. This Holiday is not approved yet !'))
        return super(holi_certificate, self).set_context(objects, data, ids ,report_type=report_type)

    def _get_holi(self,no1,no2):
          
           remind = int(no1 + no2)
           return remind

    def _get_pars(self,ids):
           top_result=[]
           res_data={}
           o = pooler.get_pool(self.cr.dbname).get('hr.holidays')
           hol_id =o.browse(self.cr, self.uid,[ids])[0]
           holiday_details = self.pool.get('hr.holidays.status').get_days(self.cr, self.uid, [hol_id.holiday_status_id.id], hol_id.employee_id.id, False, context=self.context)
           max_leaves = holiday_details.get(hol_id.holiday_status_id.id, {}).get('max_leaves', 0)
           leaves_taken = holiday_details.get(hol_id.holiday_status_id.id, {}).get('leaves_taken', 0)
           remaining = holiday_details.get(hol_id.holiday_status_id.id, {}).get('remaining_leaves', 0)
           if(hol_id.number_of_days < 0):
                   day_num = hol_id.number_of_days * -1
           else:
                   day_num = hol_id.number_of_days
           part_day = day_num
           res_data = {  
                         'complete_day': max_leaves,
                         'part_day': part_day,
                         'net_day': remaining,
                    }
           top_result.append(res_data)
           return top_result


    def _get_pars_datetime(self,t):
           d = datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
           day_string = d.strftime('%Y-%m-%d')
           
           return day_string
report_sxw.report_sxw('report.holi_certificate', 'hr.holidays', 'hr_holidays_custom/report/holi_certificate.rml' ,parser=holi_certificate ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
