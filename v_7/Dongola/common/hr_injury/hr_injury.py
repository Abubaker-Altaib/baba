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
from openerp import netsvc
import openerp.addons.decimal_precision as dp

class hr_config_settings_inherit(osv.osv_memory):
    """
    Inherits hr.config.settings to treatment account .
    """
    _inherit = 'hr.config.settings'

    _columns = {
              'treatment_account_id': fields.related('company_id','treatment_account_id',type='many2one', relation='account.account'
                                                     ,string='Treatment Account' ,domain="[('type', '!=', 'view')]",help="This account will be used for Treatment"),
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """Method that updates related fields of the company.
           @param company_id: Id of company
           
           @return: Dictionary of values 
        """
        values = {}
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            values=super(hr_config_settings_inherit,self).onchange_company_id(cr, uid, ids, company.id)
            values.get('value',{}).update({
                'treatment_account_id': company.treatment_account_id.id,
            })
        return values
#===============================================================================
#     def get_default_treatment_account_id(self, cr, uid, ids, context=None):
#         """
#         Method that get the default Treatment account.
# 
#         @return: Dictionary of values
#         """
#         treatment_account = self.pool.get("ir.config_parameter").get_param(cr, uid, "treatment_account_id", context=context)
#         return {'treatment_account_id': treatment_account}
# 
#     def set_treatment_account_id(self, cr, uid, ids, context=None):
#         """
#         Method that set the default Treatment account.
# 
#         @return: Dictionary of values
#         """ 
#         config_parameters = self.pool.get("ir.config_parameter")
#         for record in self.browse(cr, uid, ids, context=context):
#             config_parameters.set_param(cr, uid, "treatment_account_id", record.treatment_account_id.id or False, context=context)
#===============================================================================

class hr_injury_treatment(osv.Model):

    _name = "hr.injury.treatment"

    _description = "Injury Treatment"

    _columns = {
        'injury_id': fields.many2one('hr.injury', "Injury", required=True, ondelete='cascade'), 
        'treatment_amount' :fields.float("Treatment Amount", digits_compute=dp.get_precision('Payroll'), required=True),
        'invoice_no' :fields.char("Invoice No", size=100, required=True),
        'voucher_id' : fields.many2one('account.voucher',"Voucher Number",readonly=True),
    }

    _sql_constraints = [('number_positive', 'CHECK (treatment_amount>0.0)', _("Treatment amount should be positive number!")),]

    def copy_data(self, cr, uid, ids, default={}, context=None):
        """
        Inherit copy_data method that duplicate the defaults and set the voucher_id to False.
    
        @return: super copy method
        """
        default.update({'voucher_id': False})
        return super(hr_injury_treatment, self).copy_data(cr, uid, ids, default=default, context=context)


class hr_injury(osv.Model):

    _name = "hr.injury"

    _description = "Injury "

    def _compute_emp_payroll(self, cr, uid, ids, field_name, arg, context=None):
        """
        Method that computes the salary of employee for one day.

        @return: Dictionary of values
        """
        salary_degree_obj = self.pool.get('hr.salary.degree')
        payroll_obj = self.pool.get('payroll')
        pay_id = self.browse(cr, uid, ids, context=context)
        pay_id = pay_id[0].id
        res = {}
        for pay in self.browse(cr, uid, [pay_id], context):
            res[pay.id] = {}
            total_amount = 0.0
            if not pay.inability_types.allowances_id:
                raise orm.except_orm(_('Error'), _('Inability type allowance is not exist.'))
            payroll=payroll_obj.allowances_deductions_calculation(cr, uid,pay.date,pay.employee_id,{}, [pay.inability_types.allowances_id.id])
            total_amount=payroll['result'][0]['amount']/30
            res[pay.id]['employee_payroll'] = total_amount
        return res

    _columns = {
        'name': fields.char('Name', size=64, required=True),
         'employee_id': fields.many2one('hr.employee', "Employee", required=True),
         'department_id':fields.related('employee_id', 'department_id', string='Department', type='many2one', relation='hr.department', readonly=True, store=True),
         'type':fields.selection([('treatment', 'Treatment'), ('compensation', 'Compensation'), ('all', 'All')], 'Type', required="1"),
         'injury_type': fields.many2one('hr.injury.type', "Injury Type", domain="[('type','!=','injury_reason')]", required=True),
         'injury_date' :fields.datetime("Injury Date", required=True),
         'injury_reason':fields.many2one('hr.injury.type' , "Injury Reasons", domain="[('type','=','injury_reason')]", required=True),
         'inability_types':fields.many2one('hr.inability.type' , "Inability Type",),
         'inability_percentage':fields.float("Inability percentage", digits_compute=dp.get_precision('Payroll'),),
         'inability_amount':fields.float("Inability Amount", digits_compute=dp.get_precision('Payroll'),),
         'inability_date' :fields.datetime("Inability Date"),
         'accident_address':fields.text("Accident Address", size=15),
         'work_type' :fields.text("Work Type", size=15),
         'first_witness': fields.char("First witness", size=100 , required=True),
         'second_witness': fields.char("Second witness", size=100 , required=True),
         'state': fields.selection([('draft', 'Draft'), ('complete', 'Waiting for Department Manager'),
                                    ('confirm', 'Waiting for HR Manager'), ('validate', 'Waiting for General Manager'),
                                     ('refuse', 'Refused'), ('approve', 'Approved'), ('cancel', 'Cancelled')], 'State', readonly=True),
         'employee_payroll': fields.function(_compute_emp_payroll, method=True, type='float', digits_compute=dp.get_precision('Payroll'), string='Employee Payroll', readonly=True,
                                             store={'hr.injury': (lambda self, cr, uid, ids, c={}: ids, ['employee_id'], 5), }, multi='all'),
         'inability_voucher_id' :fields.many2one('account.voucher','Inability Voucher Number' , readonly=True),
         'date' :fields.date("Date", required=True),
         'recipient_name' :fields.char('recipient Name', size=64 , readonly=False),
         'treatment_ids': fields.one2many('hr.injury.treatment', 'injury_id', 'Treatment'),
         'treatment_start': fields.date("Treatment Start Date"),
         'treatment_end': fields.date("Treatment End Date"),
    }

    _defaults = {
        'name': '/',
        'state': 'draft',
        'type': 'all',
        'employee_id': False,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Inherit copy method that duplicate the defaults and set the inability_voucher_id to False.
        
        @return: ID of new record copied
        """
        default.update({'name': '/', 'state':'draft','inability_voucher_id':False})
        return super(hr_injury, self).copy(cr, uid, ids, default=default, context=context)

    def unlink(self, cr, uid, ids, context = None):
        """
        Inherit unlink method to prevent deleting record in nundraft state
        
        @return: raise an exception if record state is not draft
        """
        if self.search(cr, uid, [('id' ,'in', ids), ('state', '!=', 'draft')], context=context):
            raise orm.except_orm(_('Invalid action'), _('Can not  delete not draft records!'))
        return super(hr_injury, self).unlink(cr, uid, ids, context = context)

    def onchange_employee(self, cr, uid, ids, emp_id, context=None):
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
        domain = {'employee_id':employee_domain['employee_id']+[('state','!=','refuse')]}
        return {'domain': domain}

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
    def calculate(self, cr, uid, ids, context=None):
        """
        @return: Boolean True
        """
        return True

    def transfer(self, cr, uid, ids, context=None):
        """
        @return: Boolean True
        """
        return True

    def complete(self, cr, uid, ids, context=None):
        """
        Workflow method that changes the state to 'complete'.
        
        @return: Boolean True
        """
        
        for r in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'state':'complete', 'name': r.name == '/' and 
                                     self.pool.get('ir.sequence').get(cr, uid, 'hr.injury') or 
                                     r.name}, context=context)
        return True

    def confirm(self, cr, uid, ids, context=None):
        """
        Workflow method that changes the state to 'confirm'.

        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)

    def validate(self, cr, uid, ids, context=None):
        """
        Workflow method that changes the state to 'validate'.

        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'validate'}, context=context)

    def approve(self, cr, uid, ids, context=None):
        """
        Workflow method that changes the state to 'approve'.

        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'approve'}, context=context)

    def refuse(self, cr, uid, ids, context=None):
        """
        Workflow method that changes the state to 'refuse'.
        
        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'refuse'}, context=context)
        return True

    def set_to_draft(self, cr, uid, ids, context=None):
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

    def compute_compensation(self, cr, uid, compensation_id, context=None):
        """
        Method that computes employee compensation from injury table and transfer the amount to voucher.

        @param compensation_id: Id of the injury record
        @return: Boolean True
        """
        for record in self.browse(cr, uid, compensation_id, context=context):
            if record.inability_percentage <= 0.0 :
                raise orm.except_orm(_('Error'), _('Inability percentage must be greater than zero.'))
            total_amount = record.employee_payroll * record.inability_percentage/100 * record.inability_types.factor
            self.write(cr, uid, record.id, {'inability_amount': total_amount}, context=context)
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
        'type':fields.selection([('injury_type', 'Injury Type'), ('injury_reason', 'Injury Reason'), ], 'Type', required="1"),
    }

    _sql_constraints = [
       ('name_uniqe', 'unique (name,type)', 'Injury name from the same type must be unique!')
    ]

#----------------------------------------
#inability types
#----------------------------------------

class hr_inability_type(osv.Model):

    _name = 'hr.inability.type'

    _description = "Inability type"

    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char("Inability Type", size=64, required=True),
        'allowances_id': fields.many2one('hr.allowance.deduction'  , 'Allowance' , domain=[('name_type', '=', 'allow')], required=True),
        'factor': fields.float("Factor", digits_compute=dp.get_precision('Payroll')),
    }

    _sql_constraints = [
       ('name_uniqe', 'unique (name)', 'Inability type name must be unique!'),
       ('code_uniqe', 'unique (code)', 'Inability type code must be unique!')
    ]
