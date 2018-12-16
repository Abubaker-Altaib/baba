# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#

############################################################################
import time
from openerp.osv import fields, osv, orm
from openerp import netsvc
from openerp.tools.translate import _
import datetime


class hr_config_settings_inherit(osv.osv_memory):

    _inherit = 'hr.config.settings'

    _columns = {
        'resumption_period' :fields.integer("days"),
    }


class hr_dismissal(osv.Model):

    _inherit = "hr.dismissal"

    _columns = {
        'punishment_id': fields.many2one('hr.punishment', "Punishment", domain=[('ref_process', '=', 'termination')]), 
    }

    _sql_constraints = [
        ('punishment_uniqe', 'unique (punishment_id)', 'You can not link the same punishment with more than one dismissal reason!')
    ]


class hr_employee_reemployment(osv.Model):

    _inherit = 'hr.employee.reemployment'

    def reemployment_check(self, cr, uid, ids, *args):
        """
        inherit reemployment_check() to add new condition if thier is a punishment 
        related to the end of service it check the period of this punishment
        @return: reason if punishment_date less than reemployment date    
        """
        termination_obj = self.pool.get('hr.employment.termination')
        emp_violation_obj = self.pool.get('hr.employee.violation')
        for rec in self.browse(cr, uid, ids):
            term_id = termination_obj.search(cr, uid, [('employee_id', '=', rec.employee_id.id), ('state', '!=', 'draft')], order='dismissal_date desc', limit=1)
            for r in termination_obj.browse(cr, uid, term_id):
                if not r.dismissal_type.reemployment:
                    msg = _("You can not re-employment the employee the reason for termination is'%s' ") % (r.dismissal_type.name,)
                    cr.execute('update hr_employee_reemployment set comments=%s where id in %s', (msg, tuple(ids),))
                    return False
                punish_id = []
                if r.dismissal_type.punishment_id:
                    punish_id = emp_violation_obj.search(cr, uid, [('employee_id', '=', rec.employee_id.id), ('punishment_id', '=', r.dismissal_type.punishment_id.id), ('state', '!=', 'draft')], order='end_date desc', limit=1)
                    if punish_id:
                        for v in emp_violation_obj.browse(cr, uid, punish_id):
                            if v.end_date < rec.reemployment_date:
                                msg = _("You cannot re-employment the employee the punishment '%s' period is not end") % (v.punishment_date,)
                                cr.execute('update hr_employee_reemployment set comments=%s where id in %s', (msg, tuple(ids),))
                                return False
                if not r.dismissal_type.punishment_id or (r.dismissal_type.punishment_id and not punish_id):
                    start = time.mktime(time.strptime(r.dismissal_date, '%Y-%m-%d'))
                    end = time.mktime(time.strptime(rec.reemployment_date, '%Y-%m-%d'))
                    days = ((end - start) / (3600 * 24)) + 1
                    months = days / 30
                    if months < r.dismissal_type.period:
                        msg = _("You cannot re-employment the employee only after '%s' months from the end of his service") % (r.dismissal_type.period,)
                        cr.execute('update hr_employee_reemployment set comments=%s where id in %s', (msg, tuple(ids),))
                        return False
        return True


class hr_employee(osv.Model):

    _inherit = "hr.employee"

    _columns = {
        'state':fields.selection([('draft', 'Draft'), ('experiment', 'In Experiment'), 
                             ('approved', 'In Service'), ('suspend', 'suspend'), 
                             ('refuse', 'Out of Service')] , "State", readonly=True), 
    }

    def suspend(self, cr, uid, ids, context=None):
        """
        Workflow function
        
        @return: Change record state to 'suspend'
        """
        return self.write(cr, uid, ids, {'state': 'suspend'}, context=context)

class hr_punishment(osv.Model):

    _inherit = "hr.punishment"

    _columns = {
        'max_period' :fields.integer("Number of Days"), 
        'allowance_id' :fields.many2one('hr.allowance.deduction', 'Allowance'), 
        'ref_process':fields.selection([('penalty', 'Penalty'), ('termination', 'Dismissal'), 
                                        ('process', 'Degree Reduction') ,('procedural_suspend', 'Procedural Suspend'),
                                        ('suspend', 'Suspend')], "Process"), 
    }

    _sql_constraints = [('max_period_nagtive',"CHECK (max_period>=0)",_("Number of Days must be greater than Zero!"))]

    def onchange_ref_process(self, cr, uid, ids, ref_process, context=None):
        return {'value': {'penalty': ref_process in ['penalty','suspend','procedural_suspend'] ,'allowance_id':False}}


