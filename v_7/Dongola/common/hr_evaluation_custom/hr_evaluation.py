# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time

class hr_evaluation_planss(osv.Model):

    _inherit = "hr_evaluation.plan"
    
    def unlink(self, cr, uid, ids, context=None):
        """
        Method prevent record Deletion if it Referenced
        @return: super & raise exception
        """             
        for e in self.browse(cr, uid, ids):
            check_reference = self.pool.get("hr_evaluation.evaluation").search(cr, uid, [('plan_id', '=', e.id)])
            if check_reference:
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete This Appraisal Plan  Record Which Is Referenced!'))
        return super(osv.osv, self).unlink(cr, uid, ids, context)

    _sql_constraints = [
          ('name_unique', 'unique(name)', 'The Name of Appraisal Plan should be unique!'),
        ]

class hr_evaluation_plan_phase(osv.Model):
    """
    Inherits hr_evaluation.plan.phase to add field that defines the participation
    percentage of the current phase's results in the final evaluation result.
    """

    _inherit = "hr_evaluation.plan.phase"

    _columns = {
        'percentage': fields.float('Percentage(%)'),
    }
    

class survey_response_line(osv.Model):
    
    _name = 'survey.response.line'
    
    _inherit = 'survey.response.line'
    
    """
     Inherits survey.response.line to add feilds and functions to be used in the
     process of calculating the results .
    """
    def _get_line_ids(self, cr, uid, ids, context={}, args={}):
        """
         Method that returns ids of the answers (if changed happend to them) that
         associated to the survey.response.line record.

         @return: List of Ids
        """
        return self.pool.get('survey.response.line').search(cr, uid, [('response_answer_ids', 'in', ids)], context=context)

    def _calculate(self, cr, uid, ids, name, args, context=None):
        """
        Method that calculates the full mark of the measure (here represented 
        as question) and employee's degree in this measure.

        @return: List of Ids
        """
        if context is None:
            context = {}

        res = {}   
        for respon in self.browse(cr, uid, ids, context=context):
            if respon.question_id:
                result = 0.0
                full_mark = 0.0
                ques_weight = respon.question_id.weight
                for ans in respon.response_answer_ids:
                    full_mark += (float(ans.answer) )*ques_weight
#                     full_mark += (float(ans.value_choice )  )*ques_weight
                    result += (float(ans.value_choice))*ques_weight
                    res[respon.id] = { 'result': int(round(0.0)),'full_mark': int(round(0.0)) }
                    res[respon.id]['result'] = result
                    res[respon.id]['full_mark'] = full_mark 
        return res     
    
    _columns = {
        'result':fields.function(_calculate, type='float', digits=(18, 2), string='Result',readonly=True, 
                    store= {
                        'survey.response.line': (lambda self, cr, uid, ids, c={}: ids, ['response_answer_ids'], 20),
                        'survey.response.answer': (_get_line_ids,[], 10),
                        },multi='all'),
        'full_mark':fields.function(_calculate, type='float', digits=(18, 2), string='Full Mark',readonly=True, 
                    store= {
                        'survey.response.line': (lambda self, cr, uid, ids, c={}: ids, ['response_answer_ids'], 20),
                        'survey.response.answer': (_get_line_ids,[], 10),
                        },multi='all'),
    }

