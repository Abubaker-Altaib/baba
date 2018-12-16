# -*- coding: utf-8 -*-
############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################
import time
import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations

#----------------------------------------
# Employee Training
#----------------------------------------
class hr_employee_training_department(osv.Model):

    _name = "hr.employee.training.department"

    _description = "Department's Training Request"

    _columns = {
        'candidate_no': fields.integer('Candidates Number'),
        'department_id': fields.many2one('hr.department', 'Department Name', required=True),
        'type': fields.related('employee_training_id', 'type', type='char', string='Type', store=True),
        'employee_training_id': fields.many2one('hr.employee.training'),
      }

    def _check_dept_percentage(self, cr, uid, ids, context=None):
        """
        Method that checks if department's candidates exceeds the specified percentage 
        in training plan or not.

        @return: Boolean True or False
        """ 
        for d in self.browse(cr, uid, ids, context=context):
            if d.employee_training_id.plan_id.percentage == 0:
                continue
            candidates = self.read_group(cr, uid, [('employee_training_id.plan_id', '=', d.employee_training_id.plan_id.id), ('department_id', '=', d.department_id.id)],
                                  ['type', 'candidate_no'], ['type'], context=context)
            for c in candidates:
                if not d.department_id.member_ids or c['candidate_no'] * 100 / len(d.department_id.member_ids) > d.employee_training_id.plan_id.percentage:
                    return False
        return True

    _constraints = [
        (_check_dept_percentage, _('The total number of department candidates shouldn\'t exceed the specified percentage in training plan!'), []),
    ]

    _sql_constraints = [
        ('candidate_no_check', "CHECK (candidate_no>0)", _("Candidates number must be greater than zero!")),
    ]
