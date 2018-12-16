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

    _columns = {
    'degree_from': fields.many2one('hr.salary.degree','Degree From'),
	'degree_to': fields.many2one('hr.salary.degree','Degree To'),
	'academic': fields.boolean('Academic'),
	'qual': fields.many2one('hr.qualification','qualification'),
	'isolated' : fields.boolean('Isolated'),
	'ruling' : fields.boolean('Ruling'),
	'rebuke':fields.selection([('strong','Strong'),('simple', 'simple')] ,'Rebuke'),  
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
                new_sequence =degrees.sequence+1
                new_degree_id= salary_degree_obj.search(cr,uid,[('sequence','=',new_sequence)],context=context)
                if new_degree_id:
                    value['degree_to']=new_degree_id[0]
        return {'value':value}



    def bonus_candidates(self,cr,uid,ids,context={}):
        """Method that retreives the candidated employees for the yearly bonuses 
           ( who complated one year in thier current bonus or more or those who have not complated one year but they fall in the margin).
        @return: Dictionary 
        """
        for c in self.browse( cr, uid,ids):
            pool = pooler.get_pool(cr.dbname)
            salary_degree_obj = pool.get('hr.salary.degree')
            salary_bonuses_obj = pool.get('hr.salary.bonuses')
            employee_obj = pool.get('hr.employee')
            degree_candidate_obj = pool.get('hr.process.archive')
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
                print">>>>>>>>>>>>>>>>>>>>>>>degree_id",degree_id
                for degrees in salary_degree_obj.browse(cr,uid,degree_id,context=context):
                    if c.degree_from:
                        new_sequence =c.degree_from.sequence+1
                    else:
                        new_sequence =degrees.sequence+1
                    # Test academic & qual & isolated & ruling
                    print">>>>>>>>>>>>>>>>>>>>>>>>>,",degrees,c.payroll_id.id
                    if not c.isolated:
                        temp_employee_ids = employee_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id),('degree_id','=',degrees.id),('is_isolated','=',False)],context=context)
                    else:
                        temp_employee_ids = employee_obj.search(cr,uid,[('payroll_id','=',c.payroll_id.id),('degree_id','=',degrees.id)],context=context)
                    if c.academic:
                        print">>>>>>>>>>>>>>>>>>>>>>academic"
                        for emp in employee_obj.browse(cr,uid,temp_employee_ids,context=context): 
                            for qual in emp.qualification_ids:
                                print">>>>>>>>>>>>>>>>>>>>>>>qual",qual.emp_qual_id.parent_id.id,c.qual
                                if qual.emp_qual_id.parent_id.id == c.qual.id:
                                    employee_ids.append(emp.id)
                        print">>>>>>>>>>>>>>>>>>>>>>academicemployee_ids",employee_ids
                    if c.isolated:
                        print">>>>>>>>>>>>>>>>>>>>>>isolated",temp_employee_ids
                        for emp in employee_obj.browse(cr,uid,temp_employee_ids,context=context): 
                            if emp.is_isolated:
                                if emp.promotion_date:
                                    df=datetime.strptime(emp.promotion_date,'%Y-%m-%d')
                                else: 
                                    df=datetime.strptime(emp.employment_date,'%Y-%m-%d')
                                    dt=datetime.strptime(c.date,'%Y-%m-%d')
                                    date=relativedelta(dt,df)
                                    years=date.years
                                    print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>year",years
                                if years >= 1:
                                    employee_ids.append(emp.id)
                        print">>>>>>>>>>>>>>>>>>>>>>isolatedemployee_ids",employee_ids
                    if c.ruling:
                        print">>>>>>>>>>>>>>>>>>>>>>ruling"
                        for emp in employee_obj.browse(cr,uid,temp_employee_ids,context=context): 
                            violation = violation_obj.search(cr,uid,[('employee_id','=',emp.id)],context=context)
                            if not violation:
                                employee_ids.append(emp.id)
                        print">>>>>>>>>>>>>>>>>>>>>>rulingemployee_ids",employee_ids
                    if not c.academic and not c.isolated and not c.ruling:
                        employee_ids=temp_employee_ids
                        print">>>>>>>>>>>>>>>>>>>>>>employee_ids",employee_ids
                    if employee_ids:
                        new_degree_id= salary_degree_obj.search(cr,uid,[('sequence','=',new_sequence)],context=context)
                        print">>>>>>>>>>>>>>>>>>>>>>>>>>new_degree_id,new_sequence",new_degree_id,new_sequence
                        if new_degree_id:
                            for new_degree in salary_degree_obj.browse(cr,uid,new_degree_id,context=context):
                                margin_day=0
                                for employee in employee_obj.browse(cr,uid,employee_ids,context=context):
                                    if not employee.promotion_date:
                                        prev_degree_date = time.mktime(time.strptime(employee.employment_date,'%Y-%m-%d'))
                                    else:  
                                        prev_degree_date = time.mktime(time.strptime(employee.promotion_date,'%Y-%m-%d'))
                                    candidate_date = time.mktime(time.strptime(c.date,'%Y-%m-%d'))
                                    print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>***",candidate_date,prev_degree_date
                                    diff_day = (candidate_date-prev_degree_date)/(3600*24)

                                    #days= degree.margin_time-diff_day
                                    '''check=False
                                    if c.margin:
                                        if days <= c.margin :
                                            check=True
                                    else:
                                        check=True'''
                                    print">>>>>>>>>>>>>>>>>>>>>>check",check
                                    check=True
                                    if check:
                                        emp_degree_dict = {
                                             'employee_id': employee.id,
                                             'employee_salary_scale' : employee.payroll_id.id,
                                             'reference' : new_degree.id,
                                             'code':employee.emp_code,
                                             'date':c.date,
                                             'previous':employee.degree_id.name,
                                             'company_id':employee.company_id.id,
                                                         }
                                        record_id = movements_obj.create(cr, uid,emp_degree_dict)
                                        print"_____________________________________________emp_degree_dict",emp_degree_dict,record_id
                                        record_ids.append(record_id)
                                       
            tree_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_movements_degree_tree_view')]) 
            tree_resource_id = obj_model.read(cr, uid, tree_model_data_ids, fields=['res_id'])[0]['res_id']      
            form_model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','hr_movements_degree')]) 
            form_resource_id = obj_model.read(cr, uid, form_model_data_ids, fields=['res_id'])[0]['res_id']                                
            res= { 
			'name': 'HR Promotion',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.movements.degree',
			'views': [(tree_resource_id,'tree'),(form_resource_id,'form')],
			'type': 'ir.actions.act_window',
			'domain': [('id','in',record_ids)],
		}
	    return res
