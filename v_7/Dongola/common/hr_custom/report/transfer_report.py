import time
import pooler
#import rml_parse
import copy
from report import report_sxw
import pdb
import re
from osv import fields, osv
from tools.translate import _

class transfer_report(report_sxw.rml_parse):
       _name = 'report.transfer.report'
       def __init__(self, cr, uid, name, context):
		super(transfer_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
                        '_get_emp':self._get_emp,
                      #  'line5':self.get_transfer_total,
               })

      # def get_transfer_total(self,data,choice,date1_v,date2_v):
        #   res = hr_common_report._archive_count(self,choice,'transfer_date','transfer_date',date1_v,date2_v)
         #  return res
    
       
       def _get_emp(self,data):

           date1 = data['form']['from']
           date2 = data['form']['to'] 
                      
           self.cr.execute('''SELECT d.name as current_dep, e.emp_code as code, 
ar.transfer_date AS date,r.name AS emp 
FROM hr_process_archive AS ar 
 join hr_employee AS e on (ar.employee_id=e.id) 
 join  resource_resource AS r on (e.resource_id=r.id)
 join hr_department as d  on (e.department_id=d.id) 
where 
to_char(ar.transfer_date,'YYYY-mm-dd') between (%s) and (%s)
''',(date1,date2)) 
           res = self.cr.dictfetchall()
           #print">>>>>>>>>>>>>>>>>>>>>>>>>res",res
           #   raise osv.except_osv('ERROR', 'There is No Employee Transfer This Month')
           #else:
           return res
      

report_sxw.report_sxw('report.transfer.report', 'hr.process.archive','addons/hr_process/report/transfer_report.rml', parser=transfer_report,header="custom landscape")
