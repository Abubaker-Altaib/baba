# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import mx
import time
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from openerp import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import math
from admin_affairs.model.email_serivce import send_mail

class hr_training_plan(osv.Model):

    _inherit = "hr.training.plan"

    def _net_amount(self, cr, uid, ids, field_name, arg, context=None):
	#train_object = self.pool.get('hr.employee.training')
	res ={}
	basic = self.browse(cr,uid,ids,context=context)[0]
	print'basic : ',basic
	print'basic.suggested_course_ids : ',basic.suggested_course_ids
	course_cost = 0
 	for course in basic.suggested_course_ids:
            course_cost+=course.cost
	    print'course : ',course.cost
	
	print 'basic.plan_cost ',basic.plan_cost
	plan_cost = basic.plan_cost
	net_amount = plan_cost-course_cost
	print 'net_amount is : ',net_amount
	res[basic.id] = net_amount
	return res



    _columns = {
        'code': fields.char("Plan Code ", size=64),
        'start_date': fields.date('Plan Implementation Start Date'),
        'end_date': fields.date('Plan Implementation End Date'),
        'plan_cost' :fields.float("Training Plan cost"),
        'fees_currency_id':fields.many2one('res.currency', 'Fees Currency'),
        'type_plan': fields.selection([('internal','Internal Training'),('external','External Training')], 'Training Type'),                
        'net_amo':fields.function(_net_amount, method=True ,type='float',string='Net Amount', store=True), 
        'type': fields.selection([('internal', 'Internal Courses'),('external', 'External Courses')],'Type',required=False), 
        'classification': fields.selection((('yearly', 'Yearly Plan'), ('q_yearly', 'Quarter Yearly Plan'), ('h_yearly', 'Hafe Yearly Plan'), ('external', 'External')), 'Plan Classification'),             

    }

    def _default_currency(self, cr, uid, context=None):
        if context is None:
            context = {}
        model_data = self.pool.get('ir.model.data')
        res = False
        try:
            res = model_data.get_object_reference(cr, uid, 'hr_ntc_custom', 'SDG')[1]
        except ValueError:
            res = False
        return res
    
    
    def onchange_currancy(self, cr, uid, ids, type_plan, context=None):
        model_data = self.pool.get('ir.model.data')
	
        res = False

        if type_plan == 'internal':
            res = model_data.get_object_reference(cr, uid, 'hr_ntc_custom', 'SDG')[1]
            
        if type_plan == 'external':
            res = model_data.get_object_reference(cr, uid, 'base', 'USD')[1]
            
        return {
                'value':{'fees_currency_id':res}
               }
    _defaults = {
        
        'fees_currency_id':_default_currency,
	'type_plan':'internal',
      }

class hr_training_category(osv.Model):

    _inherit = "hr.training.category"

    _description = "Training Category"

    _columns = {
        'guidelines' : fields.text("Trainig Guidelines"),

    }

