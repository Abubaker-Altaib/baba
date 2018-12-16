# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp import pooler
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta



#----------------------------------------
#bonuses candidates
#----------------------------------------
class bonus_candidates(osv.osv_memory):
	_inherit ='hr.bonus.candidates'


	def bonus_candidates(self,cr,uid,ids,context={}):
		"""
		inherit this Method to sparate bonus_candidates from promotion_candidates 
		Method that retreives the candidated employees for the yearly bonuses 
			   ( who complated one year in thier current bonus or more or those who have not complated one year but they fall in the margin).
			@return: Dictionary 
		"""
		for c in self.browse( cr, uid,ids):
			pool = pooler.get_pool(cr.dbname)
			obj_model = self.pool.get('ir.model.data')
			salary_degree_obj = pool.get('hr.salary.degree')
			salary_bonuses_obj = pool.get('hr.salary.bonuses')
			employee_obj = pool.get('hr.employee')
			bonus_candidate_obj = pool.get('hr.movements.bonus')
			record_ids = []
			degree_ids=salary_degree_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id)],context=context)
			if degree_ids:
				for degree in salary_degree_obj.browse(cr,uid,degree_ids,context=context):
					bonus_ids = salary_bonuses_obj.search(cr,uid,[('degree_id','=',degree.id),('margin_time','>',0)],context=context)
					if bonus_ids:
						for bonus in salary_bonuses_obj.browse(cr,uid,bonus_ids,context=context):
							new_sequence =bonus.sequence+1
							employee_ids = employee_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id),('degree_id','=',degree.id),('bonus_id','=',bonus.id)],context=context)
							if employee_ids:
								new_bonus_id= salary_bonuses_obj.search(cr,uid,[('degree_id','=',degree.id),('sequence','=',new_sequence)],context=context)
								if new_bonus_id:
									for new_bonus in salary_bonuses_obj.browse(cr,uid,new_bonus_id,context=context):
										for employee in employee_obj.browse(cr,uid,employee_ids,context=context):
											if not employee.bonus_date:
												prev_bonus_date = time.mktime(time.strptime(employee.employment_date,'%Y-%m-%d'))
											else:  
												prev_bonus_date = time.mktime(time.strptime(employee.bonus_date,'%Y-%m-%d'))
											candidate_date = time.mktime(time.strptime(c.date,'%Y-%m-%d'))
											diff_day = (candidate_date-prev_bonus_date)/(3600*24)
											days= bonus.margin_time-diff_day
											if days <= c.margin :
												check=bonus_candidate_obj.search(cr,uid,[('employee_id','=',employee.id),('reference','=', new_bonus.id)])
												if not check:
													emp_bonus_dict = {
														 'employee_id': employee.id,
														 'employee_salary_scale' : employee.payroll_id.id,
														 'reference' : new_bonus.id,
														 'code':employee.emp_code,
														 'date':c.date,
														 'last_bonus_id':employee.bonus_id.name,
														 'company_id':employee.company_id.id,
																	 }
													record_id = bonus_candidate_obj.create(cr, uid,emp_bonus_dict)
													record_ids.append(record_id)
											   
				tree_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_movements_bouns_tree_view')]) 
				tree_resource_id = obj_model.read(cr, uid, tree_model_data_ids, fields=['res_id'])[0]['res_id']      
				form_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_movements_bonus')]) 
				form_resource_id = obj_model.read(cr, uid, form_model_data_ids, fields=['res_id'])[0]['res_id']                                
				res= { 
				'name': 'HR Movements Bouns',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'hr.movements.bonus',
				'views': [(tree_resource_id,'tree'),(form_resource_id,'form')],
				'type': 'ir.actions.act_window',
				'domain': [('id','in',record_ids)],
				}

				return res
