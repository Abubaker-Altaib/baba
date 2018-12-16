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


#----------------------------------------
#bonuses candidates
#----------------------------------------
class bonus_candidates(osv.osv_memory):
    _name ='hr.bonus.candidates'

    _columns = {
        'payroll_id': fields.many2one('hr.salary.scale','Salary Scale',required=True),
	    'margin': fields.integer('Margin',size=8,required=True),
        'date' :fields.date("Date", required= True),
        'type':fields.selection([('bonus_candidate', 'Bonus Candidate'), ('promotion_candidate', 'Promotion Candidate'),], "Type"),

       }



    def bonus_candidates(self,cr,uid,ids,context={}):
        """Method that retreives the candidated employees for the yearly bonuses 
           ( who complated one year in thier current bonus or more or those who have not complated one year but they fall in the margin).
        @return: Dictionary 
        """
        res={}
        for c in self.browse( cr, uid,ids):
            if c.type == 'bonus_candidate':
                
                pool = pooler.get_pool(cr.dbname)
                salary_degree_obj = pool.get('hr.salary.degree')
                salary_bonuses_obj = pool.get('hr.salary.bonuses')
                employee_obj = pool.get('hr.employee')
                bonus_candidate_obj = pool.get('hr.process.archive')
    	        obj_model = self.pool.get('ir.model.data')
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
                                                    check=bonus_candidate_obj.search(cr,uid,[('employee_id','=',employee.id),('reference','=', new_bonus.id  )])
                                                    if not check:
                                                        emp_bonus_dict = {
                                                             'employee_id': employee.id,
                                                             'employee_salary_scale' : employee.payroll_id.id,
                                                             'reference' : 'hr.salary.bonuses,'+str(new_bonus.id),
                                                             'days':days,
                                                             'code':employee.emp_code,
                                                             'date':c.date,
                                                             'previous':employee.bonus_id.name,
                                                             'company_id':employee.company_id.id,
                                                                         }
                                                        record_id = bonus_candidate_obj.create(cr, uid,emp_bonus_dict)
                                                        record_ids.append(record_id)
                                               
                tree_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_process_archive_tree_view')]) 
                tree_resource_id = obj_model.read(cr, uid, tree_model_data_ids, fields=['res_id'])[0]['res_id']      
                form_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_process_archive_form_view')]) 
                form_resource_id = obj_model.read(cr, uid, form_model_data_ids, fields=['res_id'])[0]['res_id']                                
                res= { 
    			'name': 'HR Process',
    			'view_type': 'form',
    			'view_mode': 'tree,form',
    			'res_model': 'hr.process.archive',
    			'views': [(tree_resource_id,'tree'),(form_resource_id,'form')],
    			'type': 'ir.actions.act_window',
    			'domain': [('id','in',record_ids)],
    		    }

    	        return res
            else:
                
                pool = pooler.get_pool(cr.dbname)
                salary_degree_obj = pool.get('hr.salary.degree')
                employee_obj = pool.get('hr.employee')
                degree_candidate_obj = pool.get('hr.process.archive')
                obj_model = self.pool.get('ir.model.data')
                record_ids = []
                degree_id=salary_degree_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id)],context=context)
                if degree_id:
                    for degrees in salary_degree_obj.browse(cr,uid,degree_id,context=context):
                        degree_ids = salary_degree_obj.search(cr,uid,[('id','=',degrees.id),('margin_time','>',0)],context=context)
                        
                        if degree_ids:
                            for degree in salary_degree_obj.browse(cr,uid,degree_ids,context=context):
                                new_sequence =degree.sequence-1
                                employee_ids = employee_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id),('degree_id','=',degrees.id)],context=context)
                                if employee_ids:
                                    new_degree_id= salary_degree_obj.search(cr,uid,[('sequence','=',new_sequence)],context=context)
                                    if new_degree_id:
                                        for new_degree in salary_degree_obj.browse(cr,uid,new_degree_id,context=context):
                                            for employee in employee_obj.browse(cr,uid,employee_ids,context=context):
                                                if not employee.promotion_date:
                                                    prev_degree_date = time.mktime(time.strptime(employee.employment_date,'%Y-%m-%d'))
                                                else:  
                                                    prev_degree_date = time.mktime(time.strptime(employee.promotion_date,'%Y-%m-%d'))
                                                candidate_date = time.mktime(time.strptime(c.date,'%Y-%m-%d'))
                                                diff_day = (candidate_date-prev_degree_date)/(3600*24)
                                                margin_day = degree.margin_time*365
                                                days= margin_day-diff_day
                                                if days <= c.margin :
                                                    check=degree_candidate_obj.search(cr,uid,[('employee_id','=',employee.id),('reference','=', new_degree.id  )])
                                                    if not check:
                                                        emp_degree_dict = {
                                                             'employee_id': employee.id,
                                                             'employee_salary_scale' : employee.payroll_id.id,
                                                             'reference' : 'hr.salary.degree,'+str(new_degree.id),
                                                             'days':days,
                                                             'code':employee.emp_code,
                                                             'date':c.date,
                                                             'previous':employee.degree_id.name,
                                                             'company_id':employee.company_id.id,
                                                                         }
                                                        #employee_obj.write(cr, uid,employee.id,{'promotion_date': c.date})
                                                        record_id = degree_candidate_obj.create(cr, uid,emp_degree_dict)
                                                        record_ids.append(record_id)
                                           
                tree_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_process_archive_tree_view')]) 
                tree_resource_id = obj_model.read(cr, uid, tree_model_data_ids, fields=['res_id'])[0]['res_id']      
                form_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_process_archive_form_view')]) 
                form_resource_id = obj_model.read(cr, uid, form_model_data_ids, fields=['res_id'])[0]['res_id']                                
                res= { 
                'name': 'HR Process',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.process.archive',
                'views': [(tree_resource_id,'tree'),(form_resource_id,'form')],
                'type': 'ir.actions.act_window',
                'domain': [('id','in',record_ids)],
                }
        
                return res
