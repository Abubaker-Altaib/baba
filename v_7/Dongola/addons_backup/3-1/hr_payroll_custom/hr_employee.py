# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from openerp import netsvc
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import mx

#----------------------------------------
#hr job(inherit)
#----------------------------------------
class hr_job(osv.osv):
 
    _inherit = "hr.job"
    """Inherits hr.job adds field to define the job for specific degrees.
    """
    _columns = {
         'degree_ids':fields.many2many('hr.salary.degree', 'job_degree_rel', 'degree_id', 'job_id', 'Degrees'),
    }
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """
        Method that overwrites name_search method Search for employee (only employees 
        that requested trainings) and their display name.

        @param name: Object name to search
        @param args: List of tuples specifying search criteria
        @param operator: Operator for search criterion
        @param limit: Max number of records to return
        @return: Super name_search method 
        """
        if not context : context = {}
        if 'allow_job_ids' in context:
            job_ids = [i[2]['job_id'] for i in context['allow_job_ids']]
            if job_ids : args.append(('id', 'not in',job_ids))
        return super(hr_job, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

#----------------------------------------
#Employee(inherit)
#----------------------------------------
class hr_employee(osv.osv):

    def check_no_of_emp(self, cr, uid, ids, context=None):
        """Method checks if employee's degree allows it to occupy the job or not.
           @return: Boolean True or False
        """
        for employee in self.browse(cr, uid, ids, context=context):
            if employee.job_id.degree_ids and employee.degree_id.id not in [deg.id for deg in employee.job_id.degree_ids]:
                return False
            #return False
        return True
    def _salary_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for emp in self.browse(cr, uid, ids, context=context):
            salary_total= emp.bonus_id.basic_salary or 0 
            for salary in emp.emp_salary_ids:
                if  salary.type=='allow' and not salary.allow_deduct_id.special:
                    salary_total += salary.amount or 0
                else:
                    salary_total -=  salary.amount or 0
                    
            res[emp.id]=salary_total
        return res 
    def _get_salary(self, cr, uid, ids, context=None):
        result = {}
        for e in self.pool.get('hr.employee.salary').browse(cr, uid, ids, context=context):
            result[e.employee_id.id] = True
        return result.keys() 

    def onchange_payroll(self, cr, uid, ids, payroll_id , degree_id ,flag ,context=None):
        domain = {'degree_id':[('payroll_id','=',payroll_id)],
                  'bonus_id':[('degree_id','=',degree_id)]}
        if payroll_id and (degree_id and flag) or (not degree_id and flag):
           return {'value': {'bonus_id':False} , 'domain': domain}
        if payroll_id and not degree_id and not flag :
           return {'value': {'degree_id':False,'bonus_id':False} , 'domain': domain}
        if payroll_id and degree_id and not flag :
           domain['bonus_id']=[('degree_id', '=', False)]
           return {'value': {'degree_id':False,'bonus_id':False} ,'domain': domain}

    _inherit = "hr.employee"
    _columns = {
        'payroll_id' : fields.many2one('hr.salary.scale', 'Salary Scale' ,  readonly=True, states={'draft':[('readonly', False)]},ondelete="restrict"),
        'degree_id' : fields.many2one('hr.salary.degree', 'Degree', readonly=True, states={'draft':[('readonly', False)]},ondelete="restrict"),
        'bonus_id':fields.many2one('hr.salary.bonuses', "Bonus" , readonly=True, states={'draft':[('readonly', False)]},ondelete="restrict"),
        'salary_suspend' : fields.boolean('Salary Suspend', readonly=True),
        'tax_exempted' : fields.boolean('Tax Exempted'),
        'substitution' : fields.boolean('Substitution', readonly=True),
        'tax':fields.float("Tax", digits_compute=dp.get_precision('Payroll')),
        'emp_salary_ids':fields.one2many('hr.employee.salary', 'employee_id', "Employee Salary", readonly=True),
        'bonus_date' :fields.date("Bonus Date"),
        'promotion_date' : fields.date('Promotion Date'),
        'salary_total': fields.function(_salary_all, digits_compute= dp.get_precision('Payroll'), string='Total Net',
                                         store={ 'hr.employee.salary': (_get_salary, None, 10)}),
    }

    

    def write_employee_salary(self, cr, uid, emp_ids, allow_deduct_list):
        """Method to compute all employee's allowances and deductions when create or write on employee object.
           @param emp_ids: List of employees ids
           @param allow_deduct_list: List of allowances/deductions ids
           @return: True
        """
        payroll_obj = self.pool.get('payroll')
        date = time.strftime('%Y-%m-%d')
        for emp in self.browse(cr, uid, emp_ids):
            allow_deduct_dict = payroll_obj.allowances_deductions_calculation(cr, uid, date, emp, {}, allow_deduct_list , False, [])
            write_allow_deduct = payroll_obj.write_allow_deduct(cr, uid, emp.id, allow_deduct_dict['result'])
        return True

    def employee_move_bonus_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        """Scheduler to check the employee current bouns and move bonus 
        @return True
        """
        date=time.strftime('%Y-%m-%d')
        hr_salary_bonuses_obj = self.pool.get('hr.salary.bonuses')
        emp_ids = self.search(cr,uid,[('state','=','approved')])
        today = datetime.strptime(date,"%Y-%m-%d")
        for rec in self.browse(cr, uid, emp_ids):
            bounce_date = datetime.strptime(rec.bonus_date,"%Y-%m-%d")
            date_diff = bounce_date - today
            total_date = 1+ abs(date_diff.days)
            if total_date >= rec.bonus_id.margin_time and rec.state == 'approved':
                bouns = hr_salary_bonuses_obj.search(cr,uid,[('sequence','=',rec.bonus_id.sequence+1),('payroll_id','=',rec.payroll_id.id),('degree_id','=',rec.degree_id.id)])
                if bouns :
                    for bouncs_rec in hr_salary_bonuses_obj.browse(cr,uid,bouns):
                        self.write(cr, uid,[rec.id] ,{'bonus_id':bouncs_rec.id,'bonus_date':date})
        return True

    def create(self, cr, uid, vals, context=None):
        """Method that adds a new employee and calls write_employee_salary method to write his salary.
           @param vals: Dictionary contains the entered data
           @return: Id of the created employee
        """
        emp_create = super(hr_employee, self).create(cr, uid, vals, context=None)
        update = self.write_employee_salary(cr, uid, [emp_create], [])
        return emp_create

    def write(self, cr, uid, ids, vals, context=None):
        """Method that overwrites write method and checks if any changes happend in the fields that related to salary then calls 
           write_employee_salary method to re-calculates the salary reflicts the chages.
           @param vals: Dictionary contains the entered data
           @return: Boolean True
        """
        emp_write = super(hr_employee, self).write(cr, uid, ids, vals)
        update_field = [key for key in vals.keys() if key in ('payroll_id', 'degree_id', 'bonus_id', 'job_id','department_id', 'status', 'state', 'tax_exempted', 'category_ids', 'company_id', 'substitution')]
        if update_field:
            update = self.write_employee_salary(cr, uid, ids, [])
        return emp_write

    def unlink(self, cr, uid, ids, context=None):
        """Method that overwrites unlink method and prevents the deletion of employee not in the 'draft' state and 
           the referenced employee in the hr.payroll.main.archive.
           @return: Super unlink method
        """
        for e in self.browse(cr, uid, ids):
            if e.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You cannot delete an employee which is not in draft state !'))
            check_reference = self.pool.get("hr.payroll.main.archive").search(cr, uid, [('employee_id', '=', e.id)])
            if check_reference:
                raise osv.except_osv(_('Warning!'), _('You cannot delete this employee which is referenced !'))
            delete_user = e.user_id and self.pool.get('res.users').unlink(cr, uid, [e.user_id.id],context=context)
        return super(osv.osv, self).unlink(cr, uid, ids, context)

#----------------------------------------
#employee salary in employee record
#----------------------------------------
class hr_employee_salary(osv.osv):
    _name = "hr.employee.salary"
    _description = "Employee's Salary"
    _columns = {
        'employee_id' : fields.many2one('hr.employee', "Employee", required=True, readonly=True , ondelete='cascade', select=1),
        'allow_deduct_id':fields.many2one('hr.allowance.deduction', 'Name', required=True, readonly=True, ondelete='cascade', select=1),
        'type':fields.selection([('allow', 'Allowance'), ('deduct', 'Deduction')], 'Type', required=True),
        'amount' :fields.float("Amount", digits_compute=dp.get_precision('Payroll'), readonly=True),
        'holiday_amount' :fields.float("Holiday Amount", digits_compute=dp.get_precision('Payroll'), readonly=True),
        'remain_amount' :fields.float("Remain Amount", digits_compute=dp.get_precision('Payroll'), readonly=True),
        'tax_deducted' :fields.float("Tax Deducted", digits_compute=dp.get_precision('Payroll'), readonly=True),
    }

class qualification(osv.osv):
    _inherit = "hr.qualification"
    """Inherets hr.qualification and adds method to update the qualification amount for the employees 
       if change the amount or the order of the qualification.
    """  
    def write(self, cr, uid, ids, vals, context):
        """Method that overwrites write method and recalulates qualification allowance's amount for the employees
           if change the amount or the order of the qualification.
           @param vals: Dictionary contains the entered values
           @return: Boolean True
        """
        write_allow_deduct = super(osv.osv, self).write(cr, uid, ids, vals, context)
        if 'amount' in vals or 'order' in vals:
            allow_deduct_obj = self.pool.get('hr.allowance.deduction')
            for qual in self.browse(cr, uid, ids):
                allow_deduct_ids = allow_deduct_obj.search(cr, uid, [('allowance_type', '=', 'qualification'),('in_salary_sheet', '=', True)])
                update = self.pool.get('payroll').change_allow_deduct(cr, uid, allow_deduct_ids, [])
        return write_allow_deduct
#----------------------------------------
# Employee Qualification 
#----------------------------------------
class hr_employee_qualification(osv.osv):
    """Inherets hr.employee.qualification .
    """
    _inherit = "hr.employee.qualification"

    def unlink(self, cr, uid, ids, context=None):
        """Method that overwrites unlink method where it deletes employee's qualification and re-calculates its salary.
           @return: Id of the deleted record
        """
        employee_obj = self.pool.get('hr.employee')
        for qualification in self.browse(cr, uid, ids):
            emp_id = qualification.employee_id.id
            delete = super(hr_employee_qualification, self).unlink(cr, uid, ids, context=context)
            employee_obj.write_employee_salary(cr, uid, [emp_id], [])
        return delete

    def approve_quali(self, cr, uid, ids, context=None):
        """Workflow function that changes the state to 'approved' and re-calculates the salary.
           @return: Boolean True
        """
        employee_obj = self.pool.get('hr.employee')
        self.write(cr, uid, ids, { 'state' : 'approved' }, context=context)
        for qualification in self.browse(cr, uid, ids, context=context):
            employee_obj.write_employee_salary(cr, uid, [qualification.employee_id.id], [])
        return True

    def reject_quali(self, cr, uid, ids, context=None):
        """Workflow function that changes the state to 'rejected' and re-calculates the salary.
           @return: Boolean True
        """
        employee_obj = self.pool.get('hr.employee')
        for qualification in self.browse(cr, uid, ids):
            employee_obj.write_employee_salary(cr, uid, [qualification.employee_id.id], [])
        return self.write(cr, uid, ids, { 'state' : 'rejected' }, context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        """Method function that sets the state to 'draft' and re-calculates the salary.
           @return: Boolean True
        """
        employee_obj = self.pool.get('hr.employee')
        for qualification in self.browse(cr, uid, ids, context=context):
            employee_obj.write_employee_salary(cr, uid, [qualification.employee_id.id], [])
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.qualification', id, cr)
            wf_service.trg_create(uid, 'hr.employee.qualification', id, cr)
        return self.write(cr, uid, ids, {'state': 'draft' }, context=context)

#----------------------------------------
#Employee Family Relation(inherit)
#----------------------------------------
class family_relation(osv.osv):
    _inherit = "hr.family.relation"

    def write(self, cr, uid, ids, vals, context=None):
        """Method that overwrites write method and re-calculates employees' family relation allowance when changes the amount.
           @return: Boolean True 
        """
        write_allow_deduct = super(family_relation, self).write(cr, uid, ids, vals, context=context)
        if 'social_benefit_amount' in vals:
            allow_deduct_obj = self.pool.get('hr.allowance.deduction')
            allow_deduct_ids = allow_deduct_obj.search(cr, uid, [('allowance_type', '=', 'family_relation')], context=context)
            update = self.pool.get('payroll').change_allow_deduct(cr, uid, allow_deduct_ids, [])
        return write_allow_deduct
#----------------------------------------
#Employee Family (inherit)
#----------------------------------------
class employee_family(osv.osv):
    _inherit = "hr.employee.family"

    def unlink(self, cr, uid, ids, context=None):
        """Method that overwrites unlink method where it deletes family relation record and re-write employee salary.
           @return: Ids of the deleted records 
        """
        employee_obj = self.pool.get('hr.employee')
        for relation in self.browse(cr, uid, ids, context=context):
            employee_id = relation.employee_id.id
            delete = super(employee_family, self).unlink(cr, uid, ids, context=context)
            update = employee_obj.write_employee_salary(cr, uid, [employee_id], [])
        return delete

    def mymod_approved(self, cr, uid, ids, context=None):
        """Workflow function that changes the state to 'approved' and re-writes employee's salary.
           @return: Boolean True 
        """
        employee_obj = self.pool.get('hr.employee')
        vals = { 'state' : 'approved' }
        for relation in self.browse(cr, uid, ids, context=context):
            if not relation.start_date:
                vals['start_date'] = time.strftime('%Y-%m-%d')
        self.write(cr, uid, ids, vals, context=context)
        employee_obj.write_employee_salary(cr, uid, [relation.employee_id.id], [])
        return True

    def mymod_stopped(self, cr, uid, ids, context=None):
        """Workflow function that changes the state to 'stopped' (de-activate family relation record effects in employee's salary)
           and re-writes employee's salary.
           @return: Boolean True 
        """
        employee_obj = self.pool.get('hr.employee')
        vals = { 'state' : 'stopped' }
        for relation in self.browse(cr, uid, ids, context=context):
            if not relation.end_date:
                vals['end_date'] = time.strftime('%Y-%m-%d')
        self.write(cr, uid, ids, vals, context=context)
        employee_obj.write_employee_salary(cr, uid, [relation.employee_id.id], [])
        return True


    def set_to_draft(self, cr, uid, ids, context=None):
        """Method that sets the state to 'draft' and re-writes employee's salary.
           @return: Boolean True 
        """
        employee_obj = self.pool.get('hr.employee')
        self.write(cr, uid, ids, {'state': 'draft' }, context=context)
        for relation in self.browse(cr, uid, ids, context=context):
            update = employee_obj.write_employee_salary(cr, uid, [relation.employee_id.id], [])
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.family', id, cr)
            wf_service.trg_create(uid, 'hr.employee.family', id, cr)
        return True
#----------------------------------------
#Hr dismissal
#----------------------------------------
class hr_dismissal(osv.Model):

    _inherit = "hr.dismissal"
        
    _columns = {
        'allowance_ids' :fields.many2many('hr.allowance.deduction', 'hol_allow_dismissal_rel', 'dismissal_id' , 'allow_id' , "Allowances" , domain="[('name_type', '=', 'allow'), ('allowance_type', '=', 'serv_terminate')]"),

   }
#----------------------------------------
#employment termination (inherit)
#----------------------------------------
class hr_employment_termination(osv.Model):
    """Inherits hr.employment.termination and adds some fields to be used when calculates and transfers employee's end of service allowance.
    """
    _inherit = "hr.employment.termination"
    _columns = {
        'date' :fields.date("Allowance Calculation Date", readonly=True),
        'line_ids':fields.one2many('hr.employment.termination.lines', 'termination_id', "Allowances"),
        'acc_number' :fields.many2one("account.voucher",'Voucher',readonly=True), 
        'state': fields.selection([('draft', 'Draft'), ('refuse', 'Out Of Service'), ('calculate', 'Calculated'),
                                   ('transfer', 'Transferred'), ], 'State', readonly=True),
    }

    def calculation(self, cr, uid, ids, transfer , context=None):
        """Method that calculates employee's end of service allowance and adds a record to hr.employment.termination.lines.
           @return: Boolean True 
        """
        transfer = transfer ==True and transfer or False
        payroll = self.pool.get('payroll')
        allow_list=[]
        for rec in self.browse(cr, uid, ids, context=context):
            self.pool.get('hr.employment.termination.lines').unlink(cr, uid, [l.id for l in rec.line_ids], context)
            exception_allow_deduct_obj = self.pool.get('hr.allowance.deduction.exception')
            allow_ids = exception_allow_deduct_obj.search(cr, uid, [('employee_id', '=', rec.employee_id.id), ('action', '=', 'special'), ('types', '=', 'allow')])
            allow = exception_allow_deduct_obj.browse(cr, uid, allow_ids)
            deduct_ids = exception_allow_deduct_obj.search(cr, uid, [('employee_id', '=', rec.employee_id.id), ('action', '=', 'special'), ('types', '=', 'deduct')])
            deduct = exception_allow_deduct_obj.browse(cr, uid, deduct_ids)
            total_allow=0
            for a in allow:
                current_date = mx.DateTime.Parser.DateTimeFromString(rec.dismissal_date)
                end_date = mx.DateTime.Parser.DateTimeFromString(a.end_date) 
                emp_end_date_days = (end_date - current_date).days
                day=a.amount/30
                allownce=emp_end_date_days*day
                #print"total" ,total_allow ,emp_end_date_days ,allownce ,a ,a.allow_deduct_id.account_id.id,a.id
                allownce_id=self.pool.get('hr.employment.termination.lines').create(cr, uid,{'allow_deduct_id':a.allow_deduct_id.id,
                                                                                     'account_id':a.allow_deduct_id.account_id.id,
                                                                                     'termination_id':rec.id,
                                                                                     'amount':allownce,
                                                                                     'name':a.allow_deduct_id.name})
                allow_list.append(allownce_id)
            
            for d in deduct:
                current_date = mx.DateTime.Parser.DateTimeFromString(rec.dismissal_date)
                end_date = mx.DateTime.Parser.DateTimeFromString(a.end_date) 
                emp_end_date_days = (end_date - current_date).days
                day=d.amount/30
                deduct=emp_end_date_days*day
                #print"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$deduct" ,emp_end_date_days ,deduct ,d.id
                deduct_id = self.pool.get('hr.employment.termination.lines').create(cr, uid,{'allow_deduct_id':d.allow_deduct_id.id,
                                                                                     'account_id':d.allow_deduct_id.account_id.id,
                                                                                     'termination_id':rec.id,
                                                                                     'amount':-deduct,
                                                                                     'name':d.allow_deduct_id.name})
                allow_list.append(deduct_id)

            allowance_ids = rec.dismissal_type.allowance_ids 
        if not allowance_ids:
            raise orm.except_orm(_('Sorry'), _('No Allwances to be calculated'))
        for allow in allowance_ids:
            amount = payroll.compute_allowance_deduction(cr, uid, rec.employee_id, allow.id)
            line_id=self.pool.get('hr.employment.termination.lines').create(cr, uid,{'allow_deduct_id':allow.id,
                                                                                     'account_id':allow.account_id.id,
                                                                                     'termination_id':rec.id,
                                                                                     'amount':amount['amount'],
                                                                                     'name':allow.name})
            allow_list.append(line_id)
        self.write(cr, uid, ids, { 'state' : 'calculate' , 'date':time.strftime('%Y-%m-%d')}, context=context)
        return  allow_list

    def transfer(self, cr, uid, ids, context=None ):
        """Method that transfers employee's end of service allowance to voucher.
           @return: Boolean True 
        """
        lines = []
        for rec in self.browse(cr, uid, ids):
            transfer=True
            allow_rec = self.pool.get('hr.employment.termination.lines').browse(cr, uid,rec.calculation(transfer))
            if not allow_rec:
                raise orm.except_orm(_('Sorry'), _('No Allwances to be transferred '))
            reference = 'HR/Allowances/End_Service/ ' + rec.employee_id.name + " / " + str(rec.date)
            for line in allow_rec:
                line = {
                  'name' :line.name,
                  #'allow_deduct_id':allwo.allow_deduct_id.id,
                  'amount':line.amount,
                  'account_id':line.account_id.id,
                }
                lines.append(line)
            voucher = self.pool.get('payroll').create_payment(cr, uid, ids, {'reference':reference, 'lines':lines}, context=context)
            self.write(cr, uid, ids, { 'state' : 'transfer', 'acc_number':voucher}, context=context)
        return True

#----------------------------------------
#employment termination allowances
#----------------------------------------
class hr_employment_termination_lines(osv.Model):

    _name = "hr.employment.termination.lines"
    _description = "Employment Termination's Allowance Archive"
    _columns = {
         'name':fields.char("Name", size=50 , required=True),
         'allow_deduct_id': fields.many2one('hr.allowance.deduction', 'Allowance', required=False, readonly=True),
         'amount' :fields.float("Amount", digits_compute=dp.get_precision('Payroll'), required=True, readonly=True),
         'tax_deducted' :fields.float("Tax Deducted", digits_compute=dp.get_precision('Payroll'), readonly=True),
         'termination_id': fields.many2one('hr.employment.termination', 'Termination'),
         'account_id': fields.many2one('account.account', 'Account' , required=False),
         'type':fields.selection([('trm_allowance', 'Termination Allowance'), ('special', 'Special')], 'Type'),
    }
#----------------------------------------
#hr process(inherit)
#----------------------------------------
class hr_process_archive(osv.Model):
    """Inherits hr.process.archive and adds fields to be used  when adding a process record in the archive.
    """
    _inherit = "hr.process.archive"
    _columns = {
         'employee_salary_scale': fields.many2one('hr.salary.scale', "Employee Salary Scale", size=64,  required=True, states={'approved':[('readonly',True)]}),
         'reference': fields.reference('Event Ref', selection=[
                                  ('hr.salary.degree', 'Promotion'),
                                  ('hr.salary.bonuses', 'Annual Bonus'),
                                  ('hr.department', 'Department Transfer'),
                                  ('hr.job', 'Job Transfer')], size=128 , required=True, states={'approved':[('readonly',True)]}),
    }

    def onchange_employee(self, cr, uid, ids, emp_id,context={}):
        #employee_type domain
        emp_obj = self.pool.get('hr.employee')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        contractors = company_obj.process_contractors
        employee = company_obj.process_employee
        recruit = company_obj.process_recruit
        trainee = company_obj.process_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        employee_domain['employee_id'].append(('state', '=', 'approved'))
        domain = {'employee_id':employee_domain['employee_id']}
        return {'domain': domain,'value': {'previous': False , 'reference':False,'employee_salary_scale': False}}


    def _check_reference(self, cr, uid,ids,context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.state != 'approved':
                if record.reference._name == 'hr.salary.degree':
                    if record.reference.id == record.employee_id.degree_id.id:
                       raise orm.except_orm(_('Warning'), _("You can not choose the employee's current degree!")) 
                if record.reference._name  == 'hr.salary.bonuses':
                    if record.reference.id == record.employee_id.bonus_id.id:
                       raise orm.except_orm(_('Warning'), _("You can not choose the employee's current bonus!")) 
        return super(hr_process_archive, self)._check_reference(cr, uid,ids,context=context)

    _constraints = [
        (_check_reference, "You can not choose an employee's current job/department!", ['reference']),
    ]  

    def onchange_reference(self, cr, uid, ids, reference, employee_id, context=None):
        """Method that gives employee's  previous department, job, degree or bonus based on the reference.
           @param reference: Modeld to work with
           @param employee_id: Id of employee
           @return: dictionary of values
        """
        if context is None: context = {}
        res = {}
        employee_obj = self.pool.get('hr.employee')
        if reference and employee_id:
            (model_name, id) = reference.split(',')
            row = self.read(cr, uid, employee_id, context=context)
#             if not row :
#                 return res
            emp = employee_obj.browse(cr, uid, employee_id , context=context)
            if model_name == 'hr.department':
                res = {'value': {'previous': emp.department_id.name , 'employee_salary_scale': emp.payroll_id.id }}
            if model_name == 'hr.job':
                res = {'value': {'previous': emp.job_id.name , 'employee_salary_scale': emp.payroll_id.id }}
            if model_name == 'hr.salary.degree':
                res = {'value': {'previous': emp.degree_id.name , 'employee_salary_scale': emp.payroll_id.id }}
            if model_name == 'hr.salary.bonuses':
                res = {'value': {'previous': emp.bonus_id.name , 'employee_salary_scale': emp.payroll_id.id }}
            res['value'].update({'employee_id':employee_id})
        return res

    def create_new(self, cr, uid, ids, context=None):
        """Workflow function that changes the state to 'approved' and updates employee record degree or bonus based on the reference.
           @return: Boolean True
        """
        employee_obj = self.pool.get('hr.employee')
        super(hr_process_archive, self).create_new(cr, uid, ids, context=context)
        for row in self.read(cr, uid, ids, context=context):
            (model_name, id) = row['reference'].split(',')
            if model_name == 'hr.salary.degree':
                employee_obj.write(cr, uid, [row['employee_id'][0]], {'degree_id':id})
            if model_name == 'hr.salary.bonuses':
                employee_obj.write(cr, uid, [row['employee_id'][0]], {'bonus_id':id, 'bonus_date': row['approve_date']})
                #employee_obj.write(cr,uid,[row['employee_id'][0]],{'bonus_id':id})
        return self.write(cr, uid, ids, {'state':'approved'})

#----------------------------------------
#hr reemployment(inherit)
#----------------------------------------
class hr_employee_reemployment(osv.Model):
    """Inherits hr.employee.reemployment to define the new degree and bonus of the employee.
    """ 
    _inherit = "hr.employee.reemployment"
    _columns = {
        'degree_id' : fields.many2one('hr.salary.degree', 'Degree', states={'done':[('readonly',True)]}),
        'bonus_id' : fields.many2one('hr.salary.bonuses', 'Bouns', domain="[('degree_id','=',degree_id)]", states={'done':[('readonly',True)]}),
    }

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """Method that returns employee's bonus and degree.
           @param employee_id: Id of employee
           @return: Dictionary of values 
        """
        if context is None: context = {}
        res = super(hr_employee_reemployment, self).onchange_employee_id(cr, uid, ids, employee_id, context=context)
        emp = self.pool.get('hr.employee').browse(cr, uid, employee_id , context=context)
        res['value'].update({ 'degree_id': emp.degree_id.id, 'bonus_id':emp.bonus_id.id })
        return res

    def action_done(self, cr, uid, ids, context=None):
        """Method that changes the state to 'approve10'  and adds a new record to hr.process.archive 
           if the degree or the bonus of the employee have been changed during the re-employment process.
           @return: Boolean True
        """
        process_obj = self.pool.get('hr.process.archive')
        wf_service = netsvc.LocalService("workflow")
        for record in self.browse(cr, uid, ids):
            super(hr_employee_reemployment, self).action_done(cr, uid, [record.id], context=context)
            vals= {
                   'code':record.employee_id.code,
                   'employee_id':record.employee_id.id,
                   'date': record.reemployment_date ,
                   'approve_date': time.strftime('%Y-%m-%d') ,
                   'employee_salary_scale': record.employee_id.payroll_id.id, 
                   'company_id':record.company_id.id,
                   'comments':'Reemployement',
                   'associated_reemployment':record.id,
                   
            }
            
            if record.degree_id.id != record.employee_id.degree_id.id:
                vals.update({'reference':'hr.salary.degree' + ',' + str(record.degree_id.id),
                             'previous': record.employee_id.degree_id.name, })
                process_id = process_obj.create(cr, uid, vals, context=context)
                wf_service.trg_validate(uid, 'hr.employee.reemployment', process_id , 'approve10', cr)
            if record.bonus_id.id != record.employee_id.bonus_id.id:
                vals.update({'reference':'hr.salary.bonuses' + ',' + str(record.bonus_id.id),
                              'previous': record.employee_id.bonus_id.name })
                process_id = process_obj.create(cr, uid, vals, context=context)
                wf_service.trg_validate(uid, 'hr.employee.reemployment', process_id , 'approve10', cr)
        return True

#----------------------------------------
#delegation inherit
#----------------------------------------
class hr_employee_delegation(osv.osv):
    """Inherits hr.employee.delegation to define how to deal with the saraly of the employee during the delegation period.
    """
    _inherit = 'hr.employee.delegation'
    _columns = {
        'payroll_type':fields.selection([('paied', 'Paied'), ('unpaied', 'Unpaied'),
                                         ('customized', 'Customized')], 'Payroll', required=True,readonly=True, states={'draft':[('readonly',False)]}),
        'allow_deduct_ids' :fields.many2many('hr.allowance.deduction'  , 'del_allow_deduct_rel'  , 'delegation_id' ,
                                            'allow_deduct_id' , "Allowances/Desductions" ,
                                             domain="[('in_salary_sheet','=',True),('special','=',False)]" ,readonly=True, states={'draft':[('readonly',False)]}),
        'salary_included' : fields.boolean('Basic Salary Included',readonly=True, states={'draft':[('readonly',False)]}),
    }

#----------------------------------------
#employee category(inherit) 
#----------------------------------------
class hr_employee_category(osv.Model):

    _inherit = "hr.employee.category"
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """
        Method that overwrites name_search method Search for employee (only employees 
        that requested trainings) and their display name.

        @param name: Object name to search
        @param args: List of tuples specifying search criteria
        @param operator: Operator for search criterion
        @param limit: Max number of records to return
        @return: Super name_search method 
        """
        if not context : context = {}
        if 'allow_cat_ids' in context:
            cat_ids = [i[2]['cat_id'] for i in context['allow_cat_ids']]
            if cat_ids : args.append(('id', 'not in',cat_ids))
        return super(hr_employee_category, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

    _columns = {
        'salary_batch' : fields.boolean('Salary Batch', ),
        'responsible_id' : fields.many2one('hr.employee', "Responsible Officer"  ),
        'active' : fields.boolean('Active'),
    }

    _defaults = {
        'active' : 1,
                }

    def _check_employee(self, cr, uid, ids, context=None):
        for rec in self.browse(cr ,uid, ids):
            if rec.salary_batch and rec.active and rec.employee_ids :
                emp_name = '' 
                for emp in rec.employee_ids:
                    if self.search(cr, uid,[('salary_batch','=',True),('active','=',True),('id','!=',rec.id),('employee_ids','in',(emp.id))]):
                        emp_name+=emp.name+ '\n'
                if emp_name :
                    raise osv.except_osv(_('Warning!'), 
                                        _('Sorry employees %s are existed in another batches to add them here remove them from old batches !')
                                             %emp_name )
        return True

    _constraints = [
        (_check_employee, 'Error! You cannot add same employee to more than one active salary batch ', ['employee_ids'])
    ]



