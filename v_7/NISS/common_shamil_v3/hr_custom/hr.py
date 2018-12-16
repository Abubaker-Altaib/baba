# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
import re
#----------------------------------------
#employee category(inherit) 
#----------------------------------------
class hr_employee_category(osv.Model):

    _inherit = "hr.employee.category"

    _columns = {
        'code': fields.char('Code', size=64),
    }

    _sql_constraints = [
       ('name_uniqe', 'unique (code)', 'you can not create same code !')
    ]
    
    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.employee_ids:
                raise osv.except_osv(_('Warning!'),_('You cannot delete this tag there is an employee assign to it ')%(rec.employee_ids))
        return super(hr_employee_category, self).unlink(cr, uid, ids, context)

#----------------------------------------
# Employee (Inherit) 
# Adding new fields & update workflow
#----------------------------------------
class hr_employee(osv.Model):

    _inherit = "hr.employee"

    _order = "sequence"


    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = self.search(cr, user, [('emp_code', operator, name)]+ args, limit=limit, context=context)
        ids += self.search(cr, user, [('name_related', operator, name)]+ args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        """Append the employee code to the name"""
        if not ids:
            return []
        if type( ids ) is not list:
            ids = [ids]
        res = [ (r['id'], r['name_related'] and '%s' % (r['name_related']) )
                for r in self.read(cr, uid, ids, ['name_related', 'emp_code'],
                                   context=context) ]
        return res

    def _get_type(self, cr, uid,context=None):
        """Determine the employee's type"""
        employee_type = 'employee'
        if context:
            if context.has_key('employee_type'): employee_type = context['employee_type']
        return employee_type

    def onchange_department_id(self, cr, uid, ids, department_id, context=None):
        value = {'parent_id': False}
        if department_id:
            department = self.pool.get('hr.department').browse(cr, uid, department_id)
            value['parent_id'] = department.manager_id.id
        return {'value': value}

    def get_emp_analytic(self, cr, uid, employees,  dic, date=time.strftime('%Y-%m-%d'), context={}):
	analytic_obj = self.pool.get('hr.employee.analytic')
	year = int(time.strftime('%Y'))
	month = int(time.strftime('%m'))
	analytic = False
	lines = {}
	length = len(employees)
	print employees
	for e in employees:
	   emp_ids = analytic_obj.search(cr,uid, [('employee_id','=',e.id),('year','=',year),('month','=',month)] )
	   re = analytic_obj.read(cr, uid, emp_ids, ['analytic_account_id','percentage'])
           for x in re:
              analytic_id = x['analytic_account_id'][0]
              if lines.get(analytic_id,False) and lines[analytic_id]:
                   lines[analytic_id].update({
                     'amount':lines[analytic_id]['amount']+(employees[e] * x['percentage']/100) ,
                })
              else:
		   lines[analytic_id] = dic.copy()
                   lines[analytic_id].update({
                       'account_analytic_id':analytic_id,
                        'amount': (employees[e] * x['percentage']/100) ,
                       }) 

	   if not emp_ids:
	        analytic = e.department_id.analytic_account_id and e.department_id.analytic_account_id.id 
	        if not analytic:
	             raise osv.except_osv(_('Warning!'),\
				_('Please Set an analytic account for this employee %s department.') % (e.name) )
		lines[analytic] = dic.copy()
                lines[analytic].update({
                       'account_analytic_id':analytic,
                        'amount': employees[e]  ,
                       }) 
	return lines.values()



    _columns = {
        'religion': fields.selection([('muslim', 'Muslim'), ('christian', 'Christian'), ('others', 'Others')], 'Religion', readonly=True, states={'draft':[('readonly', False)]}),
        'state':fields.selection([
                     ('draft', 'Draft'),
                     ('experiment', 'In Experiment'),
                     ('approved', 'In Service'),
                     ('refuse', 'Out of Service')] , "State", readonly=True),
        'emp_code' :fields.char("Employee Code", size=10, required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'sequence' :fields.char("Sequence" , readonly=True),
        'employment_date' : fields.date('Start Date', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        're_employment_date' : fields.date('RE-Employment Date', readonly=True),
        'first_employement_date':fields.date("First Employement Date", readonly=True, states={'draft':[('readonly', False)]}),
        'birth_place':fields.char("Birth Place", size=40, readonly=True, states={'draft':[('readonly', False)]}),
        'birthday_certificate_id':fields.char('Birthday Certificate Number', size=32 , readonly=True, states={'draft':[('readonly', False)]}),
        'participate_date' : fields.date('Social Insurance Date', readonly=True, states={'draft':[('readonly', False)]}),
        'nationality_no':fields.char("Nationality No", size=40, readonly=True, states={'draft':[('readonly', False)]}),
        'nationality_date' : fields.date('Nationality Export Date', readonly=True, states={'draft':[('readonly', False)]}),
        'emergency_data':fields.char("Emergency Phone/Address ", size=30, readonly=True, states={'draft':[('readonly', False)]}),
        'blood_type' :fields.selection([('1', 'O+'), ('2', 'O-'), ('3', 'A+'), ('4', 'A-'), ('5', 'B+'), ('6', 'B-'), ('7', 'AB+'), ('8', 'AB-')],
                                            'Blood Type', readonly=True, states={'draft':[('readonly', False)]}),
        'house_type' :fields.selection([('1', 'Government'), ('2', 'Housing ownership'), ('3', 'Rent'), ('4', 'maze'),
                                            ('5', 'Corperation Housing'), ('6', 'Random'), ('7', 'Others'), ], 'House Type',
                                            readonly=False),
        'file_no' :fields.char("File No", size=15, readonly=True, states={'draft':[('readonly', False)]}),
        'job_letter_no':fields.char("Job Letter No", size=15, readonly=True, states={'draft':[('readonly', False)]}),
        'job_letter_date':fields.date("Job Letter Date", size=8, readonly=True, states={'draft':[('readonly', False)]}),
        'nation_ser_date':fields.date("National Service Date", size=8, readonly=True, states={'draft':[('readonly', False)]}),
        'nation_srevice':fields.boolean('National Service', readonly=True, states={'draft':[('readonly', False)]}),
        'tax_exempted' : fields.boolean('Tax Exempted', readonly=True, states={'draft':[('readonly', False)]}),
        'tax':fields.float("Tax", digits=(18, 2), readonly=True, states={'draft':[('readonly', False)]}),
        'first_month' : fields.boolean('First Month', readonly=True),
        'join_date':fields.date("Join Date", size=8 , readonly=True, states={'draft':[('readonly', False)]}),
        'qualification_ids':fields.one2many('hr.employee.qualification', 'employee_id', "Qualifications", readonly=True),
        'relation_ids':fields.one2many('hr.employee.family', 'employee_id', "Relations", readonly=True),
        'analytic_ids':fields.one2many('hr.employee.analytic', 'employee_id', "Analytic" ),
        'employee_type': fields.selection([('employee', 'Employee'), ('trainee', 'Trainee'),
                                                ('contractor', 'Contractor'), ('recruit', 'Recruit')], 'Employee Type'),
        'end_date' : fields.date('End Date'),
        'period':fields.integer('Experiment Period', requierd=True, domain="[('state','in',('experiment')]"),
        'delegation' : fields.boolean('Delegation', readonly=True),
        'department_id':fields.many2one('hr.department', 'Department',ondelete="restrict"),
        'dept_parent_id': fields.related('department_id', 'parent_id', type='many2one', relation='hr.department', string='Parent Department', readonly=True),

    }

    _defaults = {
        'religion' : 'muslim',
        'state': 'draft',
        'sequence': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hr.employee'),
        'first_month' : 1,
        'employee_type': _get_type
    }

    def _check_dates(self, cr, uid, ids):
        for employee in self.browse(cr, uid, ids):
            message= "The %s must be anterior or equal to the current date!"
            if employee.birthday > time.strftime('%Y-%m-%d'):
               raise osv.except_osv(_('ERROR'), _(message %'birth date'))
            if employee.employment_date > time.strftime('%Y-%m-%d'):
               raise osv.except_osv(_('ERROR'), _(message %'employment date'))
            if employee.first_employement_date:
               if employee.first_employement_date > time.strftime('%Y-%m-%d'):
                  raise osv.except_osv(_('ERROR'), _(message %'first employment date'))
               if employee.first_employement_date > employee.employment_date:
                  raise osv.except_osv(_('ERROR'), _('first employment date must be anterior or equal to the employment date!'))
            if employee.end_date:
               if employee.end_date < employee.employment_date:
                  raise osv.except_osv(_('ERROR'), _('end date must be After the start date!'))
        return True


    def check_no_of_emp(self, cr, uid, ids, context=None):
        """ 
    Constrain method to check if there is an available job for the employee

        @return: boolean True or False
        """
        #for employee in self.browse(cr, uid, ids, context=context):
        #    if employee.job_id:
        #        employee_no = self.search(cr, uid, [('job_id', '=', employee.job_id.id), ('state', '!=', 'refuse'),('employee_type', 'in', ('employee','contractor'))], context=context)
        #        if employee.job_id.no_of_recruitment < 1 or len(employee_no) > employee.job_id.no_of_recruitment :
        #            raise osv.except_osv(_('ERROR'), _('sorry you can not exceed the Max Number of exepected employees!'))
        #        elif employee.job_id.deparment_ids and employee.department_id.id not in [dep.department_id.id for dep in employee.job_id.deparment_ids]:
        #            raise osv.except_osv(_('ERROR'), _('sorry you can not exceed the Max Number of exepected employees!'))
        #        elif employee.job_id.deparment_ids and employee.department_id.id  in [dep.department_id.id for dep in employee.job_id.deparment_ids]:
        #           dom = [('job', '=', employee.job_id.id), ('department_id', '=', employee.department_id.id)]
        #            job_dep = self.pool.get('department.jobs').search(cr, uid, dom, context=context)
        #            domain = [('job_id', '=', employee.job_id.id), ('id', '!=', employee.id), ('department_id', '=', employee.department_id.id), ('state', 'in', ('approved',))]
        #           if self.pool.get('department.jobs').browse(cr, uid, job_dep)[0].no_emp < 1 or len(self.search(cr, uid, domain, context=context)) >= self.pool.get('department.jobs').browse(cr, uid, job_dep)[0].no_emp:
        #               raise osv.except_osv(_('ERROR'), _('sorry you can not exceed the Max Number of exepected employees!'))
        return True

    _constraints = [
         (check_no_of_emp, _('sorry you can not exceed the Max Number of exepected employees'), ['expected_employees']),
         (_check_dates, _('The birth date must be anterior to the current date!'), ['birthday']),
    ]
    _sql_constraints = [
        ('Experiment Period_check', "CHECK ( period >= 0 )", "The number of Experiment Period must be greater than or equal Zero."),
        ('code_uniqe', 'unique (emp_code)', ' You can not duplicate the code!'),
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        employee = self.browse(cr, uid, id, context=context)
        default.update({'emp_code':employee.emp_code+"(copy)"})
        return super(hr_employee, self).copy(cr, uid, id, default, context=context)
    
    def create(self, cr, uid, vals, context=None):
	"""
        Override create method to create a new user for the employee

	@return: super create method
	"""
        user_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        user_id = user_obj.create(cr, uid,{
            'name': vals['name'],
            'login': vals.get('emp_code') or vals['name'][:4],
            'password': vals.get('emp_code'),
            #'context_department_id': vals['department_id'] or vals['name'][:4],
            'company_ids': [(6, 0, [vals['company_id']])],
            'company_id': vals['company_id']
        }, context=context)
        partner_id = user_obj.browse(cr, uid, user_id, context=context).partner_id.id
        partner_obj.write(cr, uid, [partner_id], {'employee': 1}, context=context)
        vals['user_id']= user_id
        return super(hr_employee, self).create(cr, uid, vals, context=context)

    def experiment(self, cr, uid, ids, context=None):
        """
	Method to change employee state to experiment.
        """
        return self.write(cr, uid, ids, {'state': 'experiment'}, context=context)

    def approve(self, cr, uid, ids, context=None):
        """Adding employee the olld name of this function was create_archive.
        @return: True 
        """
        '''end_service_archive_obj = self.pool.get('hr2.basic.employee.dismissal')
       reemployment_archive_obj = self.pool.get('hr2.basic.reemployment.archive')
       for employee in self.browse(cr, uid, ids, context=context):
          emp_archive_dict = {
            'employee_id':employee.id,
            'company_id':employee.company_id.id,
             }
          check_end_service = end_service_archive_obj.search(cr, uid, [('employee_id', '=', employee.id)], context=context)
          check_reemployment = reemployment_archive_obj.search(cr, uid, [('employee_id', '=', employee.id)], context=context)
          if check_end_service:
             if check_reemployment:
                employee_end_service = end_service_archive_obj.browse(cr, uid, check_end_service, context=context)[0]
                employeee_reemployment = reemployment_archive_obj.browse(cr, uid, check_reemployment, context=context)[0]
                if employeee_reemployment.reemployment_date <= employee_end_service.dismissal_date:
                   raise osv.except_osv(_('ERROR'), _("Can't return this employee back to in service, end of service date is after the re-employment date "))
             else:
                raise osv.except_osv(_('ERROR'), _("Can't return This employee back to in service, re-employment the employee first"))                
          '''
        return self.write(cr, uid, ids, {'state':'approved'}, context=context)

    def refuse(self, cr, uid, ids, context=None):
        """ 
	Method to change employee state to refuse.
        """
        return self.write(cr, uid, ids, {'state': 'refuse'}, context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        """
	Method to change employee state to draft.	
        """
        return self.write(cr, uid, ids, {'state': 'draft', }, context=context)

    def _get_default_employee_domain(self, cr, uid, ids, contractors, employee, recruit, trainee, context=None):
        """
	Mehtod That gets the types(domain) of employee 

        @return: dictionary of value
        """
        types = []
        if contractors: types.append('contractor')
        if employee: types.append('employee')
        if recruit: types.append('recruit')
        if trainee: types.append('trainee')
        domain = {'employee_id':[('employee_type', 'in', types)]}
        return domain


#----------------------------------------
#qualification specification
#----------------------------------------
class hr_specifications(osv.Model):
    _name = "hr.specifications"
    _description = "specifications"
    _columns = {
        'name': fields.char('Specification Name', size=64, required=True),
        'code': fields.char("Specificatlenion Code", size=64, required=True),
        'active': fields.boolean('Active', select=True),
    }
    _defaults = {
        'active':lambda *a:1,
    }
    _sql_constraints = [

       ('code_uniqe', 'unique (code)', 'you can not create same code !'),
       ('name_uniqe', 'unique (name)', 'Specification name is already exist !'),
    ]

class qualification(osv.Model):
    _name = "hr.qualification"
    _description = "qualifications"
    _columns = {
        'name' : fields.char("Qualification Title", size=50, required=True),
        'amount':fields.integer('Amount', requierd=True),
        'order':fields.integer('Order', requierd=True),
        'active' : fields.boolean('Active'),
        'code': fields.char('Code', size=64),
        'type': fields.selection([('view', 'view'), ('normal', 'Normal')], 'Type'),
        'parent_id': fields.many2one('hr.qualification', 'Qualification Parent'),
    }
    _defaults = {
        'active' : lambda *a: 1,
   }
    _sql_constraints = [

       ('code_uniqe', 'unique (code)', 'you can not create same code !'),
       ('name_uniqe', 'unique (name)', 'Qualification name is already exist !'),
    ]
    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        qual = self.browse(cr, uid, id, context=context)
        default.update({'name':qual.name+"(copy)" , 'code':False})
        return super(qualification, self).copy(cr, uid, id, default, context=context)


class hr_employee_qualification(osv.Model):

    _name = "hr.employee.qualification"
    _description = "employee's qualifications"
    _columns = {

        'employee_id' : fields.many2one('hr.employee', "Employee", required=True , readonly=True, states={'draft':[('readonly', False)]}),
        'emp_qual_id' : fields.many2one('hr.qualification', 'Qualification' , ondelete="restrict" , readonly=True, states={'draft':[('readonly', False)]}),
        'qual_date' :fields.date("Qualification Date" , readonly=True, states={'draft':[('readonly', False)]}),
        'organization' : fields.char("Organization", size=100, required=False , readonly=True, states={'draft':[('readonly', False)]}),
        'comments': fields.text("Comments"),
        'specialization': fields.many2one('hr.specifications' , 'Specialization' , readonly=True, states={'draft':[('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'), ('approved', 'Approved'),
                                  ('rejected', 'Rejected'), ], 'State', readonly=True),
    }
    _defaults = {
        'state': 'draft',
    }

    _sql_constraints = [

       ('qualification_uniqe', 'unique (employee_id,emp_qual_id)', 'The qualification already exist for this employee !'),
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        default.update({'emp_qual_id':False})
        return super(hr_employee_qualification, self).copy(cr, uid, id, default, context=context)

    def approve_quali(self, cr, uid, ids, context=None):
        """
	Add qualification to the employee, change the state to approved
        """
        return self.write(cr, uid, ids, { 'state' : 'approved' }, context=context)

    def reject_quali(self, cr, uid, ids, context=None):
        """
	Reject the qualification of the employee, change state to rejected
        """
        return self.write(cr, uid, ids, { 'state' : 'rejected' }, context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        """
	Method to reset the workflow of the employee and change state to draft.
        """
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.qualification', id, cr)
            wf_service.trg_create(uid, 'hr.employee.qualification', id, cr)
        return self.write(cr, uid, ids, {'state': 'draft' }, context=context)

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete an employee qualification which is in %s state.')%(rec.state))
        return super(hr_employee_qualification, self).unlink(cr, uid, ids, context)


#----------------------------------------
#employee family configuration
#----------------------------------------
class hr_family_relation(osv.Model):

    _name = "hr.family.relation"
    _description = "relatives settings"
    _columns = {
        'name' : fields.char("Relation Name", size=50, required=True),
        'max_age' : fields.integer("Max Age For Ensuring", required=True),
        'max_number' : fields.integer("Max No For Ensuring", required=True),
        'amount' : fields.integer("Amount", required=False),
        'active' : fields.boolean('Active'),
        'code': fields.char('Code', size=64),
    }

    _defaults = {
        'active' : 1,
    }

    _sql_constraints = [
        ('code_uniqe', 'unique (code)', 'you can not create same code !'),
        ('name_uniqe', 'unique (name)', 'Relation name already exist!')
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        relation = self.browse(cr, uid, id, context=context)
        default.update({'name':relation.name+"(copy)"})
        return super(hr_family_relation, self).copy(cr, uid, id, default, context=context)

#----------------------------------------
#employee family relation 
#----------------------------------------
class employee_family(osv.Model):

    _name = "hr.employee.family"
    _description = "employee's family members"
    _columns = {
         'employee_id': fields.many2one('hr.employee', "Employee", required=True, domain=[('marital', '!=', 'single'),('state', '=', 'approved')]) ,
         'relation_id': fields.many2one('hr.family.relation', "Relation Type", required=True ,ondelete="restrict"),
         'relation_name': fields.char("Relation Name", size=500 , required=True),
         'birth_date' :fields.date("Birth Date", required=True),
         'start_date' :fields.date("Start Date", required=True),
         'end_date' :fields.date("End Date"),
         'app_date' :fields.date("Approved Date", size=8),
         'comments': fields.text("Comments", size=100),
         'state': fields.selection([('draft', 'Draft'), ('approved', 'Approved'),
                   ('approvewfees', 'Approvedd with fees'),
                   ('rejectedwfees', 'Rejected with fees'),
                   ('rejected', 'Rejected'), ('stopped', 'Stopped'), ], 'State', readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }

    _sql_constraints = [
       ('name_uniqe', 'unique (employee_id,relation_id,relation_name)', 'This relation name is already exist for selected employee !'),
    ]

    def _check_dates(self, cr, uid, ids):
        for relation in self.browse(cr, uid, ids):
            if relation.birth_date > time.strftime('%Y-%m-%d'):
               raise osv.except_osv(_('ERROR'), _('The birth date must be anterior or equal to the current date!'))
            if relation.start_date < relation.birth_date:
                  raise osv.except_osv(_('ERROR'), _('The start date must be After or equal to the birth date!'))
            if relation.end_date:
               if relation.end_date < relation.start_date:
                  raise osv.except_osv(_('ERROR'), _('The end date must be After the start date!'))
        return True

    _constraints = [
         (_check_dates, 'The end date must be After the start date!', ['start_date']),
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Warning!'), _('You Cannot Duplicate Employee Relation !'))
        return super(employee_family, self).copy(cr, uid, id, default=default, context=context)


    def unlink(self, cr, uid, ids, context={}):
        """
	Override unlink method to call employee write method when deleting 
	family relation record in order to update salary.
        """
	#TODO: write list of employee ID intead of one ID (append IDs)
        employee_obj = self.pool.get('hr.employee')
        for relation in self.browse(cr, uid, ids, context=context):
            if relation.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete an employee relation which in %s state.')%(relation.state))
        return super(employee_family, self).unlink(cr, uid, ids, context=context)

    def mymod_approved(self, cr, uid, ids, context={}):
        """
	Add employee family record, change state to approved and set current date 
	as start date of family relation, which affect salary.
        """
        vals = { 'state' : 'approved' }
        for relation in self.browse(cr, uid, ids, context=context):
            if not relation.start_date:
                vals['start_date'] = time.strftime('%Y-%m-%d')
        self.write(cr, uid, ids, vals, context=context)
        return True

    def mymod_stopped(self, cr, uid, ids, context={}):
        """
	Stop employee family record, change state to stopped

        @return :True
        """
        vals = { 'state' : 'stopped' }
        for relation in self.browse(cr, uid, ids, context=context):
            if not relation.end_date:
                vals['end_date'] = time.strftime('%Y-%m-%d')
        self.write(cr, uid, ids, vals, context=context)
        return True

    def set_to_draft(self, cr, uid, ids, context={}):
        """
	Method to reset the workflow of the employee and change state to draft.

        @return: boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft' }, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.family', id, cr)
            wf_service.trg_create(uid, 'hr.employee.family', id, cr)
        return True

#----------------------------------------
#hr job(inherit)
#----------------------------------------
class hr_job(osv.Model):
   
    '''def check_no_of_emp(self, cr, uid, ids, context=None):
        for job in self.browse(cr, uid, ids, context=context):
            if job.no_of_employee > job.recruitment:
                return False
        return True'''


    def _no_of_employee(self, cr, uid, ids, name, args, context=None):
        """
	Method to set the numer of employees occupying the job and the free available positions.
	
	@return: dictionary of fields value to be updated
        """
        res = {}
        for job in self.browse(cr, uid, ids, context=context):
            nb_employees = len([e.id for e in job.employee_ids if e.state != 'refuse' and e.employee_type in('employee','contractor')])
            if job.no_of_recruitment != 0.0 :
                job.no_of_recruitment = job.no_of_recruitment - nb_employees
            res[job.id] = {
                'no_of_employee': nb_employees,
                'expected_employees': job.no_of_recruitment,
                          }
        return res

    def _get_job_position(self, cr, uid, ids, context=None):
        """
	Count the numer of employees in the job

	@return: list of employee IDs
        """
        res = []
        for employee in self.pool.get('hr.employee').browse(cr, uid, ids, context=context):
            if employee.job_id and employee.state != 'refuse':
                res.append(employee.job_id.id)
        return res

    _inherit = "hr.job"
    _columns = {
        'expected_employees': fields.function(_no_of_employee, string='Available position', store=True,
            #store={
            #    'hr.job': (lambda self, cr, uid, ids, c=None: ids, ['no_of_recruitment'], 10),
            #    'hr.employee': (_get_job_position, ['job_id','state'], 10),
             #},
              help='Free position of this job position after new recruitment.', multi='no_of_employee'),
                'no_of_employee': fields.function(_no_of_employee, string="Current Number of Employees", store=True,
            #store={
             #   'hr.employee': (_get_job_position, ['job_id','state'], 10),
             #}, 
             help='Number of employees currently occupying this job position.', multi='no_of_employee'),

        'code': fields.char('Code', size=64),
        'deparment_ids':fields.one2many('department.jobs', 'job', 'Basic job'),
        'type': fields.selection([('view', 'view'), ('normal', 'Normal')], 'Job Type' , required=True),
        'parent_id': fields.many2one('hr.job', 'Parent', ondelete='cascade', domain=[('type', '=', 'view')]),
               }

    def unlink(self, cr, uid, ids, context=None):
        for e in self.browse(cr, uid, ids):
            parent = self.search(cr, uid, [('parent_id', '=',e.id)])
            if  parent:
                raise osv.except_osv(_('Warning!'), _('You cannot delete this job because it has child !'))
            if e. employee_ids:
                raise osv.except_osv(_('Warning!'), _('You cannot delete this job ,there is an employee belong to it !'))
        return super(osv.osv, self).unlink(cr, uid, ids, context)
    
#----------------------------------------
#department_jobs
#----------------------------------------

class department_jobs(osv.Model):

    def check_no_of_job(self, cr, uid, ids, context={}):
        """
	Constrain method to check if there is an available job positions in the department.
        """
        for dep in self.browse(cr, uid, ids, context=context):
            if not dep.job.no_of_recruitment:
                return False
            if dep.no_emp > 0 and dep.job.no_of_recruitment:
                dep_job_ids = self.search(cr, uid, [('job', '=', dep.job.id), ('id', '!=', dep.id)], context=context)
                if dep_job_ids:
                    sums = sum([x.no_emp for x in self.browse(cr, uid, dep_job_ids)])
                    if sums >= dep.job.no_of_recruitment:
                        return False
                    elif sums < dep.job.no_of_recruitment and dep.no_emp > dep.job.no_of_recruitment - sums:
                        return False
                elif  dep.no_emp > dep.job.no_of_recruitment:
                    return False
            return True

    _name = "department.jobs"
    _description = "specified job for the department"
    _columns = {

        'department_id':fields.many2one("hr.department", "Department", required=True),
        'job':fields.many2one("hr.job", "Job", ondelete='cascade', required=True),
        'no_emp':fields.integer("No of Employees"),
    }
    _constraints = [
        (check_no_of_job, 'Sorry you can not exceed the maximum limit of this job', ['no_emp']),
    ]

    _sql_constraints = [

       ('no_emp_check', 'CHECK (no_emp >= 0)', "The number of Employees should be greater than or equal one !"),
                 ] 
#----------------------------------------
#department category
#----------------------------------------
class hr_department_cat(osv.Model):

    _name = 'hr.department.cat'
    _description = "department category"
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char('Department Category Name', size=64, required=True),
   }

    _sql_constraints = [
        ('code_uniqe', 'unique (code)', 'you can not create same code !'),
        ('name_uniqe', 'unique (name)','Category name must be unique!')
    ]


#----------------------------------------
#department(inherit) 
#----------------------------------------
class hr_department(osv.Model):

    _inherit = 'hr.department'

    _columns = {
        'employee_ids': fields.one2many('hr.employee', 'department_id', 'Employees', readonly=True, domain=[('state', '=', 'approved')]),
        'cat_id':fields.many2one('hr.department.cat', 'Department Category Name', select=True,ondelete="restrict"),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
    }

    _sql_constraints = [
        ('name_uniqe', 'unique (name,parent_id)','Department name must be unique!')
    ]

#----------------------------------------
#Hr dismissal
#----------------------------------------
class hr_dismissal(osv.Model):

    _name = "hr.dismissal"
    _description = "dismissal type"
    _columns = {
        'name':fields.char("Termination Cause", size=50 , required=True),
        'active' : fields.boolean('active'),
        'code': fields.char('Code', size=64),
        'reemployment' : fields.boolean('Reemployment', help='IF True, Employee can reemployment'),
        'period': fields.integer('Period', required=True, help='Less time allowed to reemployment.'),
   }

    _defaults = {
        'active' : 1,
        'period' : 0,
        'reemployment': 1,
    }

    _sql_constraints = [

        ('code_uniqe', 'unique (code)', 'you can not create same code !'),
        
    ]
    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        name = self.read(cr, uid, [id], ['name'], context)[0]['name']
        default.update({'name': _('%s (copy)') % name})
        data = self.copy_data(cr, uid, id, default, context)
        new_id = self.create(cr, uid, data, context)
        self.copy_translations(cr, uid,  new_id, new_id, context)
        return new_id    

#----------------------------------------
#employment termination
#----------------------------------------
class hr_employment_termination(osv.Model):

    _name = "hr.employment.termination"
    _description = "employee termination"
    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", domain="[('state','not in',('draft','refuse'))]", required=True ,readonly= True , states={'draft':[('readonly', False)]}),
        'dismissal_date' :fields.date("Termination Date", size=8, required=True ,readonly= True, states={'draft':[('readonly', False)]}),
        'dismissal_type' : fields.many2one('hr.dismissal', 'Termination Reason', required=True,readonly= True, states={'draft':[('readonly', False)]}),
        'comments': fields.text("Comments" ,readonly=True ,states={'draft':[('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'), ('refuse', 'Out Of Service'), ], 'State', readonly=True ,states={'draft':[('readonly', False)]}),
    }

    _defaults = {
        'state' : 'draft',
    }


    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Warning!'), _('You Cannot Duplicate Employee Termination !'))
        return True
    
    def termination(self, cr, uid, ids, context=None):
        """ 
	Terminate employee service and change state to refuse
        """
        wf_service = netsvc.LocalService("workflow")
	for emp in self.browse(cr, uid, ids, context=context):
	    wf_service.trg_validate(uid, 'hr.employee', emp.employee_id.id , 'refuse', cr)
	return  self.write(cr, uid, ids, { 'state' : 'refuse' }, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """ 
        function to prevent deletion of employee termination 
        record which is not in draft state  
        """
        for rec in self.browse(cr, uid, ids):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete Record Which Is Not In Draft State !'))
        return super(hr_employment_termination, self).unlink(cr, uid, ids, context)   


class employee_analytic(osv.Model):

    _name = "hr.employee.analytic"
    _description = "employee's analytic"
    _columns = {
         'employee_id': fields.many2one('hr.employee', "Employee", required=True) ,
         'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', required = True),
         'percentage' :fields.float("Percentage", required=True),
         'month' :fields.selection([('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),
                                   ('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12')], "Month", required = True),
         'year' :fields.integer("Year", required = True),
    }
    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
    }




    '''def check_percentage(self, cr, uid, ids, context={}):
        """Method that checks if the enterd persentage is less than zero it raise .
           @return: Boolean True or False
        """
        for rec in self.browse(cr, uid, ids):
            if rec.sub_prcnt_selection and rec.sub_prcnt_selection in ('percentge','bigest','smalest' ) and rec.sub_percentage <= 0:
                return False
        return True'''

    _sql_constraints = [
        ('Percentage check', "CHECK (  100 >= percentage >= 0 )", "The percentage should be between 0-100."),
    ]


