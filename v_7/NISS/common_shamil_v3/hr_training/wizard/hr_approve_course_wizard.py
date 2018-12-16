# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from osv import fields, osv, orm
from openerp import netsvc
import datetime

#----------------------------------------------------------
# Approve Suggested Courses
#----------------------------------------------------------
class approved_courses(osv.osv_memory):

    _name = "hr.approve.course"

    _columns = {
        'plan_id' : fields.many2one('hr.training.plan', 'Plan', required=True),
        'course_ids' : fields.many2many('hr.training.course', 'hr_approve_course_rel', 'wizard_id', 'couse_id', 'Courses'),
    }

    def onchange_plan_id(self, cr, uid, ids, plan_id, context=None):
        """
        Method that returns domain of the approved seggested courses that related to the chosen plan_id.

        @param plan_id: Id of plan
        @return: Dictionary of values 
        """
        training_pool = self.pool.get('hr.employee.training')
        suggested_training_ids = training_pool.search(cr, uid, [('plan_id','=',plan_id),('state','=','approved'),
                                                                            ('type','=','hr.suggested.course')], context=context)
        domain = [c['course_id'][0] for c in training_pool.read(cr, uid, suggested_training_ids,['course_id'],context=context)]
        return {'domain': {'course_ids':[('id', 'in', domain)]}}
    
    def approve_course(self, cr, uid, ids, context=None):
        """
        Merges all training requests that suggested by different departments for same course  
        together and find employees that math the course requirements.
        """
        wf_service = netsvc.LocalService("workflow")
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
                      ('employment_date','<=',(datetime.datetime.now()-relativedelta(years=course.general_experience_year)).strftime('%Y-%m-%d')),
                      ('id','not in', [l.employee_id.id for l in emp_training_pool.browse(cr, uid, trained_emp_ids, context=context)])]
            if course.job_ids: 
                job_ids = self.pool.get('hr.job').search(cr, uid, [('parent_id', 'child_of', [j.id for j in course.job_ids])], context=context)
                domain.append(('job_id','in', job_ids))
            if course.employee_category_ids: 
                domain.append(('category_ids','in', [c.id for c in course.employee_category_ids]))
            if course.qualification_ids: 
                domain.append(('qualification_ids.emp_qual_id','in', [q.id for q in course.qualification_ids]))
            if course.prev_course_ids:
                emp_training_ids = emp_training_pool.search(cr, uid, [('course_id','in',[c.id for c in course.prev_course_ids]),('type','=','hr.approved.course'),
                                                                      ('training_employee_id.state','in',['approved','done'])], context=context)
                domain.append(('id','in', [l.employee_id.id for l in emp_training_pool.browse(cr, uid, emp_training_ids, context=context)]))
            match_emp_ids =  self.pool.get('hr.employee').search(cr, uid, domain, context=context)
            vals = {'plan_id': wiz.plan_id.id,
                    'course_id': course.id,
                    'request_date': datetime.datetime.now(),
                    'type': 'hr.approved.course',
                    'department_ids':department_ids,
                    'line_ids': [(0,0,{'employee_id':e,'match':True,'suggest':True}) for e in set(suggest_emp_ids).intersection(set(match_emp_ids))] + 
                                [(0,0,{'employee_id':e,'match':True,'suggest':False}) for e in set(match_emp_ids) - set(suggest_emp_ids)] +
                                [(0,0,{'employee_id':e,'match':False,'suggest':True}) for e in set(suggest_emp_ids) - set(match_emp_ids)]
            }
            training_pool.create(cr, uid, vals, context=context)
            training_pool.write(cr, uid, suggested_training_ids,{'state':'execute'} , context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
