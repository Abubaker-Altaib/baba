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
    _inherit = "hr.allow.deduct.exception"
    
    def onchange_factor(self, cr, uid, ids, amount,factor):
        x = 0.0
        if amount and factor:
            x = amount/factor
        return {'value':{'special_amount':x}}


    _columns = {
        'factor' :fields.integer("Factor"),
        'special_amount' :fields.float("specialization Amount"),
        }

    _defaults = {
        'factor':1,
        'special_amount' : 0.0,
    }     
        
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
                         'factor':rec.factor,
                         'special_amount': rec.special_amount,
		},context=context)
       return {}


    def onchange_action_type(self, cr, uid, ids, action, types):
        """
        Method that returns domain contains the criterias of allowances/deduction searching .
        @param action: String of process choice 
        @return: Dictionary 
        """
        domain = {'allow_deduct_id':[('allowance_type','!=','in_cycle'),('name_type','=',types)]}
        if action:
            if action=='special':
                domain['allow_deduct_id'].append(('special', '=', True))
            else:
                domain['allow_deduct_id'].append(('special', '=', False))
                #domain['allow_deduct_id'].append(('in_salary_sheet', '=', True))
                
        return {'value': {'allow_deduct_id':False} , 'domain': domain}

