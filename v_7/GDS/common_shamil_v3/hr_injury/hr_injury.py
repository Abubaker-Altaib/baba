# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp


class hr_config_settings_inherit(osv.osv_memory):
    """
    Inherits hr.config.settings to treatment account .""" 
    
    _inherit = 'hr.config.settings'

    _columns = {
              'treatment_account_id':fields.related('company_id','treatment_account_id',type='many2one', relation='account.account',string='Treatment Account' ,domain="[('type', '!=', 'view')]",help="This account will be used for Treatment"),
               }


    def get_default_treatment_account_id(self, cr, uid, ids, context=None):
        """
	Method that get the defult Treatment account.

        @return: Dictionary of values
        """         
        treatment_account = self.pool.get("ir.config_parameter").get_param(cr, uid, "treatment_account_id", context=context)
        return {'treatment_account_id': treatment_account}

    def set_treatment_account_id(self, cr, uid, ids, context=None):
        """
	Method that set the defult Treatment account.

        @return: Dictionary of values
        """ 
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "treatment_account_id", record.treatment_account_id.id or False, context=context)


class hr_injury(osv.Model):
    _name = "hr.injury"
    _description = "Injury "

    def _compute_emp_payroll(self, cr, uid,ids,field_name, arg,context={}):
        """
	Method that computes the salary of employee for one day.

        @return: Dictionary of values
        """
        salary_degree_obj = self.pool.get('hr.salary.degree')
        payroll_obj = self.pool.get('payroll')
        pay_id=self.browse(cr,uid,ids,context=context)
        pay_id=pay_id[0].id
        res = {}
        for pay in self.browse(cr,uid,[pay_id],context):
            res[pay.id] = {}
            total_amount=0.0
            amount=0.0
            if pay.inability_types.allowances_id:
               allow_ids= [pay.inability_types.allowances_id.id]
               total_amount = payroll_obj.read_allowance_deduct(cr, uid,pay.name.id,allow_ids,'allow')
               started_section_ids = salary_degree_obj.search(cr,uid,[('payroll_id','=',pay.name.payroll_id.id),('id','=',pay.name.degree_id.id)],context=context)
               if started_section_ids:
                  started_section= salary_degree_obj.browse(cr,uid,started_section_ids,context=context)[0]
                  total_amount += started_section.basis
                  total_amount+= pay.name.bonus_id.basic_salary
               total_amount = total_amount / 30
            res[pay.id]['employee_payroll']= total_amount
        return res


    _columns = {  
                 'name': fields.many2one('hr.employee', "Employee", required=True, domain="[('state','!=','refuse')]"),
                 'department_id':fields.related('name', 'department_id', string='Department', type='many2one', relation='hr.department', readonly=True, store=True),
                 'type':fields.selection([('treatment', 'Treatment'), ('compensation', 'Compensation'),('all', 'All')],'Type',required="1"),
                 'injury_type': fields.many2one('hr.injury.type', "Injury Type", domain="[('type','!=','injury_reason')]", required=True),
                 'injury_date' :fields.datetime("Injury Date", required=True),
                 'injury_reason':fields.many2one('hr.injury.type' , "Injury Reasons", domain="[('type','=','injury_reason')]", required=True),
		 'inability_types':fields.many2one('hr.inability.type' , "Inability Types",),
                 'inability_percentage':fields.float("Inability percentage", digits=(18, 2),),
                 'inability_amount':fields.float("Inability Amount", digits=(18, 2),),
                 'inability_date' :fields.datetime("Inability Date"),
                 'accident_address':fields.text("Accident Address", size=15),
                 'work_type' :fields.text("Work Type", size=15),
                 'first_witness': fields.char("First witness", size=100 , required=True),
                 'second_witness': fields.char("Second witness", size=100 , required=True),
                 'state': fields.selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'),
                 ('validate1', 'Waiting Second Approval'), ('validate2', 'Waiting Third Approval'), ('validate3', 'Approved'), ('cancel', 'Cancelled')],
                 'State', readonly=True),
                 'employee_payroll': fields.function(_compute_emp_payroll, method=True,type='float', digits=(18, 2), string='employee_payroll',readonly=True, 
                 store={'hr.injury': (lambda self, cr, uid, ids, c={}: ids, ['name'], 5),},multi='all'),
                 'treatment_amount' :fields.float("Treatment Amount", digits=(18, 2)),
                 'invoice_no' :fields.integer("Invoice No", required=True),
	         'acc_number' :fields.many2one('account.voucher',"Accounting Number",readonly=True), 
                 'inability_acc_number' :fields.many2one('account.voucher','Inability Accounting Number' , readonly=True),
                 'recipient_name' :fields.char('recipient Name', size=64 , readonly=False),
       	         'transfer' :fields.boolean('Transfered', readonly=True),
       	         'compensation_transfer':fields.boolean('Transfered', readonly=True),
                 'date' :fields.date("Transfer Date", required=False),#required=True

               }
    _defaults = {
        'state': 'draft',
        'type': 'all',
        'name': lambda * a:False,
                 }

    def onchange_employee(self, cr, uid, ids, emp_id,context={}):
        """
	Method that returns the domain of employee_type that allowed to undergone the process.

        @param emp_id: Id of employee
        @return: Dictionary of values
        """
        emp_obj = self.pool.get('hr.employee')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        contractors = company_obj.injury_contractors
        employee = company_obj.injury_employee
        recruit = company_obj.injury_recruit
        trainee = company_obj.injury_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        domain = {'name':employee_domain['employee_id']}
        return { 'domain': domain}

    def create(self, cr, uid,vals,context={}):
        """
	Method that overwrites create method  and do nothing.

        @param vals: Values that have been entered
        @return: Integer ID of the created record
        """
        salary_degree_obj = self.pool.get('hr.salary.degree')
        payroll_obj = self.pool.get('payroll')
        compensation_id = super(osv.osv,self).create(cr, uid, vals,context=context)
        return compensation_id


    def calculate(self, cr, uid, ids, context={}):
        """
	Method that returns True.

        @return: Boolean True
        """
        return True

    def transfer(self, cr, uid, ids, context={}):
        """
	Method that returns True  .

        @return: Boolean True
        """
        return True
 
    def confirm(self, cr, uid, ids, context={}):
        """
	Workflow method that changes the state to 'confirm'.
        
	@return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context) 

    def validate1(self, cr, uid, ids, context={}):
        """
	Workflow method that changes the state to 'validate1'.

        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'validate1'}, context=context)

    def validate2(self, cr, uid, ids, context={}):
        """
	Workflow method that changes the state to 'validate2'.

        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'validate2'}, context=context)

    def validate3(self, cr, uid, ids, context={}):
        """
	Workflow method that changes the state to 'validate3'.

        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'validate3'}, context=context)

    def refuse(self, cr, uid, ids, context={}):
        """
	Workflow method that changes the state to 'refuse'.
        
	@return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'refuse'}, context=context)
        return True

    def set_to_draft(self, cr, uid, ids, context={}):
        """
	Method that sets the workflow to the draft state.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft', }, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.injury', id, cr)
            wf_service.trg_create(uid, 'hr.injury', id, cr)
        return True



    def compute_compensation(self, cr, uid,compensation_id,context={}):
        """
	Mehtod that computes employee compensation from injury table and transfer the amount to voucher.

        @param compensation_id: Id of the injury record
        @return: Boolean True
        """
        payroll_obj = self.pool.get('payroll')
        for record in self.browse(cr,uid,compensation_id,context=context):
            total_amount=0.0
            allows_amount=0.0
            if record.inability_percentage <= 0.0 :
                   raise osv.except_osv(_('ERROR'), _('Inability percentage less than or equal zero '))
            if record.inability_types.allowances_id:
                  allow_ids= [record.inability_types.allowances_id.id]
                  allows_amount = payroll_obj.read_allowance_deduct(cr, uid,record.name.id,allow_ids,'allow')
                  total_amount=allows_amount*record.inability_percentage
            else :
                   raise osv.except_osv(_('ERROR'), _('The allowance for inability type is not existed'))
            self.write(cr, uid, compensation_id, {'inability_amount':total_amount, }, context=context)
        return True

#----------------------------------------
#injury types
#----------------------------------------

class hr_injury_type(osv.Model):
    _name = 'hr.injury.type'
    _description = "Injury's Type and Reason"
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char('Name', size=64, required=True),
        'type':fields.selection([('injury_type', 'Injury Type'), ('injury_reason', 'Injury Reason'),],'Type',required="1"),
                }
    _sql_constraints = [

       ('name_uniqe', 'unique (code)', 'you can not create same code !')
                      ]

#----------------------------------------
#inability types
#----------------------------------------

class hr_inability_type(osv.Model):
    _name = 'hr.inability.type'
    _description = "Inability type"
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char("Inability Types", size=64, required=True),
        'allowances_id' :fields.many2one('hr.allowance.deduction'  , 'Allowance' , domain=[('name_type','=','allow')]),
                }
    _sql_constraints = [

       ('name_uniqe', 'unique (code)', 'you can not create same code !')
                      ]

