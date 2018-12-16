# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import netsvc
from tools.translate import _
from osv import osv, fields, orm
import openerp.addons.decimal_precision as dp

#----------------------------------------
# Punishment
#----------------------------------------
class hr_punishment(osv.Model):

    _name = "hr.punishment"

    _description = "Punishments"

    _columns = {
        'name':fields.char("Punishment", required= False),
        'code': fields.char('Code'),
        'penalty' : fields.boolean('Penalty'),
        'allow_deduct' :fields.many2one('hr.allowance.deduction', 'Deduction', domain=[('name_type','=','deduct'),('penalty','=',True)]),
        'active' : fields.boolean('Active'),
    }

    _defaults = {
        'active' :1,
    }

    _sql_constraints = [
       ('name_uniqe', 'unique (name)', 'you can not create same Punishments Name !')
    ]


    def copy(self, cr, uid, ids, default={}, context=None):
        default.update({'name':False })
        return super(hr_punishment, self).copy(cr, uid, ids, default=default, context=context)


    def unlink(self, cr, uid, ids, context=None):
        for e in self.browse(cr, uid, ids):
            check_reference = self.pool.get("hr.employee.violation").search(cr, uid, [('punishment_id', '=', e.id)])
            if check_reference:
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete This Punishment  Record Which Is Referenced!'))
        return super(osv.osv, self).unlink(cr, uid, ids, context)

#----------------------------------------
# Violation
#----------------------------------------
class hr_violation(osv.Model):

    _name = "hr.violation"

    _description = "Violations"

    _columns = {
        'name':fields.char("Violation", required= False),
        'code': fields.char('Code'),
        'active' : fields.boolean('Active'),
        'violation_punish_ids': fields.one2many('hr.violation.punishment' , 'violation_id', "Violation"),
    }

    _defaults = {
        'active' :1,
    }

    _sql_constraints = [
       ('name_uniqe', 'unique (name)', 'you can not create same Violations Name !')
 
    ]

    def copy(self, cr, uid, ids, default={}, context=None):
        default.update({'name':False })
        return super(hr_violation, self).copy(cr, uid, ids, default=default, context=context)

    def unlink(self, cr, uid, ids, context=None):
        for e in self.browse(cr, uid, ids):
            check_reference = self.pool.get("hr.employee.violation").search(cr, uid, [('violation_id', '=', e.id)])
            if check_reference:
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete This Violation  Record Which Is Referenced!'))
        return super(osv.osv, self).unlink(cr, uid, ids, context)

#----------------------------------------
# violation and punishment 
#----------------------------------------
class hr_violation_punishment(osv.Model):

    _name = "hr.violation.punishment"

    _description = "punishments of Violations"

    _order = "sequence"

    _columns = {
        'violation_id':  fields.many2one('hr.violation' , "Violation" , required=True, ondelete='cascade'),
        'punishment_id':  fields.many2one('hr.punishment' , "Punishment", required=True, ondelete='restrict'),
        'sequence': fields.integer('Sequence', required=True),
    }

    _sql_constraints = [
 
       ('violation_punishment_uniqe', 'unique (punishment_id,violation_id)', 'you can not create same punishment in same violation Name !')
    ]