class hr_training_training_courses(osv.Model):

    _inherit = "hr.employee.training"

    _columns = {
        'comments' : fields.text("Reject Reasons"),
        'course_type': fields.selection((('beginners', 'Beginners'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')), 
                'Courses Type', required=False),
    	'terms' : fields.text("Course Terms"),
    	'training_date' : fields.selection((('1', 'First Date'), ('2', 'Second Date'),('3', 'Third Date'), ('4', 'Last Date')), 'Training Date'),
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Requested from section manager'),
                                    ('confirmed', 'Confirmed from department maneger'),
                                    ('validated', 'Validated from general department'),
                                    ('approved', 'Approved Training'),
                                    ('approved2', 'Approved from General Manager'),
                                    ('approved_na', 'Approved'),
                                    ('execute', 'Transferred to "Approved Courses"'), ('done', 'Done'),
                                    ('rejected', 'Reject from general manager'),
                                    ('edit', 'Edit'),('cancel', 'rejection')], 'State', readonly=True),
    	'cost' :fields.float("Triaining cost"),
        'fees_currency_id':fields.many2one('res.currency', 'Fees Currency'), 
        'country_id':fields.many2one('res.country', 'Country'), 
        'eva_template_id':fields.many2one('training.eva', 'Evaluation Template'), 
        'comments': fields.text('Comments'),
    }

    def approve(self, cr, uid, ids, context=None):
        """
		Workflow function that changes the state to 'approved' and if the type is 
        'hr.approved.course' then it updates employee's record and set training to
        True to indicate that the employee is in training.

		@return: Boolean True 
        """
        obj_attachment = self.pool.get('ir.attachment')
        emp_obj = self.pool.get('hr.employee')
        emp_training_id = self.browse(cr, uid, ids, context=context)[0].id
        for emp_trainig in self.browse(cr, uid, ids, context=context):
            if emp_trainig.type == 'hr.approved.course':
                emp_ids = [l.employee_id.id for l in emp_trainig.line_ids]
                emp_obj.write(cr, uid, emp_ids, {'training':True}, context=context)
        attachment_ids = obj_attachment.search(cr, uid, [('res_model','in',('hr.employee.training.approved','hr.employee.training.suggested')),('res_id','=',emp_training_id)], context=context)
        

        
        '''if attachment_ids:
            self.write(cr, uid, ids, {'state':'approved'}, context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('Their Is No Attachments To Approved'))'''
        training_line_pool = self.pool.get('hr.employee.training.line')
        line_ids = training_line_pool.search(cr, uid, [('training_employee_id', 'in', ids)], context=context)
        emp_dict = [{'name':l.training_employee_id.course_id.name,
         'emp_id':l.employee_id.id, 
         'place':l.training_employee_id.training_place, 
         'from':l.training_employee_id.start_date, 
         'to':l.training_employee_id.end_date, 
         'trainer':l.training_employee_id.partner_id.name,
         'template': False,
         'user_id':l.employee_id.user_id.id,
         'course_id':ids[0]} 
        for l in training_line_pool.browse(cr, uid, line_ids, context=context)]
        hr_employee_obj = self.pool.get('hr.employee')
        for emp in emp_dict:
            send_mail(hr_employee_obj, cr, uid,emp['emp_id'],'','Course', 
            unicode(' لديك دورة تدريبية ', 'utf-8') +emp['name']+
            unicode(' \n في ', 'utf-8')+emp['trainer']+unicode(' \n من ', 'utf-8')+emp['from']+
            unicode(' إلى ', 'utf-8')+emp['to'],
            user=[emp['user_id']],context=context or {})
                            
        self.write(cr, uid, ids, {'state':'approved'}, context=context)
        return True

    def done(self, cr, uid, ids, context={}):
        """
        Workflow function that changes the state to 'done' and updates employee's record 
        by setting training to False to indicate that the employee has finished the training.

		@return: Boolean True 
        """
        training_line_pool = self.pool.get('hr.employee.training.line')
        line_ids = training_line_pool.search(cr, uid, [('training_employee_id', 'in', ids)], context=context)
        emp_ids = [l.employee_id.id for l in training_line_pool.browse(cr, uid, line_ids, context=context)]
        self.pool.get('hr.employee').write(cr, uid, emp_ids, {'training':False}, context=context)

        ####
        training_eva_obj = self.pool.get('training.eva')
        #training_eva_ids = training_eva_obj.search(cr, uid, [('template','=', True)], context=context)
        #close for something
        training_eva_id = self.read(cr, uid, ids[0], context=context)['eva_template_id'][0]

        emp_dict = [{'name':l.training_employee_id.course_id.name,
         'emp_id':l.employee_id.id, 
         'place':l.training_employee_id.training_place, 
         'from':l.training_employee_id.start_date, 
         'to':l.training_employee_id.end_date, 
         'trainer':l.training_employee_id.partner_id.name,
         'template': False,
         'user_id':l.employee_id.user_id.id,
         'course_id':ids[0]} 
        for l in training_line_pool.browse(cr, uid, line_ids, context=context)]

        for emp in emp_dict:
            new_id = training_eva_obj.copy(cr, uid, training_eva_id, emp, context=context)
            #for email perpuse
            context['action'] = 'hr_ntc_custom.training_eva_form_action_menud'
            
            send_mail(training_eva_obj, cr, uid,new_id,'',unicode(' طلب تقييم ', 'utf-8'), unicode(' طلب تقييم في', 'utf-8'),user=[emp['user_id']], context=context or {})
                           
        
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)
    
   

