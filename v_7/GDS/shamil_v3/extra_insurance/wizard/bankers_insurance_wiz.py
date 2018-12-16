# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time
from datetime import timedelta,date , datetime
from openerp.tools.translate import _

#----------------------------------------
#Bankers Insurance wizard lines
#----------------------------------------

class bankers_insurance_lines_wizard(osv.osv_memory):

    _name = "bankers.insurance.lines.wizard"    
    _columns = {
    		'name': fields.text('Specification', size=256),
                'department_id':  fields.many2one('hr.department', 'Department', required=True), 
                'employee_id':  fields.many2one('hr.employee', 'Employee', required=True),
		'amount':fields.float('Amount', digits=(18,2),required=True), 
		'cash_saved_cost':fields.float('Cash Saved', digits=(18,2),required=True),
		'cash_carry_cost':fields.float('Cash Carry', digits=(18,2),required=True),
                'wizard_lines_id': fields.many2one('bankers.insurance.wizard', 'Bankers Insurance', ondelete='cascade'),

            }


#----------------------------------------
#Bankers Insurance wizard
#----------------------------------------

class bankers_insurance_wizard(osv.osv_memory):

    _name = "bankers.insurance.wizard"    
    _columns = {
        'company_id' : fields.many2one('res.company', 'Company',required=True), 
        'bankers_id':fields.many2one('bankers.insurance', 'Bankers Insurance'),
	'bankers_insurance_ids':fields.one2many('bankers.insurance.lines.wizard', 'wizard_lines_id' , 'Bankers Details',),
            }

    _defaults = {
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'bankers.insurance.wizard', context=c),
                }

    def update_car_operation(self,cr,uid,ids,context={}):
        """Method updates Bankers Insurance by adding Bankers Insurance lines.
           @return: Dictionary 
        """
        bankers_insurance_obj = self.pool.get('bankers.insurance')
        bankers_insurance_line_obj = self.pool.get('bankers.insurance.lines')
        
        for record in self.browse(cr,uid,ids,context=context):
		for line in record.bankers_insurance_ids :
			banker_id = bankers_insurance_line_obj.create(cr, uid, {
                 		'lines_id': record.bankers_id.id,
                 		'company_id': record.company_id.id,
                 		'department_id': line.department_id.id,
                		'employee_id':line.employee_id.id , 
                 		'amount': line.amount,
                 		'cash_saved_cost': line.cash_saved_cost,
                 		'cash_carry_cost': line.cash_carry_cost, 
                 		'name':line.name,

                                    }, context=context)


        return {}

bankers_insurance_wizard()