#----------------------------------------
# Employee violation and punishment 
#----------------------------------------
class hr_employee_violation(osv.Model):

    _name = "hr.employee.violation"

    _description = "Employee Violations and Punishments"

    _rec_name = "employee_id"

    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", domain="[('state','!=',('refuse','draft'))]", required=True, 
                                       readonly=True, states={'draft':[('readonly', False)]}),
        'violation_id': fields.many2one('hr.violation', "Violation", required=True, 
                                       readonly=True, states={'draft':[('readonly', False)]}),
        'violation_date' :fields.date("Violation Date" , required=True, 
                                       readonly=True, states={'draft':[('readonly', False)]}),
        'violation_descr' :fields.text("Violation Description"),
        'decision_date' :fields.date("Decision Date",
                                       readonly=True, states={'draft':[('readonly', False)]}),
        'decision_descr' :fields.text("Decision Description"),
        'punishment_id': fields.many2one('hr.punishment', "Punishment", 
                                       readonly=True, states={'draft':[('readonly', False)]} ),
		'punishment_date' :fields.date("Punishment Date", size=8),
        'penalty_amount': fields.float("Penalty Amount", digits_compute=dp.get_precision('penalty_amount')),
        'start_date' :fields.date("Penalty Start Date"),
        'end_date' :fields.date("Penalty End Date"),
        'factor' :fields.integer("Factor"),
        'penalty' : fields.boolean('Penalty'),
        'state': fields.selection([('draft', 'Draft'), ('complete', 'Complete'),('implement','Implement')], 'State', readonly=True),
    }

    _defaults = {
        'state': 'draft',
        'violation_id':False, #To call onchange_violation and apply punishment_id domain
    }

    def _positive_factor(self, cr, uid, ids, context=None):
        for fact in self.browse(cr, uid, ids, context=context):
          if fact.factor<0 or fact.penalty_amount<0:
               return False
        return True 

    def check_dates(self, cr, uid, ids, context=None):
         exp = self.read(cr, uid, ids[0], ['violation_date', 'decision_date'])
         if exp['violation_date'] and exp['decision_date']:
             if exp['violation_date'] > exp['decision_date']:
                 return False
         return True
    def check_dates2(self, cr, uid, ids, context=None):
         exp = self.read(cr, uid, ids[0], ['start_date', 'end_date'])
         if exp['start_date'] and exp['end_date']:
             if exp['start_date'] > exp['end_date']:
                 return False
         return True   
     
    _constraints = [
        (_positive_factor, 'The value  must be more than zero!', ['factor or penalty_amount']),
        (check_dates, 'Error! Exception violation-date must be lower then Exception decision-date.', ['violation_date', 'decision_date']),(check_dates2, 'Error! Exception Penality Start Date must be lower then Penality End Date.', ['start_date', 'end_date']),
    ]

    _sql_constraints = [
        ("factor_check", "CHECK (state <> 'implement' OR penalty <> True OR factor > 0)",  _("The factor should be greater than Zero!")),
        ("penalty_amount_check", "CHECK (state <> 'implement' OR penalty <> True OR penalty_amount > 0)",  _("The penalty amount should be greater than Zero!")),
    ]

    def onchange_punishment(self, cr, uid, ids, punishment_id, context=None):
        """
        Method that retrieves the pentalty of the selected punishment.

        @param punishment_id: ID of the punishment
        @return: Dictionary of value 
        """
        return {'value': {'penalty':self.pool.get('hr.punishment').browse(cr, uid, punishment_id, context=context).penalty}}

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
        #return {'value': {'punishment_id':False} , 'domain': {'punishment_id':[('id', 'in', punishs),('ref_process','=','procedural_suspend')]}}
        return {'value': {'punishment_id':False} , 'domain': {'punishment_id':[('id', 'in', punishs)]}}

    def onchange_factor(self, cr, uid, ids,start_date, factor, employee_id, punishment_id, context=None):
        """
        Method thats computes the penalty amount of the violations.

        @param factor: Number of days
        @param employee_id: ID of employee
        @param punishment_id: ID of punishment
        @return: Dictionary that contains the Value of penalty
        """
        amount = 0
        punishment = self.pool.get('hr.punishment').browse(cr, uid, punishment_id, context=context)
        if punishment.penalty:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            allow_dict=self.pool.get('payroll').allowances_deductions_calculation(cr,uid,start_date,emp,{'no_sp_rec':True}, [ punishment.allow_deduct.id], False,[])
            amount = round(allow_dict['total_deduct']/30*factor,2)
        return {'value': {'penalty_amount':amount}}

    def implement_penalty(self, cr, uid, ids, context=None):
        """
        Creates Record  in hr_allowance_deduction_exception object.

        @return: Boolean True
        """
        employee_exception_line_obj = self.pool.get('hr.allowance.deduction.exception')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.penalty:
                emp_line = {
                    'code':rec.employee_id.emp_code,
                    'employee_id':rec.employee_id.id,
                    'start_date':rec.start_date,
                    'end_date':rec.end_date,
                    'allow_deduct_id':rec.punishment_id.allow_deduct.id,
                    'amount':rec.penalty_amount,
                    'types':'deduct',
                    'action':'special',
                    'types':rec.punishment_id.allow_deduct.name_type,
                }
                employee_exception_line_obj.create(cr, uid, emp_line, context=context)
        return self.write(cr, uid, ids, {'state':'implement'}, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """
        Method that prevents the deletion of non draft punishment.

        @return: Super unlink mehtod or raise exception
        """
        if self.search(cr, uid, [('state','!=','draft'),('id','in',ids)], context=context):
            raise orm.except_orm(_('Warning!'),_('You cannot delete non draft violation process.'))
        return super(hr_employee_violation,self).unlink(cr, uid, ids, context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        """
        Method reset the workflow and change state to 'draft'.
        
        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.violation', id, cr)
            wf_service.trg_create(uid, 'hr.employee.violation', id, cr)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Warning!'),_('You cannot duplicate this record refill it if you want !'))
    
class hr_employee_delegation(osv.Model):

    _inherit = "hr.employee.delegation"
    """Inherets hr.employee.delegation and adds function to check if the employee has punishment befor delegating  him.
    """  

    def check_punishment(self, cr, uid, ids, context=None):
        """
        Method that checks if the employee has punishment or not.

        @return: Boolean True or False
        """
        message = ''
        emp_violation_obj=self.pool.get('hr.employee.violation')
        for r in self.browse(cr, uid, ids, context=context):
            punish=emp_violation_obj.search(cr, uid, [('end_date', '>=', r.start_date),('start_date', '<=', r.end_date),('employee_id', '=', r.employee_id.id),
                                                      ('penalty', '=',True),('state', '!=', 'draft')], context=context)
            if punish:
                    message = _('This employee has  punishment with penalty')
            if message:
                if not r.message:
                    cr.execute('update hr_employee_delegation set message=%s where id=%s', (message, r.id))
                return False
        return True

#----------------------------------------
#Add  exception employee termenate
#----------------------------------------

class hr_employment_termination(osv.Model):
    """Inherets hr.employment.termination and adds function to check if the employee has punishment befor terminating his service.
    """
    _inherit = "hr.employment.termination"

    def termination(self, cr, uid, ids, context=None):
        """
        Method checks if the employee has punishment or not.

        @return: super termination method
        """
        wf_service = netsvc.LocalService("workflow")
        for emp in self.browse(cr, uid, ids, context=context):
                emp_obj = self.pool.get('hr.employee.violation')
                emp_id= emp_obj.search(cr, uid, [('employee_id','=',emp.employee_id.id),('end_date','>=',emp.dismissal_date)], context=context)
                if emp_id:
                    raise osv.except_osv(_('Warrning'), _('This employee has penalty not finished yet!'))
        return super(hr_employment_termination, self).termination(cr, uid, ids, context=context)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
