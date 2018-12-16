# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv
import openerp.addons.decimal_precision as dp
#----------------------------------------
#allow_deduct_exception
#----------------------------------------
class allow_deduct_exception(osv.osv_memory):
    _name = "hr.allow.deduct.exception"
    _columns = {
        'action':fields.selection([('special','Specialization'),('exclusion','Exclusion')],'Process Type',required= True),
        'types':fields.selection([('allow', 'Allowance'), ('deduct', 'Deduction')], 'Type', required=True),
	    'company_id' : fields.many2one('res.company', 'Company',required=True),
	    'employee_ids': fields.many2many('hr.employee', 'exception_employee_rel','exception','employee_id','Employees',required=True ),
	    'allow_deduct_id': fields.many2one('hr.allowance.deduction', 'Allowance/Deduction',required=True ),
	    'start_date': fields.date("Start Date", required= True),
	    'end_date' : fields.date("End Date"),
	    'amount' :fields.float("Amount/Percentage", digits_compute=dp.get_precision('Payroll')),
    }
    _defaults = {
       
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.allow.deduct.exception', context=c), 
	
    }
    def check_dates(self, cr, uid, ids, context=None):
        exp = self.read(cr, uid, ids[0], ['start_date', 'end_date'])
        if exp['start_date'] and exp['end_date']:
            if exp['start_date'] > exp['end_date']:
                return False
        return True

    def duplicate_rec(self, cr, uid, ids, context=None): 
        process_obj = self.pool.get('hr.allowance.deduction.exception')
        employee_obj = self.pool.get('hr.employee')            
        for record in self.browse(cr, uid,ids):
            if record.employee_ids:
                employee_list = [employee.id for employee in record.employee_ids]
            else:
                employee_list = employee_obj.search(cr,uid,[])
            for employee in employee_list:
                check_salary = process_obj.search(cr,uid,[('employee_id','=',employee),('action','=',record.action),
                                                          ('types','=',record.types),('start_date','=',record.start_date)])
                if check_salary:
                    return False
        return True

    _constraints = [
        (check_dates, 'Error! Exception start-date must be lower then Exception end-date.', []),
        #(duplicate_rec, 'Error! Duplication of The Same Exception Record Not Allowed.', ['employee_id', 'action','types','start_date'])
    ]

    def onchange_action_type(self, cr, uid, ids, action, types):
        """
        Method that returns domain contains the criterias of allowances/deduction searching .
        @param action: String of process choice 
        @return: Dictionary 
        """
        domain = {'allow_deduct_id':[('allowance_type','!=','in_cycle'),('in_salary_sheet', '=', True),('name_type','=',types)]}
        if action:
            if action=='special':
                domain['allow_deduct_id'].append(('special', '=', True))
            else:
            	domain['allow_deduct_id'].append(('special', '=', False))
            	
        return {'value': {'allow_deduct_id':False} , 'domain': domain}

          
        
    def create_exception(self,cr,uid,ids,context={}):
       """
       Method that adds special allowance/deduction for a group of employees in same dapartment in specific period .
       @return: Dictionary 
       """
       exception_obj = self.pool.get('hr.allowance.deduction.exception')
       for rec in self.browse(cr,uid,ids,context=context):
          for emp in rec.employee_ids:
                exception_obj.create(cr, uid, {
			 'code' : emp.emp_code,
		         'employee_id':emp.id,
		         'allow_deduct_id' :rec.allow_deduct_id.id,
		         'start_date' : rec.start_date,
		         'end_date' : rec.end_date,
		         'amount':rec.amount,
                         'types':rec.allow_deduct_id.name_type,
                         'action':rec.action,
		},context=context)
       return {}

