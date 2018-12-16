# -*- coding: utf-8 -*-
##############################################################################
#
#	NCTR, Nile Center for Technology Research
#	Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime
#----------------------------------------
#salary scale allowances and deductions
#----------------------------------------

class salary_scale_addition(osv.osv_memory):
	_name= "salary.scale.addition"
	_description = 'Salary scale addition'
	_columns = {
	
                'selection' :fields.selection([('amount', 'Amount'),('percentge', 'Percentage')], 'Amount/Percentage Selection',required=True),
		'amount':fields.float("Amount/Percentage", digits_compute=dp.get_precision('Payroll'),required=True),
		'degree_ids': fields.many2many('hr.salary.degree', 'scale_degree_rel','scale_id','degree_id','Degrees'),
                'date': fields.date('Date', required=True, select=True),
	          }



        _defaults = {
               'date': lambda *a: time.strftime('%Y-%m-%d'),
                 }


	
	def update_scale(self,cr,uid,ids,context):

	    """Updates the mount of salary scale given degree/s and bonus .
	       @return: dictionary
            """

            salary_scale_obj = self.pool.get('hr.salary.scale')
            bonus_lines_obj = self.pool.get('hr.salary.bonuses.lines')
	    for rec in self.browse(cr, uid, ids, context=context):
                payroll_id = context['active_id']
                degrees = rec.degree_ids or salary_scale_obj.browse(cr, uid, payroll_id,context).degree_ids
                for degree in degrees:
                    for bonus in degree.bonus_ids:
                        amount = rec.selection=='amount' and (bonus.basic_salary + rec.amount) or (bonus.basic_salary + (bonus.basic_salary*rec.amount/100) )
                        bonus_lines_obj.create(cr, uid, {'hr_salary_bonuses_id':bonus.id,'date':rec.date,'amount':amount,}, context)
            return True
