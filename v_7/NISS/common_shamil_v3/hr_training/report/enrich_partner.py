import time
import pooler
import copy
from report import report_sxw
import pdb
import re
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar


class enrich_partner(report_sxw.rml_parse):
      	def __init__(self, cr, uid, name, context):
			super(enrich_partner, self).__init__(cr, uid, name, context=context)
			self.localcontext.update({
				'time': time,
            	'total':self._get_num,
            	'days':self._get_days,
				'convert':self._convert,
                      
               })
			self.context = context


    
   
#####################################################################################################

      	def _convert(self, amount, currency ):
			amt_en = amount_to_text_ar(amount, 'ar', currency.name ,'' )
			return amt_en
      	def _get_days(self,ids):
			o = pooler.get_pool(self.cr.dbname).get('hr.employee.training')
			cour =o.browse(self.cr, self.uid,[ids])[0]
			days=self.pool.get("hr.employee.training.line")._get_days(self.cr, self.uid,context={'start_date':cour.start_date, 'end_date':cour.end_date})
			#print ">>>>>>>>>>>>>>>>>>>>>>>>" ,days
			return days
		
      	def _get_num(self, ids):
			amount_list= []
			o = pooler.get_pool(self.cr.dbname).get('hr.employee.training')
			cour =o.browse(self.cr, self.uid,[ids])[0]
			emp_ids = self.pool.get('hr.employee.training.line').search(self.cr, self.uid, [('training_employee_id','=',cour.id)], context=self.context)
			num = self.pool.get('hr.employee.training.line').browse(self.cr, self.uid, emp_ids, context=self.context)
			return len(num)
           



report_sxw.report_sxw('report.enrich.partner', 'hr.employee.training.approved',
	'addons/hr_training/report/enrich_partner.rml', parser=enrich_partner, header=True)
