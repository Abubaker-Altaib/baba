# -*- coding: utf-8 -*-
##############################################################################
#
#	NCTR, Nile Center for Technology Research
#	Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv
import time
import mx
from datetime import datetime

#----------------------------------------
#employees exempt tax
#----------------------------------------
class employees_exempt_tax(osv.osv_memory):
	_name = "employees.exempt.tax"
	_columns = {
		'company_ids': fields.many2many('res.company','tax_company_rel','emp_tax_id','company_id','Company'),
		'date': fields.date('Date', required=True),
   	}
	_defaults= {
	  'date':time.strftime('%Y-%m-%d'),
	} 

	def exempt_tax(self,cr,uid,ids,context={}):
		"""Retrieves employees who should be exempted from tax those who reached tax exemption age or completed the specified years of work.
		  @return: Dictionary 
		"""
		employee_obj = self.pool.get('hr.employee')
		tax_obj = self.pool.get('hr.tax')
		company_obj = self.pool.get('res.company')
		emp_exempt_tax_obj = self.pool.get('hr.employee.exempt.tax')
		obj_model = self.pool.get('ir.model.data')
		record_ids= []
		for emp_tax in self.browse(cr,uid,ids,context=context):
			tax_id= tax_obj.search(cr,uid,[],context=context)
			if tax_id:
				tax = tax_obj.browse(cr,uid,tax_id[0],context=context)
				date = mx.DateTime.Parser.DateTimeFromString(emp_tax.date)
				company_ids = (emp_tax.company_ids and [c.id for c in emp_tax.company_ids] )or \
						 company_obj.search(cr,uid,[],context=context)
				emp_ids = employee_obj.search(cr,uid,[('state','=','approved'),('tax_exempted','!=',True),('company_id','in',tuple(company_ids))],context=context)
				employee_msg =  False
				for employee in employee_obj.browse(cr,uid,emp_ids): 
					if not employee.birthday or not employee.first_employement_date:
						employee_msg = employee_msg and employee_msg + " \n" + employee.name or " \n" + employee.name
					if employee_msg: continue
					birth_date = mx.DateTime.Parser.DateTimeFromString(employee.birthday)
					diff_day = int(date.year)-int(birth_date.year)
					employment_date = mx.DateTime.Parser.DateTimeFromString(employee.first_employement_date)
					diff_day1= int(date.year)-int(employment_date.year)
					if diff_day >= tax.taxset_age or diff_day1 >= tax.no_years_service :
						check=emp_exempt_tax_obj.search(cr,uid,[('employee_id','=',employee.id)],context=context)
                                                if check:
                                                   raise osv.except_osv('ERROR', 'The Employees Within This Period already exempted')
						else:
							emp_tax_dict = {
								'company_id':employee.company_id.id,
								'employee_id': employee.id,
								'birth_date':employee.birthday,
								'employment_date':employee.first_employement_date or employee.employment_date,
								'date':emp_tax.date,
							}
							record_id= emp_exempt_tax_obj.create(cr, uid, emp_tax_dict,context=context)
							record_ids.append(record_id)
				if employee_msg:
                                    raise osv.except_osv('ERROR', 'Please check the birth date and employment date for the following employees: %s'%(employee_msg,))
					
		model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_hr_employee_exempt_tax_tree')]) 
		resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
		res= { 
			'name': 'Employee Exempt Tax',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.employee.exempt.tax',
			'views': [(resource_id,'tree')],
			'type': 'ir.actions.act_window',
			'domain': [('id','in',record_ids)],
		}
		return res
