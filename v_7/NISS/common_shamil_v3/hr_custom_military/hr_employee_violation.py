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
import openerp.addons.decimal_precision as dp
from lxml import etree

#----------------------------------------
# Punishment
#----------------------------------------
class hr_punishment(osv.Model):
    _inherit = "hr.punishment"
    _columns = {
        'company_id': fields.many2one('res.company','company'),
    }
    _defaults = {
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    }


#----------------------------------------
# Violation
#----------------------------------------
class hr_violation(osv.Model):

    _inherit = "hr.violation"
    _columns = {
        'company_id': fields.many2one('res.company','company'),
    }
    _defaults = {
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    }

#----------------------------------------
# violation and punishment 
#----------------------------------------
class hr_violation_punishment(osv.Model):

    _inherit = "hr.violation.punishment"
    _columns = {
        'company_id': fields.many2one('res.company','company'),
    }
    _defaults = {
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    }

class hr_employee_violation_search_employee(osv.Model):
    _name = "hr_employee_violation_search_employee.wizard"

    _columns = {
        'name_related': fields.char('Name'),
        'otherid': fields.char('otherid'),
        'degree_id': fields.many2one('hr.salary.degree', 'Degree'),
        'employee_id':fields.integer('Employee'),
        'search_id': fields.many2one('hr_employee_violation_search.wizard'),
        'type': fields.char('otherid'),
        'rec_id':fields.integer('rec_id'),
    }
    def select(self, cr, uid, ids, context=None):
        ids = ids[0]
        static = self.browse(cr, uid, ids, context=context)
        self.pool.get("hr.employee.violation").write(cr, uid, [static.rec_id], {static.type:static.employee_id})

        cr.execute( "delete from hr_employee_violation_search_employee_wizard where search_id="+str(static.rec_id)+";")
        cr.execute( "delete from hr_employee_violation_search_wizard where id="+str(static.rec_id)+";")

class hr_employee_violation_search(osv.Model):
    _name = "hr_employee_violation_search.wizard"

    _columns = {
        'name': fields.char('Name'),
        'employees_ids': fields.one2many('hr_employee_violation_search_employee.wizard',
        'search_id', string="Employees"),
    }

    def search(self, cr, uid, ids, context=None):
        ids = ids[0]
        
        cr.execute( "delete from hr_employee_violation_search_employee_wizard where search_id="+str(ids)+";")

        static = self.browse(cr, uid, ids, context=context)
        name = '%'+static.name+'%'

        cr.execute( """insert into hr_employee_violation_search_employee_wizard(rec_id,type,search_id,employee_id,name_related,otherid,degree_id)
        select '%s','%s','%s',emp.id as employee_id,name_related,otherid,degree_id from hr_employee emp 
        where emp.name_related ilike '%s' and emp.military_type='officer'
        """%(context['active_id'],context['active_type'],ids,name) )
        static = self.browse(cr, uid, ids, context=context)

        return {
            'name':_("Search"),
            'view_mode': 'form',
            'view_type': 'tree,form',
            'res_model': 'hr_employee_violation_search.wizard',
            'type': 'ir.actions.act_window',
            'domain': '[]',
            'res_id': ids,
            'target':"new",
            'context': context, 
        }   