#----------------------------------------
# Employee Training
#----------------------------------------
class hr_employee_training(osv.Model):

    _name = "hr.employee.training"

    _description = "Employee Training"

    _columns = {
        'name': fields.char('Number', size=64, required=True),
        
        'code': fields.related('course_id', 'code', type='char', string='Course Code', store=False, readonly=True),

        'company_id' : fields.many2one('res.company', 'Company', readonly=True, required=True, 
                                       states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        'course_id': fields.many2one('hr.training.course', 'Course Name', required=True, readonly=True, ondelete='restrict',
                                     states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        'plan_id' : fields.many2one('hr.training.plan', 'Plan', required=True, readonly=True, ondelete='restrict',
                                    states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        'request_date': fields.date('Request Date', readonly=True),
        'start_date': fields.date('Start Date', readonly=True,
                                  states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        'end_date': fields.date('End Date', readonly=True,
                                states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        'training_place': fields.selection([('inside', 'Inside Sudan'), ('outside', 'Outside Sudan')], 'Place' , readonly=True, states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        #FIXME: Required is not working
        'department_ids': fields.one2many('hr.employee.training.department', 'employee_training_id', 'Departments', required=True,
                                          readonly=True, states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Requested from section manager'),
                                    ('confirmed', 'Confirmed from department maneger'),
                                    ('validated', 'Validated from general department'),
                                    ('approved', 'Approved from Training Department'),
                                    ('execute', 'Transferred to "Approved Courses"'), ('done', 'Done'),
                                    ('rejected', 'Reject from general manager'),
                                    ('edit', 'Edit')], 'State', readonly=True),
        'line_ids': fields.one2many('hr.employee.training.line', 'training_employee_id', 'Employees', readonly=True,
                                     states={'draft':[('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', 'Trainer', ondelete='restrict', domain=[('trainer','=',True)],
                                     states={'draft':[('readonly', False)]}),
        'enrich_id': fields.many2one('hr.training.enrich', 'Enrich', readonly=True, ondelete='restrict',
                                     states={'draft':[('readonly', False)]}),
        'trainer_cost': fields.float('Trainer Cost', digits_compute=dp.get_precision('Account'), readonly=True,
                                     states={'draft':[('readonly', False)]}),
        'location' :fields.char("Training Location", size=64, readonly=True,
                                     states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        'trainer_payment_no' :fields.many2one('account.voucher','Trainer Payment Number' , readonly=True),
        'enrich_payment_no' :fields.many2one('account.voucher','Enrich Payment Number' , readonly=True),
        'start_time': fields.float('Start Time', readonly=True, states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        'end_time': fields.float('End Time', readonly=True, states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
        'type' : fields.selection((('hr.suggested.course', 'Suggested Courses'), ('hr.approved.course', 'Approved Courses')), 'Type'),
        'currency_id': fields.many2one('res.currency', 'Trainer Currency', readonly=True,
                                     states={'draft':[('readonly', False)]}),
        'department_id': fields.many2one('hr.department', string='Department',readonly=True,
                                     states={'draft':[('readonly', False)]}),
        'course_type': fields.selection((('suggested', 'Suggested Course'), ('needs', 'Needs Course'), ('plan', 'Training Plan')), 'Courses Type'),

      }

    _defaults = {
        'name': '/',
        'state': 'draft',
        'request_date': time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
        'currency_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id,
    }

    _sql_constraints = [
        ('end_date_check', "CHECK (end_date >= start_date)", _("The start date must be before the end date!")),
        ('trainer_cost_positive', "CHECK (type='hr.suggested.course' or state='draft' or trainer_cost>0)", _("Trainer cost must be positive value!")),
    ]
    def custom_done(self, cr, uid, ids, context=None):
        new_ids = self.search(cr, uid, [])
        for rec in self.browse(cr, uid, new_ids):
            rec.write({'trainer_cost':1})
        for rec in self.browse(cr, uid, new_ids):
            if rec.state!='done':
                rec.new_approve()
                rec.new_done()
                
                
    
    def new_approve(self, cr, uid, ids, context=None):
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
                #emp_obj.write(cr, uid, emp_ids, {'training':True}, context=context)
        attachment_ids = obj_attachment.search(cr, uid, [('res_model','in',('hr.employee.training.approved','hr.employee.training.suggested')),('res_id','=',emp_training_id)], context=context)
        

        
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
        '''for emp in emp_dict:
            send_mail(hr_employee_obj, cr, uid,emp['emp_id'],'','Course', 
            unicode(' لديك دورة تدريبية ', 'utf-8') +emp['name']+
            unicode(' \n في ', 'utf-8')+emp['trainer']+unicode(' \n من ', 'utf-8')+emp['from']+
            unicode(' إلى ', 'utf-8')+emp['to'],
            user=[emp['user_id']],context=context or {})'''
                            
        self.write(cr, uid, ids, {'state':'approved'}, context=context)
        return True

    def new_done(self, cr, uid, ids, context={}):
        """
        Workflow function that changes the state to 'done' and updates employee's record 
        by setting training to False to indicate that the employee has finished the training.

		@return: Boolean True 
        """
        training_line_pool = self.pool.get('hr.employee.training.line')
        line_ids = training_line_pool.search(cr, uid, [('training_employee_id', 'in', ids)], context=context)
        emp_ids = [l.employee_id.id for l in training_line_pool.browse(cr, uid, line_ids, context=context)]
        #self.pool.get('hr.employee').write(cr, uid, emp_ids, {'training':False}, context=context)

        ####
        training_eva_obj = self.pool.get('training.eva')
        #training_eva_ids = training_eva_obj.search(cr, uid, [('template','=', True)], context=context)
        #close for something
        #training_eva_id = self.read(cr, uid, ids[0], context=context)['eva_template_id'][0]

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

        '''for emp in emp_dict:
            new_id = training_eva_obj.copy(cr, uid, training_eva_id, emp, context=context)
            #for email perpuse
            context['action'] = 'hr_ntc_custom.training_eva_form_action_menud'
            
            send_mail(training_eva_obj, cr, uid,new_id,'',unicode(' طلب تقييم ', 'utf-8'), unicode(' طلب تقييم في', 'utf-8'),user=[emp['user_id']], context=context or {})
        '''                    
        
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)
    def _check_days(self, cr, uid, ids, context=None):
        """
        Method that checks wether trainee's training days exceed training specified
        days or not.

        @return: Boolean True or False
        """ 
        line_pool = self.pool.get('hr.employee.training.line')
        for training in self.browse(cr, uid, ids, context=context):
            if training.state != 'draft':
                for line in training.line_ids:
                    if line.days > line_pool._get_days(cr, uid, context={'start_date':training.start_date, 'end_date':training.end_date}):
                        return False
        return True

    def _check_candidates(self, cr, uid, ids, context=None):
        """
        Method that checks wether candidates number from department exceed specified 
        candidaes number for that department or not.
 
        @return: Boolean True or False
        """ 
        training_line_pool = self.pool.get('hr.employee.training.line')
        for training in self.browse(cr, uid, ids, context=context):
            if training.state != 'draft':
                candidates = []
                for dept in training.department_ids:
                    dept_candidates = training_line_pool.search(cr, uid, [('training_employee_id', '=', training.id), ('supervisor', '=', False),
                                                        ('department_id', '=', dept.department_id.id)], context=context)
                    candidates += dept_candidates
                    if dept.candidate_no != len(dept_candidates):
                        return False
                if training_line_pool.search(cr, uid, [('training_employee_id', '=', training.id), ('supervisor', '=', False),
                                                        ('id', 'not in', candidates)], context=context):
                    return False
        return True

    def _required_department_ids(self, cr, uid, ids, context=None):
        if self.search(cr, uid, [('id', 'in', ids), ('department_ids', '=', False), ('state', '!=', 'draft')], context=context):
            return False
        return True
    
    def _check_holidays(self, cr, uid, ids, context=None):
        """
        Method that checks wither trainee in a holiday or not.
        @return: Boolean True or False
        """
        holidays_obj = self.pool.get('hr.holidays')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state in ['approved','done']:
                for line in rec.line_ids:
                    holidays_id = holidays_obj.search(cr, uid,
                       [('employee_id', '=', line.employee_id.id), ('date_from','<=',line.end_date),
                       ('date_to','>=',line.start_date),('type','=','remove'),('state','not in',('cancel','refuse'))],
                       context=context)
                    if holidays_id:
                        raise orm.except_orm(_('Warning!'), _('%s is in holiday during the corse period.')%(line.employee_id.name,))
        return True
    
    _constraints = [
        (_check_days, _('The attending number of days for each employee shouldn\'t be grater than the total course number of days!'), []),
        (_check_candidates, _('There is mismatching between the suggested department\'s candidates & the suggested employees!'), []),
        (_required_department_ids, _('Operation is not completed, Departments & their candidates number are missing!'), ['department_ids']),
        (_check_holidays, _('This employee in holiday'), []),
    ]

    def update_days(self, cr, uid, ids, context=None):
        """
        Method that updates training lines (employee's training days) with the training days .

        @return: Boolean True
        """ 
        line_pool = self.pool.get('hr.employee.training.line')
        for training in self.browse(cr, uid, ids, context=context):
            lines = line_pool.search(cr, uid, [('training_employee_id', '=', training.id)], context=context)
            days = line_pool._get_days(cr, uid, context={'start_date':training.start_date, 'end_date':training.end_date})
            line_pool.write(cr, uid, lines, {'days':days}, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
        Method that overwrites unlink method to pervent the deletion of record that is not in the draft state.

        @return: Super unlink method 
        """
        if self.search(cr, uid, [('state', '!=', 'draft'), ('id', 'in', ids)], context=context):
            raise orm.except_orm(_('Warning!'), _('You cannot delete not draft training.'))
        return super(hr_employee_training, self).unlink(cr, uid, ids, context=context)

    def create(self, cr, uid, vals, context=None):
        """
        Method that overwrites create method to set employee's training serial number based on record type.

        @param vals: Dictionary contains entered data
        @return: Super create method 
        """
        vals.update({'name':self.pool.get('ir.sequence').get(cr, uid, vals.get('type'))})
        return super(hr_employee_training, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Method that overwrites copy method duplicates the value of the given id and 
        updates the value of state, payment_no, name fields.

        @param default: Dictionary of data
        @return: Super copy method 
        """
        default.update({
            'state': 'draft',
            'name': '/',
            'trainer_payment_no': False,
            'enrich_payment_no': False,
            'department_ids': False,
            'line_ids': False,
        })
        return super(hr_employee_training, self).copy(cr, uid, ids, default, context)

    def set_to_draft(self, cr, uid, ids, context=None):
        """
    	Method that resets the workflow (delets the old and creates a new one) and
        changes the state to 'draft'.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.training', id, cr)
            wf_service.trg_create(uid, 'hr.employee.training', id, cr)
        return True

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
        
        if attachment_ids:
            self.write(cr, uid, ids, {'state':'approved'}, context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('Their Is No Attachments To Approved'))
        return True

    def done(self, cr, uid, ids, context=None):
        """
        Workflow function that changes the state to 'done' and updates employee's record 
        by setting training to False to indicate that the employee has finished the training.

		@return: Boolean True 
        """
        training_line_pool = self.pool.get('hr.employee.training.line')
        line_ids = training_line_pool.search(cr, uid, [('training_employee_id', 'in', ids)], context=context)
        emp_ids = [l.employee_id.id for l in training_line_pool.browse(cr, uid, line_ids, context=context)]
        self.pool.get('hr.employee').write(cr, uid, emp_ids, {'training':False}, context=context)
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def check_account(self, cr, uid, rec, context=None):
        """
        Method that checks wether the training accounting configuration 
        (training journal, acount and analytic acount) has been set or not.

		@param rec: Browsing record of 'hr.employee.training' 
		@return: Boolean True or False
        """
        if not rec.company_id.training_account_id or not rec.company_id.hr_analytic_account_id or \
            not rec.company_id.training_journal_id:
            return False
        return True

    def trainer_transfar(self, cr, uid, ids, context=None):
        """
        Method that transfers the training cost to voucher and returns the created 
        voucher or reference to trainer_payment_no and it raises exceptions if no 
        accounting configurations or no training cost.

        @return: Boolean True 
        """
        payroll_pool = self.pool.get('payroll')
        for rec in self.browse(cr, uid, ids, context=context):
            if not self.check_account(cr, uid, rec, context=context):
                raise osv.except_osv(_('Configuration Error!'), _("Some training account Configurations doesn't set in '%s' Company.") % (rec.company_id.name,))
            if not rec.trainer_cost:
                raise osv.except_osv(_('Error!'), _('Please enter the trainer cost.'))
            journal_id = rec.company_id.training_journal_id.id
            partner_id = rec.partner_id.id
            currency_id = rec.currency_id.id
            if rec.department_id:
                department_id= rec.department_id.id 
            else:
                employee_id=self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
                department_id= employee_id and self.pool.get('hr.employee').browse(cr, uid,employee_id)[0].department_id.id or False

            reference = 'HR/Training/' + rec.partner_id.name + ' - ' + str(rec.start_date)


            employees_dic = {}
            for l in rec.line_ids:
                employees_dic[l.employee_id] = rec.trainer_cost/len(rec.line_ids)
            lines = self.pool.get('hr.employee').get_emp_analytic(cr, uid, employees_dic,\
                                   { 'account_id':rec.company_id.training_account_id.id })

            voucher = payroll_pool.create_payment(cr, uid, ids, {'reference':reference, 'lines':lines,
                                                                 'narration':reference, 'department_id':department_id,
                                                                 'journal_id':journal_id, 'currency_id':currency_id,
                                                                 'partner_id':partner_id}, context=context)
            self.write(cr, uid, rec.id, {'trainer_payment_no':voucher }, context=context)
        return True

    def enrich_transfar(self, cr, uid, ids, context=None):
        """
        Method that transfers the training enrich amount to voucher and returns the 
        created voucher or reference to enrich_payment_no and it raises exceptions 
        if no accounting configurations.

        @return: Boolean True 
        """
        payroll_pool = self.pool.get('payroll')
        enrich_amount = 0.0
        for rec in self.browse(cr, uid, ids, context=context):
            if not self.check_account(cr, uid, rec, context=context):
                raise osv.except_osv(_('Configuration Error!'), _("Some training account Configurations doesn't set in '%s' Company.") % (rec.company_id.name,))
            enrich_amount = sum([line.final_amount for line in rec.line_ids])
            if enrich_amount > 0:
                journal_id = rec.company_id.training_journal_id.id
                currency_id = rec.enrich_id.currency and rec.enrich_id.currency.id or rec.company_id.id
                reference = 'HR/Enrich/' + rec.course_id.name + '  -  ' + str(rec.start_date)
                start = time.mktime(time.strptime(rec.start_date, '%Y-%m-%d'))
                end = time.mktime(time.strptime(rec.end_date, '%Y-%m-%d'))
                days = ((end - start) / (3600 * 24)) + 1
                narration = _('Place OF Training = ( ' + str(rec.location or '') + ' ) . \
                        \n Number OF employee = (' + str(len(rec.line_ids)) + ' ). \
                        \n Number OF Days = (' + str(days) + ' )')
                account_analytic_id= rec.department_id.analytic_account_id and rec.department_id.analytic_account_id.id or rec.company_id.training_analytic_account_id.id

                
                employees_dic = {}
                for l in rec.line_ids:
                    employees_dic[l.employee_id] = l.final_amount
                lines = self.pool.get('hr.employee').get_emp_analytic(cr, uid, employees_dic,\
                                      { 'account_id':rec.company_id.training_account_id.id,  })
                if rec.department_id:
                    department_id= rec.department_id.id 
                else:
                    employee_id=self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
                    department_id= employee_id and self.pool.get('hr.employee').browse(cr, uid,employee_id)[0].department_id.id or False
                voucher = payroll_pool.create_payment(cr, uid, ids, {'reference':reference, 'lines':lines,
                                                                     'department_id':department_id,
                                                                     'narration':narration, 'journal_id':journal_id,
                                                                     'currency_id':currency_id}, context=context)
                self.write(cr, uid, rec.id, {'enrich_payment_no':voucher}, context=context)
        return True
#----------------------------------------------------------
# "Empty" Classes that are used to vary from the original employee.training
#   in order to offer a different usability with different views, labels, available reports/wizards...
#----------------------------------------------------------
class hr_employee_training_suggested(osv.Model):

    _name = "hr.employee.training.suggested"
    _inherit = "hr.employee.training"
    _table = "hr_employee_training"
    _description = "Suggested Courses"

    _defaults = {
        'type': 'hr.suggested.course',
    }
    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        """
        Method that overwrites search method.

        @param args: List of tuples specifying the search domain
        @param offset: Number of results to skip in the returned values
        @param limit: Max number of records to return
        @param order: Columns to sort by
        @param count: Returns only the number of records matching the criteria 
        @return: Super search method 
        """
        return self.pool.get('hr.employee.training').search(cr, user, args, offset, limit, order, context, count)

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        """
        Method that overwrites read method.

        @param fields: List of field names to return
        @return: Super read method 
        """
        return self.pool.get('hr.employee.training').read(cr, uid, ids, fields=fields, context=context, load=load)

    def check_access_rights(self, cr, uid, operation, raise_exception=True):
        """
        Method that overwrites check_access_rights method to redirect the check of 
        acces rights on the hr.employee.training object.

        @param operation: Operation (read, write, create, delete)
        @return: Super check_access_rights method 
        """
        return self.pool.get('hr.employee.training').check_access_rights(cr, uid, operation, raise_exception=raise_exception)

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        """
        Method that overwrites check_access_rule method to to redirect the check 
        of acces rules on the hr.employee.training object.

        @param operation: Operation (read, write, create, delete)
        @return: Super check_access_rule method
        """
        return self.pool.get('hr.employee.training').check_access_rule(cr, uid, ids, operation, context=context)

    def _workflow_trigger(self, cr, uid, ids, trigger, context=None):
        """
        Method that overwrites _workflow_trigger in order to trigger the workflow of 
        hr.employee.training at the end of create, write and unlink operation instead
        of it's own workflow (which is not existing).

        @param trigger: Trigger of workflow
        @return: Super _workflow_trigger method
        """
        return self.pool.get('hr.employee.training')._workflow_trigger(cr, uid, ids, trigger, context=context)

    def _workflow_signal(self, cr, uid, ids, signal, context=None):
        """
        Method that overwrites _workflow_signal to fire the workflow signal on given 
        hr.employee.training workflow instance instead of it's own workflow 
        (which is not existing).

        @param signal: Signal of workflow
        @return: Super workflow_signa method
        """
        return self.pool.get('hr.employee.training')._workflow_signal(cr, uid, ids, signal, context=context)



class hr_employee_training_approved(osv.Model):

    _name = "hr.employee.training.approved"
    _inherit = "hr.employee.training"
    _table = "hr_employee_training"
    _description = "Approved Courses"

    _defaults = {
        'type': 'hr.approved.course',
    }

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        """
        Method that overwrites search to redirect the search method to the hr.employee.training object

        @param args: List of tuples specifying the search domain
        @param offset: Number of results to skip in the returned values
        @param limit: Max number of records to return
        @param order: Columns to sort by
        @param count: Returns only the number of records matching the criteria 
        @return: Super search method
        """
        return self.pool.get('hr.employee.training').search(cr, user, args, offset, limit, order, context, count)

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        """
        Method that overwrites read to redirect the read method to the hr.employee.training object 

        @param fields: List of field names to return 
        @return: Super read method
        """
        return self.pool.get('hr.employee.training').read(cr, uid, ids, fields=fields, context=context, load=load)

    def check_access_rights(self, cr, uid, operation, raise_exception=True):
        """
        Method that overwrites check_access_rights method to redirect the check of 
        acces rights to the hr.employee.training object.

        @param operation: Operation (read, write, create, delete)
        @return: Super check_access_rights method 
        """
        return self.pool.get('hr.employee.training').check_access_rights(cr, uid, operation, raise_exception=raise_exception)

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        """
        Method that overwrites check_access_rule method to to redirect the check of 
        acces rules to the hr.employee.training object.

        @param operation: Operation (read, write, create, delete)
        @return: Super check_access_rule method
        """
        return self.pool.get('hr.employee.training').check_access_rule(cr, uid, ids, operation, context=context)

    def _workflow_trigger(self, cr, uid, ids, trigger, context=None):
        """
        Method that overwrites _workflow_trigger in order to trigger the workflow of
        hr.employee.training at the end of create, write and unlink operation instead
        of it's own workflow (which is not existing).

        @param trigger: Trigger of workflow
        @return: Super _workflow_trigger method
        """
        return self.pool.get('hr.employee.training')._workflow_trigger(cr, uid, ids, trigger, context=context)

    def _workflow_signal(self, cr, uid, ids, signal, context=None):
        #override in order to fire the workflow signal on given hr.employee.training workflow instance
        #instead of it's own workflow (which is not existing)
        return self.pool.get('hr.employee.training')._workflow_signal(cr, uid, ids, signal, context=context)


#----------------------------------------
# Training Line
#----------------------------------------
class hr_employee_training_line(osv.Model):

    _name = "hr.employee.training.line"
    _rec_name = "training_employee_id"
    _description = "Employee Training Line"
    _order = "supervisor desc"

    def _get_line_ids(self, cr, uid, ids, context=None, args={}):
        """
	    Method that returns ids of the hr.employee.training.line (if changed 
        happend to them) that associated to hr.employee.traininge record.

        @return: List of Ids
        """
        return self.pool.get('hr.employee.training.line').search(cr, uid, [('training_employee_id', 'in', ids)], context=context)

    def _get_emp_line_ids(self, cr, uid, ids, context=None, args={}):
        """
	    Method that returns ids of the hr.employee (if changed happend to them
        specialy department) that associated to hr.employee.traininge record.
        @return: List of Ids
        """
        return self.pool.get('hr.employee.training.line').search(cr, uid, [('employee_id', 'in', ids)], context=context)

    def _compute(self, cr, uid, ids , final_amount, arg=None , context=None) :
        """
        Method that computes training enrich for employees attend specific course.

        @return: Dictionary of data
        """
        payroll_pool = self.pool.get('payroll')
        enrich_state_pool = self.pool.get('emp.states')
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount = line.days and (line.supervisor and line.supervision_amount or \
                        line.training_employee_id.enrich_id.enrich_type == '3' and line.training_employee_id.enrich_id.fixed_value) or 0
            final_amount = (line.supervisor or line.training_employee_id.enrich_id.enrich_type == '3') and amount or 0
            total_days = self._get_days(cr, uid, {'start_date': line.training_employee_id.start_date, 'end_date': line.training_employee_id.end_date})
            if not line.supervisor and line.training_employee_id.enrich_id.enrich_type == '1':
                enrich_state_ids = enrich_state_pool.search(cr, uid, [('company_id', '=', line.employee_id.company_id.id) , ('name', '=', line.training_employee_id.enrich_id.id)])
                emp_enrich_state = enrich_state_pool.browse(cr, uid, enrich_state_ids, context=context)
                amount = (emp_enrich_state and emp_enrich_state[0].amount or 0.0) * total_days
                final_amount = (emp_enrich_state and emp_enrich_state[0].amount or 0.0) * line.days
            if not line.supervisor and line.training_employee_id.enrich_id.enrich_type == '2':
                if line.training_employee_id.enrich_id.allowance_id:
                        allow_deduct_dict = payroll_pool.allowances_deductions_calculation(cr, uid, line.training_employee_id.start_date, line.employee_id, {}, [line.training_employee_id.enrich_id.allowance_id.id], False, [])
                        amount = allow_deduct_dict['total_allow'] * total_days
                        final_amount = allow_deduct_dict['total_allow'] * line.days
            res.update({line.id: {'amount': amount, 'final_amount': final_amount}})
        return res

    def _get_days(self, cr, uid, context={}):
        """
        Method that computes number of days betwee tow dates.

        @return: Integer represents the number of days
        """

        if context.get('start_date', '') and context.get('end_date', ''):
            start = time.mktime(time.strptime(context.get('start_date', ''), '%Y-%m-%d'))
            end = time.mktime(time.strptime(context.get('end_date', ''), '%Y-%m-%d'))
            return ((end - start) / (3600 * 24)) + 1
        return 0
    
    def _get_ages(self, cr, uid, ids , employee, arg=None , context=None) :
        """
        Method that computes age for employees attend specific course.

        @return: Dictionary of data
        """
        employee_pool = self.pool.get('hr.employee')
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            emp=employee_pool.search(cr, uid, [('id', '=', line.employee_id.id)], context=context)
            employee = employee_pool.browse(cr, uid, emp,context=context)
            birthday = time.mktime(time.strptime(employee[0]['birthday'], '%Y-%m-%d'))
            system_date = time.mktime(time.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d'))
            age = ((system_date - birthday) / (3600 * 24)) / 365
            res.update({line.id: {'age': int(age)}})
        return res


    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", domain=[('state', '!=', 'refuse')], required=True, ondelete='restrict'),
        'department_id': fields.related('employee_id', 'department_id', type='many2one', relation='hr.department', string='Department', readonly=True ,
                                    store={'hr.employee':(_get_emp_line_ids, ['department_id'], 10),
                                           'hr.employee.training.line': (lambda self, cr, uid, ids, c=None:ids, ['employee_id'], 10)}),
        'course_id': fields.related('training_employee_id', 'course_id', type='many2one', relation='hr.training.course', string='Course', readonly=True),
        'enrich_payment_no': fields.related('training_employee_id', 'enrich_payment_no', type='many2one', relation='account.voucher', string='Enrich Payment Number', readonly=True),
        'start_date': fields.related('training_employee_id', 'start_date', type='date', string='Start Date', readonly=True , store={
                    'hr.employee.training.approved':(_get_line_ids, ['start_date'], 10),
                    'hr.employee.training.suggested':(_get_line_ids, ['start_date'], 10),
                    'hr.employee.training.line': (lambda self, cr, uid, ids, c=None:ids, ['training_employee_id'], 10) }),
        'end_date': fields.related('training_employee_id', 'end_date', type='date', string='End Date', readonly=True , store={
                    'hr.employee.training.approved':(_get_line_ids, ['end_date'], 10),
                    'hr.employee.training.suggested':(_get_line_ids, ['end_date'], 10),
                    'hr.employee.training.line': (lambda self, cr, uid, ids, c=None:ids, ['training_employee_id'], 10) }),
        'match': fields.boolean('Match', readonly=True),
        'days': fields.integer('Days'),
        'amount': fields.function(_compute, method=True , multi='amount', string='Amount',
                        digits_compute=dp.get_precision('Account'), store={
                    'hr.employee.training.approved':(_get_line_ids, ['enrich_id'], 10),
                    'hr.employee.training.suggested':(_get_line_ids, ['enrich_id'], 10),
                    'hr.employee.training.line': (lambda self, cr, uid, ids, c=None:ids, ['days','final_amount'], 10)
                   }),
        'final_amount': fields.function(_compute, method=True , multi='amount', string='Final Amount',
                        digits_compute=dp.get_precision('Account'), store={
                    'hr.employee.training.approved':(_get_line_ids, ['enrich_id'], 10),
                    'hr.employee.training.suggested':(_get_line_ids, ['enrich_id'], 10),
                    'hr.employee.training.line': (lambda self, cr, uid, ids, c=None:ids, ['days','final_amount'], 10)
                   }),
        'supervision_amount': fields.float('Supervision Amount', digits_compute=dp.get_precision('Account')),
        'attendance' : fields.selection((('1', 'Attend'), ('2', 'Absence with Reason'), ('3', 'Absence without Reason')), 'Attendance'),
        'supervisor': fields.boolean('Supervisor'),
        'training_employee_id' :fields.many2one('hr.employee.training', 'Training Course', required=True, ondelete='cascade'),
        'training_place': fields.related('training_employee_id', 'training_place', type='char', string='Training Place', store=False, readonly=True),
        'suggest': fields.boolean('Suggest', readonly=True),
        'type': fields.related('training_employee_id', 'type', type='char', string='Type', store=True),
        'currency_id': fields.related('training_employee_id', 'currency_id', type='many2one', relation='res.currency', string='currency', readonly=True),
        'code': fields.related('training_employee_id', 'code', type='char', string='Code', store=False, readonly=True),
        'age': fields.function(_get_ages, method=True , multi='employee_id', string='age', digits_compute=dp.get_precision('Account')),
        'plan_id': fields.related('training_employee_id', 'plan_id', type='many2one', relation='hr.training.plan', string='Plan', store=True, readonly=True),
        'emp_code': fields.related('employee_id', 'emp_code', type='char', string='Emp_code', store=True, readonly=True),
       
    }

    _defaults = {
        'attendance': '1',
        'days' : _get_days,
        'employee_id': lambda *a: False,
    }

    def write(self, cr, uid, ids, vals, context={}):
        days = 'days' in vals and vals['days'] or self.read(cr, uid, ids , ["days"], context=context)[0]['days']
        vals.update({'supervision_amount' : days != 0 and vals.get('final_amount') or 0})
        return super(hr_employee_training_line, self).write(cr, uid, ids, vals, context=context)

    def onchange_employee(self, cr, uid, ids, emp_id, context={}):
        """
		Method that returns the  employee_type that allowed to take training.
        @param emp_id: Id of employee
        @return: Dictionary of values
        """
        emp_obj = self.pool.get('hr.employee')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        contractors = company_obj.training_contractors
        employee = company_obj.training_employee
        recruit = company_obj.training_recruit
        trainee = company_obj.training_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        domain = {'employee_id':[('state', '!=', 'refuse')] + employee_domain['employee_id']}
        return {'domain':domain}

    def _check_days(self, cr, uid, ids, context=None):
        """
		Method that checks wether trainee's training days exceed training specified days or not.
        @param emp_id: Id of employee
        @return: Boolean True or False
        """
        line = self.browse(cr, uid, ids[0], context=context)
        if line.days > self._get_days(cr, uid, context={'start_date':line.training_employee_id.start_date, 'end_date':line.training_employee_id.end_date}):
            return False
        return True



    def _check_courses(self, cr, uid, ids, context=None):
        """
		Method that checks whether trainee is already take this course.
        @return: Boolean True or False
        """
        for line in self.browse(cr, uid, ids, context=context):
            if self.search(cr, uid, [('course_id', '=', line.course_id.id),('employee_id', '=', line.employee_id.id),('id', '<>', line.id), 
                                     ('training_employee_id.state','in',['approved','done']), ('type','=','hr.approved.course')], context=context):
                raise orm.except_orm(_('Warning!'), _('%s has already taken %s course or has been nominated to this course.')%(line.employee_id.name,line.course_id.name))
        return True

    _constraints = [
        (_check_days, _('The attending number of days for each employee shouldn\'t be grater than the total course number of days'), []),

        (_check_courses, _('This employee is already take this course'), ['employee_id']),
    ]

class hr_employee(osv.Model):

    _inherit = "hr.employee"

    _columns = {
                'course_ids': fields.one2many('hr.employee.training.line', 'employee_id', "Courses", readonly=True, domain=[('type', '=', 'hr.approved.course'),('training_employee_id.state','=','done')]),
                'training': fields.boolean('IN Training', readonly=True),
    }

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Method that overwrites copy method duplicates the value of the given id and updates
        the value of training and training fields.

        @param default: Dictionary of data
        @return: Super copy method 
        """
        default.update({'course_ids': False, 'training':False})
        return super(hr_employee, self).copy(cr, uid, ids, default=default, context=context)

    def name_search(self, cr, uid, name, args=None , operator='ilike', context=None, limit=100):
        """
        Method that overwrites name_search method Search for department (only departments 
        that requested trainings) and their display name.

        @param name: Object name to search
        @param args: List of tuples specifying search criteria
        @param operator: Operator for search criterion
        @param limit: Max number of records to return
        @return: Super name_search method 
        """
        if not args:
            args = []
        if context is None:
            context = {}
        if context.get('model') == 'hr.employee.training.line':
            if context.get('department_ids', []):
                department_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.employee.training.department'),
                                              context.get('department_ids'), ["department_id"], context)
                dept_ids=[]
                for d in department_ids:
                    if d.get('id',False):
                        dept_ids.append(d['department_id'][0])
                    if not d.get('id',False):
                        dept_ids.append(d['department_id'])
                    args.append(('department_id', 'in',dept_ids))

            if context.get('line_ids',[]):
                emp_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.employee.training.line'),
                                              context.get('line_ids'), ["employee_id"], context)
                values=[]
                for d in emp_ids:
                    if d.get('id',False):
                        values.append(d['employee_id'][0])
                    if not d.get('id',False):
                        values.append(d['employee_id'])
                    args.append(('id', 'not in', values))
        return super(hr_employee, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)


class hr_department(osv.Model):

    _inherit = "hr.department"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        if context.get('model') == 'hr.employee.training.department':
            if context.get('department_ids', []):
                department_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.employee.training.department'),
                                                  context.get('department_ids'), ["department_id"], context)
                args.append(('id', 'not in', [isinstance(d['department_id'], tuple) and d['department_id'][0] or d['department_id'] for d in department_ids]))
        return super(hr_department, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

