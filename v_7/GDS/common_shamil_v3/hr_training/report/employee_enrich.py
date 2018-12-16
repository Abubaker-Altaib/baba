# -*- coding: utf-8 -*-import time
import pooler
import copy
from openerp.report import report_sxw
import pdb
import re
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm
import time

class employee_enrich(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
		super(employee_enrich, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
            'total':self._get_total,
                      
               })
		self.context = context


    
   
#####################################################################################################

      def set_context(self, objects, data, ids, report_type=None):
        	for obj in self.pool.get('hr.employee.training.approved').browse(self.cr, self.uid, ids, self.context):
           		c=obj.state
        		if (c!='done'):
        			raise osv.except_osv(_('Error!'), _('You can not print ..This report available only if state is done!'))
        	return super(employee_enrich, self).set_context(objects, data, ids ,report_type=report_type)
		
      def _get_total(self, ids):
			amount_list= []
			o = pooler.get_pool(self.cr.dbname).get('hr.employee.training')
			cour =o.browse(self.cr, self.uid,[ids])[0]
			emp_ids = self.pool.get('hr.employee.training.line').search(self.cr, self.uid, [('training_employee_id','=',cour.id)], context=self.context)
			f_amount = self.pool.get('hr.employee.training.line').browse(self.cr, self.uid, emp_ids, context=self.context)
			for f in f_amount :
				total = sum(ca.final_amount for ca in f_amount)
				dic = { 'total' : total , }
			amount_list.append(dic)
			return amount_list[0]['total']
           



report_sxw.report_sxw('report.employee.enrich', 'hr.employee.training.approved',
	'addons/hr_training/report/employee_enrich.rml', parser=employee_enrich, header=True)