class hr_training_suggested_courses(osv.Model):

    _inherit = "hr.employee.training.suggested"

    '''def _net_amount(self, cr, uid, ids, field_name, arg, context=None):
	train_object = self.pool.get('hr.employee.training')
	basic = self.browse(cr,uid,ids,context=context)[0]
	course_cost = 0
	idss = train_object.search(cr,uid,[('type','=','hr.suggested.course'),('plan_id','=',basic.plan_id.id)])
	print "-------------------idss",idss
 	for course in self.browse(cr, uid, idss, context=context):
            course_cost+=course.cost
	print ">>>>>>>.....>>>>>>>>",course_cost, basic.plan_id
	plan_cost = basic.plan_id.plan_cost
	print "--------------------------", plan_cost
	net_amount = plan_cost-course_cost
	print "-------------------net_amount",net_amount
	return net_amount'''


    def _default_currency(self, cr, uid, context=None):
		if context is None:
		    context = {}
		model_data = self.pool.get('ir.model.data')
		res = False
		try:
		    res = model_data.get_object_reference(cr, uid, 'hr_ntc_custom', 'SDG')[1]
		except ValueError:
		    res = False
		return res
    _columns = {
	
        'training_date' : fields.selection((('1', 'First Date'), ('2', 'Second Date'),('3', 'Third Date'), ('4', 'Last Date')), 'Training Date'),
	    'course_type': fields.selection((('beginners', 'Beginners'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')), 
            'Courses Type', required=False),
        'comments' : fields.text("Reject Reasons"),
    	'terms' : fields.text("Course Terms"),
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Requested from section manager'),
                                    ('confirmed', 'Confirmed from department maneger'),
                                    ('validated', 'Validated from general department'),
                                    ('approved', 'Approved Training'),
                                    ('approved_gen', 'Approved from General Manager'),
                                    ('approved2', 'Approved'),
                                    ('execute', 'Transferred to "Approved Courses"'), ('done', 'Done'),
                                    ('rejected', 'Reject'),
                                    ('edit', 'Edit'),('cancel', 'rejection')], 'State', readonly=True),
    	'cost' :fields.float("Triaining cost"),
        'fees_currency_id':fields.many2one('res.currency', 'Fees Currency'),                
	#'net_amo':fields.function(_net_amount, string='Net Amount', store=True, readonly=True)               
    }
    _defaults = {
        
        'fees_currency_id':_default_currency,
      }


    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        '''self.write(cr, uid, ids, {'state':'draft'})
        return True'''
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.training', id, cr)
            wf_service.trg_create(uid, 'hr.employee.training', id, cr)
        return True

    def training_manager_aprove(self, cr, uid, ids, context=None):
	self.write(cr, uid, ids, {'state':'approved'})
        return True

    
    def onchange_course(self, cr, uid, ids, course_id ,context=None):
        """ 
        return value of course terma, according to course id.        
        @return: dictionary of values of fields to be updated 
        """
        course = self.pool.get('hr.training.course').browse(cr,uid ,course_id,)
	return {'value':{'terms':course.training_category_id.guidelines}}




class hr_employee_training_approved(osv.Model):

    _inherit = "hr.employee.training.approved"

    
    _columns = {
    
        'course_type': fields.selection((('beginners', 'Beginners'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')), 
            'Courses Type', required=False),
        'country_id':fields.many2one('res.country', 'Country'), 
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Requested from section manager'),
                                    ('confirmed', 'Confirmed from department maneger'),
                                    ('validated', 'Validated from general department'),
                                    ('approved2', 'Approved from General Manager'),
                                    ('approved', 'Approved from Training Managment'),
                                    ('execute', 'Transferred to "Approved Courses"'), ('done', 'Done'),
                                    ('rejected', 'Reject from general manager'),], 'State', readonly=True),
        'eva_template_id':fields.many2one('training.eva', 'Evaluation Template'), 
        'comments': fields.text('Comments'),
        

    }


class hr_training_course(osv.Model):

    _inherit = "hr.training.course"

    
    _columns = {
        'name': fields.char("Course Name", required=True),
        'departments_ids':fields.many2many('hr.department', string= 'Departments'), 
        'job_ids':fields.many2many('hr.job', 'course_job_rel', 'course_id', 'job_id', 'Job'),
        }

