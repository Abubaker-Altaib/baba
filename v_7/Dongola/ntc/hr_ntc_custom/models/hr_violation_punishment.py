# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from __future__ import division
import datetime
from dateutil.relativedelta import relativedelta
import mx
import time
from openerp import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import math

class hr_employee_violation(osv.Model):

    _inherit = "hr.employee.violation"
    _columns = {
        'punishment_id': fields.many2many('hr.punishment',"hr_employee_violation_hr_punishment_rel",
        	'violation_id','punishment_id',string="Punishment", readonly=True, states={'draft':[('readonly', False)]} ),
         }
   

    def onchange_punishment(self, cr, uid, ids, punishment_id, context=None):
        """
        Method that retrieves the penalty of the selected punishment.

        @param punishment_id: ID of the punishment
        @return: Dictionary of value 
        """
        penalty = False
        for x in punishment_id:
        	if x[2]:
        		for record in self.pool.get('hr.punishment').browse(cr, uid, x[2], context=context):
        			penalty = record.penalty
        			if penalty == True:
        				break        	
        return {'value': {'penalty':penalty}}

    def onchange_violation(self, cr, uid, ids, violation_id, context=None):
        """
        Retrieves available punishments for specific Violation.

        @param violation_id: ID of violation
        @return: Dictionary of values
        """
        punishs = []
        if violation_id:
            punish_pool = self.pool.get('hr.violation.punishment')
            punish_ids = punish_pool.search(cr, uid, [('violation_id','=',violation_id)], context=context)
            punishs =[p['punishment_id'][0] for p in punish_pool.read(cr, uid, punish_ids, ['punishment_id'],context=context)]
        return {'value': {'punishment_id':False} , 'domain': {'punishment_id':[('id', 'in', punishs)]}}

    def onchange_factor(self, cr, uid, ids,start_date, factor, employee_id, punishment_id, context=None):
        """
        Method thats computes the penalty amount of the violations.

        @param factor: Number of days
        @param employee_id: ID of employee
        @param punishment_id: ID of punishment
        @return: Dictionary that contains the Value of penalty
        """
        if not start_date:
            raise osv.except_osv(_('Warrning'), _('Please Enter the  Start Date!'))
        if not employee_id:
            raise osv.except_osv(_('Warrning'), _('Please Enter Employee!'))
        amount = 0
        for x in punishment_id:
        	if x[2]:
        		for punishment in self.pool.get('hr.punishment').browse(cr, uid, x[2], context=context):
        			if punishment.penalty:
	    				emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
	    				allow_dict=self.pool.get('payroll').allowances_deductions_calculation(cr,uid,start_date,emp,{'no_sp_rec':True}, [ punishment.allow_deduct.id], False,[])
	    				amount += round(allow_dict['total_deduct']/30*factor,2)
        return {'value': {'penalty_amount':amount}}

    def resume_button(self, cr, uid, ids, context=None):
        """
        Method that check resume_date greater than start_date and check the numbers of days more than maximum period 
        that pre-configured before and then resume the employee state to approved &change the state of violation to done state.
        
        @return: boolean True
        """
        emp_obj=self.pool.get('hr.employee')
        employee_exception_line_obj = self.pool.get('hr.allowance.deduction.exception')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.start_date and rec.resume_date:
                date1 = datetime.datetime.strptime(rec.start_date, '%Y-%m-%d')
                date2 = datetime.datetime.strptime(rec.resume_date, '%Y-%m-%d')
                timedelta = date2 - date1
                diff_day = timedelta.days + float(timedelta.seconds) / 86400
                diff_mon = (date2.month - date1.month)+1
                count = 0
                count2 = 0
                for r in rec.punishment_id:
                	count += 1 
                	count2 += diff_day > r.max_period and 1 or 0
                if (rec.resume_date > rec.start_date) and count2 == count :
                    for rec1 in rec.punishment_id:
	                    if (rec1.penalty and rec1.allow_deduct.id):
	                        emp_line = {
	                            'code':rec.employee_id.emp_code,
	                            'employee_id':rec.employee_id.id,
	                            'start_date':rec.start_date,
	                            'end_date':rec.resume_date,
	                            'allow_deduct_id':rec1.allow_deduct.id,
	                            'amount':(rec.penalty_amount)*diff_mon ,
	                            'types':'allow',
	                            'action':'special',
	                        }
	                        employee_exception_line_obj.create(cr, uid, emp_line, context=context)
                    self.write(cr, uid, ids, {'end_date': rec.resume_date,'state': 'done'}, context=context)
                    emp_obj.write(cr, uid, [rec.employee_id.id], {'state':'approved'})
                else:
                    raise osv.except_osv(_('Warning '), _("penalty days not completed"))
            else:
                raise osv.except_osv(_('Configuration Error'), _("You Have To Insert Procedural Suspend Dates First "))
        return True


    def implement_penalty(self, cr, uid, ids, context=None):
        """
        Create Record line in hr_allowance_deduction_exception object.
        
        @return: True
        """
        print "---------------------context", context
        degree_obj = self.pool.get('hr.salary.degree')
        bonuses_obj = self.pool.get('hr.salary.bonuses')
        process_obj = self.pool.get('hr.process.archive')
        employee_exception_line_obj = self.pool.get('hr.allowance.deduction.exception')
        termination_pool = self.pool.get('hr.employment.termination')
        dismissal_pool = self.pool.get('hr.dismissal')
        wf_service = netsvc.LocalService("workflow")
        ref_process=''

        for rec in self.browse(cr, uid, ids, context=context):
            for rec1 in rec.punishment_id:
	            if rec1.penalty:
			print "-----------------------penalty"
	                emp_line = {
	                    'code':rec.employee_id.emp_code, 
	                    'employee_id':rec.employee_id.id, 
	                    'start_date':rec.start_date, 
	                    'end_date':rec.end_date, 
	                    'allow_deduct_id':rec1.allow_deduct.id, 
	                    'amount':rec.penalty_amount, 
	                    'types':'deduct', 
	                    'action':'special', 
	                }
	                exception_id=employee_exception_line_obj.create(cr, uid, emp_line, context=context)
	                ref_process='hr.allowance.deduction.exception'+','+str(exception_id)
	            if rec1.ref_process == 'termination':
	                dissmissal = dismissal_pool.search(cr, uid, [('punishment_id', '=', rec1.id)], context=context)
	                if not dissmissal:
	                    raise osv.except_osv(_('Configuration Error'), _("There is no dismissal reason linked to this punishment, kindly check  dismissal reason configurations!"))
	                id = termination_pool.create(cr, uid, {'employee_id': rec.employee_id.id, 
	                                                            'dismissal_date' :rec.decision_date, 
	                                                            'dismissal_type' : dissmissal[0], 
	                                                            'comments': _('This employee has been dismiss according to accounting board decision for making %s violation') % (rec.violation_id.name)}, context=context)
	                ref_process = 'hr.employment.termination,%s'%(id,)
			if context:
	    	                context.pop("default_type")
	    	                context.pop("default_operation_type")
	                termination_pool.termination(cr, uid, [id], context=context)
	                termination_pool.calculation(cr, uid, [id],False, context=context)
	                termination_pool.transfer(cr, uid, [id], context=context)
	            if rec1.ref_process=='process':
			print "---------------------process"
	                vals= {
	                       'code':rec.employee_id.code, 
	                       'employee_id':rec.employee_id.id, 
	                       'date': rec.start_date , 
	                       'approve_date': time.strftime('%Y-%m-%d') , 
	                       'employee_salary_scale': rec.employee_id.payroll_id.id, 
	                       'comments':'Punishment', 
	                }
			degree_id=degree_obj.search(cr, uid, [('sequence', '=', rec.employee_id.degree_id.sequence+1)], context=context)

			bonus_id=bonuses_obj.search(cr, uid, [('degree_id', 'in', degree_id)], order='sequence', limit=1, context=context)
                    	if not degree_id or not bonus_id:
	                    raise orm.except_orm(_('Warning'), _('This Punishment Not possible: '
	                                                          'Unable to determine the degre and bonus'))
			vals.update({'reference':'hr.salary.degree'+','+str(degree_id[0]), 
				     'previous': rec.employee_id.degree_id.name, })
			process_id=process_obj.create(cr, uid, vals, context=context)
			vals.update({'reference':'hr.salary.bonuses'+','+str(bonus_id[0]), 
				      'previous': rec.employee_id.bonus_id.name, 
				      'associated_id':process_id})
			process_obj.create(cr, uid, vals, context=context)
			wf_service.trg_validate(uid, 'hr.process.archive', process_id , 'approve', cr)
			ref_process='hr.process.archive'+','+str(process_id)
	            if rec1.ref_process in ('suspend','procedural_suspend'):
			emp_obj = self.pool.get('hr.employee')
			wf_service.trg_validate(uid, 'hr.employee',rec.employee_id.id ,'approve', cr)
			emp_obj.write(cr, uid, [rec.employee_id.id], {'state':'suspend'})
        return self.write(cr, uid, ids, {'state':'implement', 'ref_process':ref_process}, context=context)