class hr_employee_violation(osv.Model):

    _inherit = "hr.employee.violation"

    _columns = {
        'type' : fields.selection((('procedural.obj', 'Procedural Stop'), ('punishment.obj', 'Punishment')), 'Type'), 
        'operation_type' : fields.selection([('accounting_board', 'Accounting Board'),
                                             ('resumption', 'Resumption'),('remove', 'Remove'),] ,  'Operation Type'), 
        'state': fields.selection([ ('draft', 'Draft'), ('complete', 'Complete') ,('confirm', 'Waiting For General Manager'),
                                    ('approve', 'Waiting For Accounting Board'), ('confirm2', 'General Manager'),
                                    ('implement', 'Implement') ,('validate', 'waiting for administrative & financial manager'),
                                    ('done', 'Done') ,('cancel', 'Cancel'),('resumption','Resumption') ], 'State', readonly=True),
        'ref_process': fields.reference('Process', selection=[('hr.allowance.deduction.exception', 'Penalty'), ('hr.employment.termination', 'Dismissal'), 
                                                               ('hr.process.archive', 'Degree Reduction')], readonly=True, size=128), 
        'resumption_type' : fields.selection([('accounting_board','Accounting Board'),('punishment','Punishment'),], 'Type' ,  readonly = True),        
        'active' : fields.boolean('Active'),
        'resume_date' : fields.date('Resume Date'),
        'punishments_ids': fields.many2many('hr.punishment', 'hr_employee_violation_punishment', 
            'hr_employee_violation_id', 'punishment_id', 
            string="Punishment" ),

   }

    _defaults = {
        'type': 'punishment.obj',
        'active' :1,
    }

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
                if (rec.resume_date > rec.start_date) and (diff_day > rec.punishment_id.max_period) :
                    if (rec.punishment_id.penalty and rec.punishment_id.allow_deduct.id):
                        emp_line = {
                            'code':rec.employee_id.otherid,
                            'employee_id':rec.employee_id.id,
                            'start_date':rec.start_date,
                            'end_date':rec.resume_date,
                            'allow_deduct_id':rec.punishment_id.allow_deduct.id,
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

    def appeal_punishment(self, cr, uid, ids, context=None):
        """
        Method that check number of days less than resumption_period and if resumption_type == 'punishment' change the state
        to confirm2 else change the state to confirm , if  number of days more than resumption_period this method rise exception
        that pre-configured before and then resume the employee state to approved &change the state of violation to done state.
        @return: boolean True
        """        
        hr_setting= self.pool.get('hr.config.settings')
        config_ids=hr_setting.search(cr,uid,[])
        config_browse=hr_setting.browse(cr, uid, config_ids)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.start_date and rec.end_date:
                date1 = datetime.datetime.strptime(rec.start_date, '%Y-%m-%d')
                date2 = datetime.datetime.strptime(rec.end_date, '%Y-%m-%d')
                diff = date2 - date1
                if config_browse == []:
                    raise osv.except_osv(_('You Cannot make Resumption '), _("Resumption period is Zero"))
                else:                
                    if config_browse[0].resumption_period > diff.days:
                        if rec.resumption_type == 'punishment':
                            self.write(cr, uid, ids, {'state':'confirm2'}, context=context)
                        else:
                            self.write(cr, uid, ids, {'state':'confirm'}, context=context)
                    # if remind days > REsumeption days  then cancle the request
                    else:
                        self.write(cr, uid, ids, {'state':'cancel','decision_descr':'Sorry ! The Resumption period was finished according to Penalty Dates and number of days in conf ..'}, context=context)    
            else:
                raise osv.except_osv(_('Configuration Error'), _("You Have To Insert Penalty Dates First "))
        return True
    
    def remove_button(self, cr, uid, ids, context=None):
        """
        Workflow function
        @return: Change record state to 'validate' and operation_type to 'remove'
        """
        return self.write(cr, uid, ids, {'state':'validate', 'operation_type':'remove'}, context=context)

    def approve_confirm2(self, cr, uid, ids, context=None):
        """
        Workflow function
        @return: Change record state to 'confirm2'
        """
        return self.write(cr, uid, ids, {'state':'confirm2'}, context=context)
    
    def validate_approve_cond(self, cr, uid, ids, context=None):
        """
        Workflow function
        @return: Change record state to 'approve'
        """
        return self.write(cr, uid, ids, {'state':'approve'}, context=context)
    
    def approve_confirm_cond(self, cr, uid, ids, context=None):
        """
        Workflow function
        @return: Change record state to 'confirm'
        """
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)

    def confirm1_cancel(self, cr, uid, ids, context=None):
        """
        Workflow function
        @return: Change record state to 'cancel'
        """
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)
    
    def to_appeal(self, cr, uid, ids, context=None):
        """
        Workflow function
        @return: Change record state to 'resumption'
        """
        return self.write(cr, uid, ids, {'state':'resumption'}, context=context)

    def done(self, cr, uid, ids, context=None):
        """
        Workflow function that set employee state to 'approved'
        @return: Change record state to 'done' & make it inactive
        """
        emp_ids = [rec.employee_id.id for rec in self.browse(cr, uid, ids, context=context)]
        self.pool.get('hr.employee').write(cr, uid, emp_ids, {'state':'approved'}, context=context)
        return self.write(cr, uid, ids, {'state': 'done' , 'active':False}, context=context)

    def accounting_board(self, cr, uid, ids, context=None):
        """
        Workflow function that create record .
        
        @return: call done method
        """
        for rec in self.browse(cr, uid, ids, context=context):
            self.create(cr, uid, {'employee_id':rec.employee_id.id,
                                'violation_id': rec.violation_id.id,
                                'violation_date': rec.violation_date,
                                'violation_descr': rec.violation_descr,
                                'operation_type' :'accounting_board',
                                'type': 'punishment.obj'}, context=context)
        return self.done(cr, uid, ids, context=context)

    def implement_penalty(self, cr, uid, ids, context=None):
        """
        Create Record line in hr_allowance_deduction_exception object.
        
        @return: True
        """
        degree_obj = self.pool.get('hr.salary.degree')
        bonuses_obj = self.pool.get('hr.salary.bonuses')
        process_obj = self.pool.get('hr.process.archive')
        employee_exception_line_obj = self.pool.get('hr.allowance.deduction.exception')
        termination_pool = self.pool.get('hr.employment.termination')
        dismissal_pool = self.pool.get('hr.dismissal')
        wf_service = netsvc.LocalService("workflow")
        ref_process=''

        for rec in self.browse(cr, uid, ids, context=context):
            if rec.penalty:
                emp_line = {
                    'code':rec.employee_id.otherid, 
                    'employee_id':rec.employee_id.id, 
                    'start_date':rec.start_date, 
                    'end_date':rec.end_date, 
                    'allow_deduct_id':rec.punishment_id.allow_deduct.id, 
                    'amount':rec.penalty_amount, 
                    'types':'deduct', 
                    'action':'special', 
                }
                exception_id=employee_exception_line_obj.create(cr, uid, emp_line, context=context)
                ref_process='hr.allowance.deduction.exception'+','+str(exception_id)
            if rec.punishment_id.ref_process == 'termination':
                dissmissal = dismissal_pool.search(cr, uid, [('punishment_id', '=', rec.punishment_id.id)], context=context)
                if not dissmissal:
                    raise osv.except_osv(_('Configuration Error'), _("There is no dismissal reason linked to this punishment, kindly check  dismissal reason configurations!"))
                id = termination_pool.create(cr, uid, {'employee_id': rec.employee_id.id, 
                                                            'dismissal_date' :rec.decision_date, 
                                                            'dismissal_type' : dissmissal[0], 
                                                            'comments': _('This employee has been dismiss according to accounting board decision for making %s violation') % (rec.violation_id.name)}, context=context)
                ref_process = 'hr.employment.termination,%s'%(id,)
                context.pop("default_type")
                context.pop("default_operation_type")
                termination_pool.termination(cr, uid, [id], context=context)
                termination_pool.calculation(cr, uid, [id],False, context=context)
                termination_pool.transfer(cr, uid, [id], context=context)
            if rec.punishment_id.ref_process=='process':
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
                    raise orm.except_orm(_('Warning'), _('This Punishment Not possible'
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
            if rec.punishment_id.ref_process in ('suspend','procedural_suspend'):
                emp_obj = self.pool.get('hr.employee')
                wf_service.trg_validate(uid, 'hr.employee',rec.employee_id.id ,'approve', cr)
                emp_obj.write(cr, uid, [rec.employee_id.id], {'state':'suspend'})
        return self.write(cr, uid, ids, {'state':'implement', 'ref_process':ref_process}, context=context)
