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
class hr_promotions_candidates(osv.osv_memory):
    _name ='hr.promotions.candidates'

    _columns = {
    'degree_from': fields.many2one('hr.salary.degree','Degree From'),
	'degree_to': fields.many2one('hr.salary.degree','Degree To'),
	'academic': fields.boolean('Academic'),
	'qual': fields.many2one('hr.qualification','qualification'),
	'isolated' : fields.boolean('Don\'t Include The Isolated'),
	'ruling' : fields.boolean('Ruling'),
	'rebuke':fields.selection([('strong','Strong'),('simple', 'simple')] ,'Rebuke'),  
    'payroll_id': fields.many2one('hr.salary.scale','Salary Scale',required=True),
    'margin': fields.integer('Margin',size=8,required=True),
    'date' :fields.date("Date", required= True),
       }

    def onchange_degree_from(self, cr, uid, ids, degree_from, absence=False,context=None):
        """
        Set degree_to.

        @param emp_id: Id of degree_from
        @return: Dictionary of values 
        """
        salary_degree_obj = self.pool.get('hr.salary.degree')
        value = {}
        if degree_from:
            for degrees in salary_degree_obj.browse(cr,uid,[degree_from],context=context):
                new_sequence =degrees.sequence-1
                new_degree_id= salary_degree_obj.search(cr,uid,[('sequence','=',new_sequence)],context=context)
                if new_degree_id:
                    value['degree_to']=new_degree_id[0]
        return {'value':value}



    def promotions_candidates(self,cr,uid,ids,context={}):
        """Method that retreives the candidated employees for the promotions.
           @return: Dictionary 
        """
        for c in self.browse( cr, uid,ids):
            pool = pooler.get_pool(cr.dbname)
            salary_degree_obj = pool.get('hr.salary.degree')
            salary_bonuses_obj = pool.get('hr.salary.bonuses')
            employee_obj = pool.get('hr.employee')
            violation_obj = pool.get('hr.employee.violation')
            movements_obj = pool.get('hr.movements.degree')
            obj_model = self.pool.get('ir.model.data')
            record_ids = []
            employee_ids =[]
            degree_id=[]
            if c.degree_from and c.degree_to:
               degree_id.append(c.degree_from.id)
            else:
               degree_id=salary_degree_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id)],context=context)
            if degree_id:
                for degrees in salary_degree_obj.browse(cr,uid,degree_id,context=context):
                    if c.degree_from:
                        new_sequence =c.degree_to.sequence
                    else:
                        new_sequence =degrees.sequence-1

                    #Isolated employee is included after one year
                    if not c.isolated:
                        employee_ids = employee_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id),('degree_id','=',degrees.id),('is_isolated','=',True),('state','=','approved')],context=context)
                        temp_employee_ids=[]
                        for emp in employee_obj.browse(cr,uid,employee_ids,context=context):
                            if emp.is_isolated:
                                if emp.promotion_date:
                                    df=datetime.strptime(emp.promotion_date,'%Y-%m-%d')
                                else:
                                    df=datetime.strptime(emp.employment_date,'%Y-%m-%d')
                                dt=datetime.strptime(c.date,'%Y-%m-%d')
                                date=relativedelta(dt,df)
                                years=date.years
                                if years >= 1:
                                    temp_employee_ids.append(emp.id)
                        employee_not_isolated = employee_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id),('degree_id','=',degrees.id),('is_isolated','=',False),('state','=','approved')],context=context)
                        employee_ids=temp_employee_ids+employee_not_isolated
                    else:
                        employee_ids = employee_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id),('degree_id','=',degrees.id),('is_isolated','=',False),('state','=','approved')],context=context)
                    
                    # employee that have ruling is not included
                    if not c.ruling:
                        temp_employee_ids=[]
                        for emp in employee_obj.browse(cr,uid,employee_ids,context=context): 
                                violation = violation_obj.search(cr,uid,[('employee_id','=',emp.id)],context=context)
                                if not violation:
                                    temp_employee_ids.append(emp.id)
                        employee_ids=temp_employee_ids
                    else:
                        temp_employee_ids=[]
                        for emp in employee_obj.browse(cr,uid,employee_ids,context=context): 
                            violation = violation_obj.search(cr,uid,[('employee_id','=',emp.id)],context=context)
                            if violation:
                                employee_ids.append(emp.id)
                        employee_ids+=temp_employee_ids
                        employee_ids=list(set(employee_ids))
                    if c.academic:
                        temp_employee_ids=[]
                        for emp in employee_obj.browse(cr,uid,employee_ids,context=context): 
                            for qual in emp.qualification_ids:
                                if qual.emp_qual_id.parent_id.id == c.qual.id:
                                    temp_employee_ids.append(emp.id)
                        employee_ids=temp_employee_ids
                    
                    if employee_ids:
                        new_degree_id= salary_degree_obj.search(cr,uid,[('sequence','=',new_sequence)],context=context)
                        if new_degree_id:
                            for new_degree in salary_degree_obj.browse(cr,uid,new_degree_id,context=context):
                                for employee in employee_obj.browse(cr,uid,employee_ids,context=context):
                                    # to get margin_time for Degree
                                    degree_margin_time=0
                                    if c.degree_from:
                                        for seq in range(c.degree_from.sequence,c.degree_to.sequence):
                                            sequence=salary_degree_obj.search(cr,uid,[('sequence','=',seq)],context=context)
                                            if sequence:
                                                for dt in salary_degree_obj.browse(cr,uid,sequence,context=context):
                                                    for bt in dt.bonus_ids:
                                                        degree_margin_time+=bt.margin_time
                                    else:
                                        dt = employee.degree_id
                                        for bt in dt.bonus_ids:
                                            degree_margin_time+=bt.margin_time
                                    if not employee.promotion_date:
                                        prev_degree_date = time.mktime(time.strptime(employee.employment_date,'%Y-%m-%d'))
                                    else:  
                                        prev_degree_date = time.mktime(time.strptime(employee.promotion_date,'%Y-%m-%d'))
                                    candidate_date = time.mktime(time.strptime(c.date,'%Y-%m-%d'))
                                    diff_day = (candidate_date-prev_degree_date)/(3600*24)
                                    days= degree_margin_time-diff_day
                                    if days <= c.margin :
                                        min_bonus =  min(new_degree.bonus_ids , key=lambda x : x.sequence)
                                        emp_degree_dict = {
                                             'employee_id': employee.id,
                                             'employee_salary_scale' : employee.payroll_id.id,
                                             'new_scale_id' : new_degree.payroll_id.id,
                                             'reference' : new_degree.id,
                                             'code':employee.emp_code,
                                             'date':c.date,
                                             'previous':employee.degree_id.name,
                                             'company_id':employee.company_id.id,
                                             'new_bonuse_id' : min_bonus.id ,
                                             'process_type' : 'promotion',

                                                         }
                                        record_id = movements_obj.create(cr, uid,emp_degree_dict)
                                        record_ids.append(record_id)
                                       
            tree_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_movements_degree_tree_view')]) 
            tree_resource_id = obj_model.read(cr, uid, tree_model_data_ids, fields=['res_id'])[0]['res_id']      
            form_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_movements_degree')]) 
            form_resource_id = obj_model.read(cr, uid, form_model_data_ids, fields=['res_id'])[0]['res_id']                                
            res= { 
			'name': 'HR Movements Degree',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.movements.degree',
			'views': [(tree_resource_id,'tree'),(form_resource_id,'form')],
			'type': 'ir.actions.act_window',
			'domain': [('id','in',record_ids)],
		}
	    return res