class apparaisal_grade(osv.Model):
           
    _name = "hr.apparaisal.grade"

    _description = "Evaluation Grade"

    _columns = {
		'name' : fields.char("Grade ", size=64 , required=True,translate=True ),
		'min' :fields.float("Minimum "  ,required=True),
		'max' : fields.float("Maximum ", required=True),
    }

    def check_min_grade(self, cr, uid, ids, context={}):
        """
        Method that checks if the minimum grade is greater than the maximum grade
        then it returns an empty list.
        
        @return: List of floats
        """
        res = []
        for grade in self.browse(cr, uid, ids, context=context):
            if grade.min<grade.max:
                res.append(grade.min)
        return res

    _constraints = [
        (check_min_grade, 'sorry the Minimum grade is  Greater than Maximum grade', ['min']),
    ]    
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        Method prevent record duplication
        @return: raise exception
        """          
        raise osv.except_osv(_('Warning!'),_(' "Grade" name must unique !! '))
    
    def unlink(self, cr, uid, ids, context=None):
        """
        Method prevent record Deletion if it Referenced
        @return: super & raise exception
        """                        
        for e in self.browse(cr, uid, ids):
            check_reference = self.pool.get("hr_evaluation.evaluation").search(cr, uid, [('rating', '=', e.id)])
            if check_reference:
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete This Appraisal Grate  Record Which Is Referenced!'))
        return super(osv.osv, self).unlink(cr, uid, ids, context)

#----------------------------------------------------------
# survey question (Inherit)
#----------------------------------------------------------
class survey_question(osv.osv):
    """
    Inherits survey.question to add weight to the measure (represented as question).
    """

    _inherit = "survey.question"

    _columns = {
        'weight': fields.float('Weight'),
    }
    
    
class survey_response(osv.Model):
    """
    Inherits survey.question to add functional field that computes the result
    of the evaluation (answers).
    """
    
    _inherit = 'survey.response'

    def _get_line_ids(self, cr, uid, ids, context={}, args={}):
        """
        Method search for ids in object and return them
        """         
        return self.pool.get('survey.response.line').search(cr, uid, [('response_answer_ids', 'in', ids)], context=context)

    def _get_ids(self, cr, uid, ids, context={}, args={}):
        """
        Method search for ids in object and return them
        """             
        return self.pool.get('survey.response').search(cr, uid, [('question_ids', 'in', ids)], context=context)

    def _compute_result(self, cr, uid, ids, name, args, context=None):
        """
        Method that computes the result of the final appraisal by accumulating all the measures result.
        
        @return: Dictionary that contains the calculated result
        """
        response_line_obj = self.pool.get('survey.response.line')
        sur_que = self.pool.get('survey.question')
        res = {}
        for ser in self.browse(cr,uid,ids,context):
            res[ser.id] = {}
            question_ids=[q.id for q in ser.survey_id.page_ids]
            search_que = sur_que.search(cr, uid, [ ('page_id','in',question_ids)], context=context)
            search_resp = response_line_obj.search(cr, uid, [ ('question_id','in',search_que)], context=context)
            for que in response_line_obj.browse(cr, uid, search_resp, context):
                amount=0.0
                mark=0.0
                total_amount=0.0
                amount+=que.result
                mark+=que.full_mark
                try:
                    total_amount=(amount/mark)*100
                except:
                    raise osv.except_osv(_('ERROR'), _('Full Mark is Zero'))
                res[ser.id]['result']=total_amount
        return res
        
    _columns = {
       'result': fields.function(_compute_result, method=True,type='float', digits=(18, 2), string='Result',readonly=True,multi='all'),
    }

   
#----------------------------------------------------------
# evaluation interview (Inherit)
#----------------------------------------------------------
class hr_evaluation_interview(osv.Model):
    """
    Inherits hr.evaluation.interview to add functions that handle evaluation .
    """

    _inherit = "hr.evaluation.interview"
    
    def _get_ids(self, cr, uid, ids, context=None):
        """
        Method that returns ids of the response (that associated to the 
        hr.evaluation.interview) if they have been changed.

        @return: List of Ids
        """
        return self.pool.get('hr.evaluation.interview').search(cr, uid, [('response', '=', ids)], context=context)
        
    _columns = {       
        'result': fields.related('response', 'result',  string='Result',group_operator="avg",
                                    store={'hr.evaluation.interview': (lambda self, cr, uid, ids, c={}: ids, ['response'], 10),
                                    		'survey.response': (_get_ids, ['question_ids'], 10)}),
        'phase_id' : fields.many2one('hr_evaluation.plan.phase', 'Phase', ondelete='cascade'),
        
      }

    def onchange_evaluation_id(self, cr, uid, ids, phase_id,evaluation_id,context=None):
        """
        Method that returns the phase_id and a domain of it  based on the selected
        evaluation_id .
        @param phase_id: Id of the phase
        @param evaluation_id: Id of the evaluation
        @return: Dictionary
        """
        domain={}
        phase_obj = self.pool.get('hr_evaluation.plan.phase')
        evaluation_obj = self.pool.get('hr_evaluation.evaluation')
        if evaluation_id:
            for v in evaluation_obj.browse(cr, uid, [evaluation_id], context=context):
                plan_id=v.plan_id.id
                domain={'phase_id':[('plan_id','=',plan_id)]}
                if phase_id:
                    for phase in phase_obj.browse(cr, uid, [phase_id], context=context):
                        if phase.plan_id.id<> plan_id:
                            phase_id=False
        return {'value': {'phase_id':phase_id},'domain':domain}

    def onchange_phase_id(self, cr, uid, ids, phase_id,context=None):
        """
		Method that returns the survey_id based on the selected phase_id .
        @param phase_id: Id of the phase
        @return: Dictionary
        """
        phase_obj = self.pool.get('hr_evaluation.plan.phase')
        survey_id=False
        if phase_id:
            for phase in phase_obj.browse(cr, uid, [phase_id], context=context):
                survey_id=phase.survey_id.id 
        return {'value': {'survey_id':survey_id}}

    def onchange_survey_id(self, cr, uid, ids, phase_id,survey_id,context=None):
        """
		Method that returns the survey_id if there a phase_id 
		then it returns it based on the selected phase_id.
        @param phase_id: Id of the phase
        @param survey_id: Id of the survey
        @return: Dictionary
        """
        survey_id=survey_id
        if phase_id:
            return self.onchange_phase_id(cr, uid, ids, phase_id,context=context)
        return {'value': {'survey_id':survey_id}}

#----------------------------------------------------------
# evaluation  (Inherit)
#----------------------------------------------------------    
class hr_evaluation(osv.osv):
    """
    Inherits hr_evaluation.evaluation to add fields and functions that handle employee's evaluation .
    """
    _inherit = "hr_evaluation.evaluation"
    
    def _get_result(self, cr, uid, ids, name, args, context=None):
        """
        Method that calculates the final result from all interviews based 
        on the percentage of each phase.
        @return: Dictionary
        """
        res = {}
        interview_obj = self.pool.get('hr.evaluation.interview')
        phase_obj = self.pool.get('hr_evaluation.plan.phase')
        for r in self.browse(cr, uid, ids, context=context):
            result=0.0
            ids2= [s.id for s in r.survey_request_ids]
            interview = interview_obj.read_group(cr, uid, [('id', 'in', ids2),
            ('state','=','done')], ['phase_id','result'], ['phase_id'])
            for m in interview:
                percentage=phase_obj.browse(cr, uid,[m['phase_id'][0]] )[0].percentage
                result += (m['result']*percentage)/100.0
            res[r.id] = result
        return res
        
    def _get_rating(self, cr, uid, ids, name, args, context=None):
        """
        Method that returns the grade of the employee's appraisal based on his final result.
        @return: Dictionary
        """
        res = {}
        grade_obj = self.pool.get('hr.apparaisal.grade')
        for r in self.browse(cr, uid, ids, context=context):
            grade_id=grade_obj.search(cr, uid, [('min', '<=', r.result),('max', '>=', r.result)],limit=1)
            res[r.id] = grade_id and grade_id[0] or False
        return res
        
    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", required=True,domain="[('state','=','approved')]"),
        'result': fields.function(_get_result, string='Result', type='float'),
        'rating': fields.function(_get_rating, type='many2one', relation='hr.apparaisal.grade', string='Appreciation', readonly=True, store=True, help="This is the appreciation on which the evaluation is summarized."),
      }
    

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Method prevent record duplication

        @return: raise exception
        """        
        raise osv.except_osv(_('Warning!'),_('"Date" must unique !!'))
          
    def unlink(self, cr, uid, ids, context=None):
        """
        Method prevent record Deletion if it is not in draft state

        @return: super & raise exception
        """           
        for e in self.browse(cr, uid, ids):
            if e.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete an Employee Apparaisals Record Which Is Not In Draft State !'))
        return super(osv.osv, self).unlink(cr, uid, ids, context)  

    def button_plan_in_progress(self, cr, uid, ids, context=None):
        """
        Method that over writes button_plan_in_progress (mainly it adds the phase_id to the 
        interview record) it goes through the phases of the evaluation and for each phase it
        gets the interviewers and for each one of them it creates an interview records and sets  
        the phase in the wait state if its not it also sends email notification to the interviewers 
        if the phase has that feature.

        @return: True
        """
        hr_eval_inter_obj = self.pool.get('hr.evaluation.interview')
        if context is None:
            context = {}
        for evaluation in self.browse(cr, uid, ids, context=context):
            wait = False
            for phase in evaluation.plan_id.phase_ids:
                children = []
                if phase.action == "bottom-up":
                    children = evaluation.employee_id.child_ids
                elif phase.action in ("top-down", "final"):
                    if evaluation.employee_id.parent_id:
                        children = [evaluation.employee_id.parent_id]
                elif phase.action == "self":
                    children = [evaluation.employee_id]
                for child in children:

                    int_id = hr_eval_inter_obj.create(cr, uid, {
                        'evaluation_id': evaluation.id,
                        'phase_id': phase.id,
                        'survey_id': phase.survey_id.id,
                        'date_deadline': (parser.parse(datetime.now().strftime('%Y-%m-%d')) + relativedelta(months =+ 1)).strftime('%Y-%m-%d'),
                        'user_id': child.user_id.id,
                        'user_to_review_id': evaluation.employee_id.id
                    }, context=context)
                    if phase.wait:
                        wait = True
                    if not wait:
                        hr_eval_inter_obj.survey_req_waiting_answer(cr, uid, [int_id], context=context)

                    if (not wait) and phase.mail_feature:
                        body = phase.mail_body % {'employee_name': child.name, 'user_signature': child.user_id.signature,
                            'eval_name': phase.survey_id.title, 'date': time.strftime('%Y-%m-%d'), 'time': time }
                        sub = phase.email_subject
                        if child.work_email:
                            vals = {'state': 'outgoing',
                                    'subject': sub,
                                    'body_html': '<pre>%s</pre>' % body,
                                    'email_to': child.work_email,
                                    'email_from': evaluation.employee_id.work_email}
                            self.pool.get('mail.mail').create(cr, uid, vals, context=context)

        self.write(cr, uid, ids, {'state':'wait'}, context=context)
        return True 
    
