import time
from datetime import datetime
import re
import pooler
from report import report_sxw
import calendar
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
import time
import datetime
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT



class holi_certificate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(holi_certificate, self).__init__(cr, uid, name, context)
        record = self.get_record()
        self.localcontext.update(record)

    def get_record(self):
      res = {}
      for i in self.pool.get('hr.holidays').browse(self.cr , self.uid , [self.context['active_id']]) :
            res['name'] = i.employee_id.name_related 
            res['code'] = i.employee_id.otherid or "" 
            res['degree'] = i.employee_id.degree_id.name 
            res['place'] = i.place_id.name or ""
            res['holi_days'] = i.number_of_days_temp
            res['street_days'] = i.street_days
            res['total_days'] = i.total_days
            res['date_from'] = datetime.datetime.strptime(i.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
            res['date_to'] = datetime.datetime.strptime(i.date_to, DEFAULT_SERVER_DATETIME_FORMAT).date()
            res['seq'] = i.sequence or "" 
            res['holi_type'] = i.holiday_status_id.name or "" 
            res['date'] = datetime.date.today().strftime('%Y-%m-%d')
            res['from_company2department']=self.from_company_to_department(self.uid)
      return res

    def from_company_to_department(self,uid):
        emp_obj=self.pool.get('hr.employee')
        dept_obj=self.pool.get('hr.department')
        emp=emp_obj.search(self.cr, self.uid, [('user_id','=',uid)])
        res = ""
        employee = emp_obj.browse(self.cr, self.uid, emp[0])
        reads=dept_obj.name_get(self.cr, self.uid, [employee.department_id.id])
        res+= employee.company_id.name + '<br/>' 
        departments=reads[0][1].split(' / ')
        for dept in departments:            
            dept_res=dept_obj.search(self.cr, self.uid, [('name','ilike',dept.encode('utf-8')),('cat_type','in',['department','corp','aria'])])
            if dept_res:
                res+=dept.encode('utf-8')+'<br/>'
            else:
                break
        return res

# remove previous report.holi_certificate service :
#from netsvc import Service
#del Service._services['report.holi_certificate']

report_sxw.report_sxw('report.holi_certificate_military', 'hr.holidays', 'addons/hr_custom_military/report/holi_certificate.mako' ,parser=holi_certificate ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
