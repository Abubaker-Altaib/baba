# -*- coding: utf-8 -*-
##############################################################################
#
#	NCTR, Nile Center for Technology Research
#	Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

#----------------------------------------
#salary scale allowances and deductions
#----------------------------------------
class salary_scale_allow_deduct(osv.osv_memory):

	_name= "salary.scale.allow.deduct"

	_description = 'Salary scale allowances and deductions'

	_columns = {
		'payroll_id': fields.many2one('hr.salary.scale', 'Salary Scale',required=True),	
		'degree_ids': fields.many2many('hr.salary.degree', 'allow_deduct_degree_rel','alow_deduct_id','degree_id','Degrees',
								   domain="[('payroll_id','=',payroll_id)]",required=True),
		'amount':fields.float("Amount/Percentage", digits_compute=dp.get_precision('Payroll')),
	}

	def positive_amount(self, cr, uid, ids, context=None):
         for m in self.browse(cr, uid, ids, context=context):
          if m.amount<0 :
               return False
         return True 

	_constraints = [
        (positive_amount, 'The Amount  must be more than zero!',[]),
	]

	def create_degrees(self,cr,uid,ids,context):
		"""
		Method that creates records for allowance/deduction that contain the amount of allowance/deduction for each degree.
		@return: dictionary
		"""
		allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
		form = self.browse(cr, uid, ids, context=context)[0]
		for allow_deduct in context['active_ids']: 
			for degree in form.degree_ids:
				allow_deduct_obj.create(cr, uid, {'payroll_id': form.payroll_id.id,
												  'degree_id': degree.id,
												  'allow_deduct_id' : allow_deduct,
												  'amount':form.amount,},context=context)
		return True
	
	def update_degrees(self,cr,uid,ids,context):
		"""
		Updates allowance/deduction amount of the given degree/s.
		@return: dictionary
		"""
		allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
		form = self.browse(cr, uid, ids, context=context)[0]
		res=allow_deduct_obj.search(cr,uid,[('degree_id','in',[x.id for x in form.degree_ids]),('allow_deduct_id','in',context['active_ids'])],context=context)
		allow_deduct_obj.write(cr, uid, res, {'amount':form.amount})
 
		return True