class approved_courses(osv.osv_memory):

    _inherit = "hr.approve.course"

    def onchange_plan_id(self, cr, uid, ids, plan_id, context=None):
        """
        Method that returns domain of the approved seggested courses that related to the chosen plan_id.

        @param plan_id: Id of plan
        @return: Dictionary of values 
        """
        training_pool = self.pool.get('hr.employee.training')
        suggested_training_ids = training_pool.search(cr, uid, [('plan_id','=',plan_id),('state','=','approved2'),
                                                                            ('type','=','hr.suggested.course')], context=context)
        domain = [c['course_id'][0] for c in training_pool.read(cr, uid, suggested_training_ids,['course_id'],context=context)]
        return {'domain': {'course_ids':[('id', 'in', domain)]}}

    def approve_course(self, cr, uid, ids, context=None):
        """
        Merges all training requests that suggested by different departments for same course  
        together and find employees that math the course requirements.
        """
        training_pool = self.pool.get('hr.employee.training')
        emp_training_pool = self.pool.get('hr.employee.training.line')
        wiz = self.browse(cr, uid, ids, context=context)[0]
        course_ids = wiz.course_ids and [c.id for c in wiz.course_ids] or self.onchange_plan_id(cr, uid, ids, wiz.plan_id.id, context=context)['domain']['course_ids'][0][2]
        if not course_ids:
            raise orm.except_orm(_('Sorry!'), _('There is no courses suggested by any department!'))
        for course in set(self.pool.get('hr.training.course').browse(cr, uid, course_ids, context=context)):
            department_ids = []
            department_list = []
            suggested_training_ids = training_pool.search(cr, uid, [('plan_id','=',wiz.plan_id.id),('state','=','approved'),('course_id','=',course.id),
                                           ('type','=','hr.suggested.course')], context=context)
            suggest_line_ids = emp_training_pool.search(cr, uid, [('training_employee_id', 'in', suggested_training_ids)], context=context)
            suggest_emp_ids = [l.employee_id.id for l in emp_training_pool.browse(cr, uid, suggest_line_ids, context=context)]
            for l in self.pool.get('hr.employee.training.department').read_group(cr, uid, [('employee_training_id','in',suggested_training_ids)], 
                                                                                 ['department_id','candidate_no'], ['department_id'], context=context):
                department_ids.append((0,0,{'candidate_no':l['candidate_no'], 'department_id':l['department_id'][0],'type':'hr.approved.course'}))
                department_list.append(l['department_id'][0])
            trained_emp_ids = emp_training_pool.search(cr, uid, [('course_id','=', course.id),('type','=','hr.approved.course'),
                                                                 ('training_employee_id.state','in',['approved','done'])], context=context)
            domain = [('state', '!=', 'refuse'),('department_id','in',department_list),
                      ('employment_date','<=',(datetime.now()-relativedelta(years=course.general_experience_year)).strftime('%Y-%m-%d')),
                      ('id','not in', [l.employee_id.id for l in emp_training_pool.browse(cr, uid, trained_emp_ids, context=context)])]
            if course.job_ids: 
                job_ids = self.pool.get('hr.job').search(cr, uid, [('parent_id', 'child_of', [j.id for j in course.job_ids])], context=context)
                domain.append(('job_id','in', job_ids))
            if course.employee_category_ids: 
                domain.append(('category_ids','in', [c.id for c in course.employee_category_ids]))
            if course.departments_ids: 
                domain.append(('department_id','in', [d.id for d in course.departments_ids]))
            if course.prev_course_ids:
                emp_training_ids = emp_training_pool.search(cr, uid, [('course_id','in',[c.id for c in course.prev_course_ids]),('type','=','hr.approved.course'),
                                                                      ('training_employee_id.state','in',['approved','done'])], context=context)
                domain.append(('id','in', [l.employee_id.id for l in emp_training_pool.browse(cr, uid, emp_training_ids, context=context)]))
            match_emp_ids =  self.pool.get('hr.employee').search(cr, uid, domain, context=context)
            vals = {'plan_id': wiz.plan_id.id,
                    'course_id': course.id,
                    'request_date': datetime.now(),
                    'type': 'hr.approved.course',
                    'course_type' :'beginners',
                    'department_ids':department_ids,
                    'line_ids': [(0,0,{'employee_id':e,'match':True,'suggest':True}) for e in set(suggest_emp_ids).intersection(set(match_emp_ids))] + 
                                [(0,0,{'employee_id':e,'match':True,'suggest':False}) for e in set(match_emp_ids) - set(suggest_emp_ids)] +
                                [(0,0,{'employee_id':e,'match':False,'suggest':True}) for e in set(suggest_emp_ids) - set(match_emp_ids)]
            }
            training_pool.write(cr, uid, suggested_training_ids,{'state':'execute'} , context=context)
            training_pool.create(cr, uid, vals, context=context)