class hr_employee_violation(osv.Model):

    _inherit = "hr.employee.violation"

    def _penalty_amount(self, cr, uid, ids, name, args, context=None):
        res = {}

        payroll_obj = self.pool.get('payroll')
        employee_obj = self.pool.get('hr.employee')

        for rec in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            for punishment in rec.punishments_ids:
                if punishment.penalty:
                    emp = rec.employee_id
                    allow_dict=payroll_obj.allowances_deductions_calculation(cr,uid,rec.start_date,emp,{'no_sp_rec':True}, [ punishment.allow_deduct.id], False,[])
                    amount += round(allow_dict['total_deduct']*rec.factor,2)
            res[rec.id] = amount
        return res
    
    def _installment_amount(self, cr, uid, ids, name, args, context=None):
        res = {}

        payroll_obj = self.pool.get('payroll')
        employee_obj = self.pool.get('hr.employee')

        for rec in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            period = rec.period and rec.period or 1.0
            for punishment in rec.punishments_ids:
                if punishment.penalty:
                    emp = rec.employee_id
                    allow_dict=payroll_obj.allowances_deductions_calculation(cr,uid,rec.start_date,emp,{'no_sp_rec':True}, [ punishment.allow_deduct.id], False,[])
                    amount += round(allow_dict['total_deduct']*rec.factor,2)
            res[rec.id] = amount/period
        return res

    _columns = {
        'punishments_ids': fields.many2many('hr.punishment', 'hr_employee_violation_punishment',
                                            'hr_employee_violation_id', 'punishment_id',
                                            string="Punishment"),
        
        'penalty_amount': fields.function(_penalty_amount, string="Penalty Amount", type="float", store=True),
        'company_id': fields.many2one('res.company','company'),

        'employee_exception_ids': fields.many2many('hr.allowance.deduction.exception', 'hr_employee_violation_exception',
                                            'hr_employee_violation_id', 'exception_id',
                                            string="Allowance Deduction Exceptions"),
                
        'loan_id': fields.many2one('hr.employee.loan', "Loan", invisible=True),

        'punishment_position': fields.many2one('hr.employee', 'Punishment Position'),
        'punishment_delegation': fields.many2one('hr.employee', 'Punishment Delegation'),


        'violations_ids': fields.many2many('hr.violation', 'hr_employee_violation_violation',
                                            'hr_employee_violation_id', 'violation_id',
                                            string="Violations"),
        'violation_id': fields.many2one('hr.violation', "Violation", required=False, 
                                       readonly=True, states={'draft':[('readonly', False)]}),
        
        'installment' : fields.function(_installment_amount, string="Installment", type="float", digits_compute=dp.get_precision('Installment')),


        'period' : fields.integer('period'),

    }

    _defaults = {
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_employee_violation, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//label[@for='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res

    #deprecated
    def onchange_punishment(self, cr, uid, ids, punishment_id, context=None):
        """
        Method that retrieves the pentalty of the selected punishment.

        @param punishment_id: ID of the punishment
        @return: Dictionary of value 
        """
        return {'value': {}}

    def onchange_punishment_delegation_otherid(self, cr, uid, ids, punishment_delegation_otherid, context=None):
        """
        @return: Dictionary of value 
        """
        if punishment_delegation_otherid:
            emp_obj = self.pool.get('hr.employee')
            emp_ids = emp_obj.search(cr, 1, [('otherid','=',punishment_delegation_otherid),('employee_type','=','employee'),('military_type','=','officer')])
            emp_ids = emp_obj.browse(cr, 1, emp_ids)
            if emp_ids:
                return {'value': 
                                {
                                    'punishment_delegation':emp_ids[0].name_related
                                }}
        return {'value': {'punishment_delegation':False}}
    
    def onchange_punishment_position_otherid(self, cr, uid, ids, punishment_position_otherid, context=None):
        """
        @return: Dictionary of value 
        """
        if punishment_position_otherid:
            emp_obj = self.pool.get('hr.employee')
            emp_ids = emp_obj.search(cr, 1, [('otherid','=',punishment_position_otherid),('employee_type','=','employee'),('military_type','=','officer')])
            emp_ids = emp_obj.browse(cr, 1, emp_ids)
            if emp_ids:
                return {'value': 
                                {
                                    'punishment_position':emp_ids[0].name_related
                                }}
        return {'value': {'punishment_position': False}}
        
    def create(self , cr , uid , vals , context=None):
        if 'punishment_delegation_otherid' in vals:
            temp = self.onchange_punishment_delegation_otherid(cr, uid, [], vals['punishment_delegation_otherid'])
            temp = temp['value']['punishment_delegation']
            vals['punishment_delegation'] = temp and temp or ''
        if 'punishment_position_otherid' in vals:
            temp = self.onchange_punishment_position_otherid(cr, uid, [], vals['punishment_position_otherid'])
            temp = temp['value']['punishment_position']
            vals['punishment_position'] = temp and temp or ''
        return super(hr_employee_violation , self).create(cr , uid , vals , context)

    def write(self , cr , uid , ids, vals , context=None):
        """
        """
        for rec in self.browse(cr, uid, ids, context):
            if 'punishment_delegation_otherid' in vals:
                temp = self.onchange_punishment_delegation_otherid(cr, uid, [], vals['punishment_delegation_otherid'])
                temp = temp['value']['punishment_delegation']
                vals['punishment_delegation'] = temp and temp or ''
            if 'punishment_position_otherid' in vals:
                temp = self.onchange_punishment_position_otherid(cr, uid, [], vals['punishment_position_otherid'])
                temp = temp['value']['punishment_position']
                vals['punishment_position'] = temp and temp or ''

        return super(hr_employee_violation,self).write(cr , uid , ids, vals , context)

    def onchange_punishments(self, cr, uid, ids, punishment_ids, context=None):
        """
        Method that retrieves the pentalty of the selected punishment.

        @param punishment_id: ID of the punishment
        @return: Dictionary of value 
        """
        penalty = False
        if punishment_ids:
            punishment_ids = punishment_ids[0]
            if punishment_ids:
                punishment_ids = punishment_ids[2]
                penalties = self.pool.get('hr.punishment').read(cr, uid, punishment_ids, ['penalty'])
                penalties = [x['penalty'] for x in penalties]
                if True in penalties:
                    penalty = True
        return {'value': {'penalty':penalty}}

    def onchange_violation(self, cr, uid, ids, violation_id, context=None):
        """
        Retrieves available punishments for specific Violation.

        @param violation_id: ID of violation
        @return: Dictionary of values
        deprecated
        """
        
        return {'value': {}}

    def onchange_factor(self, cr, uid, ids,start_date, factor,period, employee_id, punishments_ids, context=None):
        """
        Method thats computes the penalty amount of the violations.

        @param factor: Number of days
        @param employee_id: ID of employee
        @param punishment_id: ID of punishment
        @return: Dictionary that contains the Value of penalty
        """
        amount = 0.0
        period = period and period or 1.0
        #if no punishments exit the method
        if punishments_ids:
            punishments_ids = punishments_ids[0]
            if punishments_ids:
                punishments_ids = punishments_ids[2]
            else:
                return
        else:
            return
        payroll_obj = self.pool.get('payroll')
        employee_obj = self.pool.get('hr.employee')
        for punishment in self.pool.get('hr.punishment').browse(cr, uid, punishments_ids, context=context):
            
            if punishment.penalty:
                emp = employee_obj.browse(cr, uid, employee_id, context=context)
                allow_dict=payroll_obj.allowances_deductions_calculation(cr,uid,start_date,emp,{'no_sp_rec':True}, [ punishment.allow_deduct.id], False,[])
                amount += round(allow_dict['total_deduct']*factor,2)
        return {'value': {'penalty_amount':amount, 'installment' : amount/period}}

    
    def implement_penalty(self, cr, uid, ids, context=None):
        """
        Creates Record  in hr_allowance_deduction_exception object.

        @return: Boolean True
        """
        
        employee_exception_line_obj = self.pool.get('hr.allowance.deduction.exception')
        payroll_obj = self.pool.get('payroll')
        loan_obj = self.pool.get('hr.employee.loan')
        create_lines = {}
        for rec in self.browse(cr, uid, ids, context=context):
            all_amount = 0.0

            if rec.penalty:
                all_amount = rec.penalty_amount
                
                current_salary = payroll_obj.current_salary_status(cr, uid,ids, rec.employee_id, rec.start_date)
                balance = current_salary.get('balance',0.0)
                
                if balance<all_amount:
					raise osv.except_osv(_('Error!'),_('this employe is not enough balance'))

                loan_id = loan_obj.create(cr, uid, {'employee_id':rec.employee_id.id,\
                                                'refund_from':'salary',\
                                'loan_id':rec.company_id.punish_loan_id.id ,\
                                'total_installment':rec.period,\
                                'loan_amount': all_amount ,
                                'salary_refund':rec.installment,
                                'addendum_refund' : 1,
                                'state':'draft',
                                'start_date':rec.start_date,
                                'comments':'أقساط عقوبات',
                                'addendum_install_no' : 1 , }, context)
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid , 'hr.employee.loan' , loan_id , 'cooperative_loan_paid' ,cr )
                loan_obj.write(cr ,uid , loan_id , {'state' : 'paid'},context = context)



                self.write(cr, uid, [rec.id], {'loan_id': loan_id,'penalty_amount':all_amount}, context=context) 


        return self.write(cr, uid, ids, {'state':'implement'}, context=context)


    
    def implement_penalty_old(self, cr, uid, ids, context=None):
        """
        Creates Record  in hr_allowance_deduction_exception object.

        @return: Boolean True
        """
        all_amount = 0.0
        employee_exception_line_obj = self.pool.get('hr.allowance.deduction.exception')
        payroll_obj = self.pool.get('payroll')
        create_lines = {}
        for rec in self.browse(cr, uid, ids, context=context):
            rec_employee_exception = []
            if rec.penalty:
                for punishment_id in rec.punishments_ids:
                    if punishment_id.penalty:
                        emp = rec.employee_id
                        allow_dict=payroll_obj.allowances_deductions_calculation(cr,uid,rec.start_date,emp,{'no_sp_rec':True}, [ punishment_id.allow_deduct.id], False,[])
                        amount = round(allow_dict['total_deduct']*rec.factor,2)

                        create_lines[(rec.employee_id.otherid,
                        rec.employee_id.id,rec.start_date,rec.end_date,
                        punishment_id.allow_deduct.id,
                        punishment_id.allow_deduct.name_type)] = create_lines.get( (rec.employee_id.otherid,
                        rec.employee_id.id,rec.start_date,rec.end_date,
                        punishment_id.allow_deduct.id,
                        punishment_id.allow_deduct.name_type),0.0)

                        create_lines[(rec.employee_id.otherid,
                        rec.employee_id.id,rec.start_date,rec.end_date,
                        punishment_id.allow_deduct.id,
                        punishment_id.allow_deduct.name_type)] += amount
                        all_amount += all_amount
                    
                for line in create_lines.keys():
                    emp_line = {
                        'code':line[0],
                        'employee_id':line[1],
                        'start_date':line[2],
                        'end_date':line[3],
                        'allow_deduct_id':line[4],
                        'amount':create_lines[line],
                        'types':'deduct',
                        'action':'special',
                        'types':line[5],
                    }
                    employee_exception_id = employee_exception_line_obj.create(cr, uid, emp_line, context=context)
                    rec_employee_exception.append(employee_exception_id)
                self.write(cr, uid, [rec.id], {'employee_exception_ids': [[6,0,rec_employee_exception ]],'penalty_amount':all_amount}, context=context) 


        return self.write(cr, uid, ids, {'state':'implement'}, context=context)
    
    def set_to_draft(self, cr, uid, ids, context=None):
        """
        Method reset the workflow and change state to 'draft'.
        
        @return: Boolean True
        """
        for rec in self.browse(cr, uid, ids, context=context):
            for excep in rec.employee_exception_ids:
                excep.unlink()
            if rec.loan_id:
                rec.loan_id.write({'state' : 'rejected'})
        self.write(cr, uid, ids, {'employee_exception_ids':[[5]]}, context=context) 
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.violation', id, cr)
            wf_service.trg_create(uid, 'hr.employee.violation', id, cr)
        return True

#----------------------------------------
#Allowance Deduction Exception
#----------------------------------------           
class hr_allowance_deduction_exception(osv.osv):
    _inherit = "hr.allowance.deduction.exception"

    # _sql_constraints = [('unique_check', 'CHECK(1<1)', _('You Can Not Duplicate Two Exception Records With The Same Information!')),]

    # def check_unique(self, cr, uid, ids, context=None):
    #     for rec in self.browse(cr, uid, ids, context=context):
    #         if self.search(cr, uid, [('id','!=',rec.id), ('employee_id','=',rec.employee_id.id), 
    #         ('action','=',rec.action), ('types','=',rec.types), 
    #         ('allow_deduct_id','=',rec.allow_deduct_id.id), 
    #         ('start_date','=',rec.start_date),]):
    #             raise osv.except_osv(_('Erorr!'), _('You Can Not Duplicate Two Exception Records With The Same Information!'))

    #     return True

    # _constraints = [
    #     (check_unique, '', ['employee_id','action','types','allow_deduct_id','start_date'])
    # ]
