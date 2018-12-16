# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from tools.translate import _
import time
import netsvc
from datetime import datetime
from openerp.osv import fields,osv, orm
from openerp.tools.translate import _
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations

#----------------------------------------
#promotion types
#----------------------------------------
class hr_promotion_type(osv.osv):
    _name = "hr.promotion.type"
    _description = "promotion type"
    _columns = {
        'name': fields.char('Promotion Name',size=256, required=True ),
        'code': fields.char('Promotion Code',size=256 , select=True),
    } 

#----------------------------------------
# Hr Process Archive
#----------------------------------------
class hr_process_archive(osv.osv):
    _name = "hr.process.archive"
    _description = "employee's process archive"
    _columns = {
        'name': fields.char("Code", size=64 , states={'approved':[('readonly',True)]}),
        'state':fields.selection([ ('draft','Draft'),('approved','Approved'),] ,'Status' ,select=True, readonly=True),                                       
        'previous': fields.char('Previous', size=64,readonly=False),
        'reference': fields.reference('Event Ref', selection=[
                                 ('hr.department', 'Department Transfer'),
                                 ('hr.job', 'Job Transfer')],size=128 ,required=True , states={'approved':[('readonly',True)]}),       
        'date' :fields.date("Date", size=8 , states={'approved':[('readonly',True)]}),      
        'approve_date' :fields.date("Approve Date", size=8  , select=True , states={'approved':[('readonly',True)]}), 
        'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=False ,select=True , change_default=True , states={'approved':[('readonly',True)]}), 
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=False, states={'approved':[('readonly',True)]}),
        'promotion_type': fields.many2one('hr.promotion.type', "Promotion Type" , states={'approved':[('readonly',True)]}),
        'comments': fields.text("Comments", readonly=False ),    
        'code': fields.char("Code", size=64 , readonly=False, states={'approved':[('readonly',True)]} ),
        'days': fields.char('days', size=64, readonly=False , states={'approved':[('readonly',True)]}),
        'associated_id': fields.many2one('hr.process.archive', 'Associated', select=True, ondelete='cascade' , states={'approved':[('readonly',True)]}), 
        'associated_reemployment': fields.many2one("hr.employee.reemployment", 'Reemployment' , states={'approved':[('readonly',True)]}),
        'associated_ids':fields.one2many('hr.process.archive', 'associated_id' , 'Associated' , states={'approved':[('readonly',True)]}), 
    }
    _defaults = {
		'state': 'draft',
		'reference': lambda *a: False,                 
		'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
		'employee_id': lambda *a: False,
    }  

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Warning!'),_('You Can Not Have Two Employee Processes Records with the same "Event Ref","Approved Date","Employee" and "Date" !"  '))
    
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
        if emp_id:
           employee = emp_obj.browse(cr, uid, emp_id)
           domain['reference']=['|',('reference', '!=', 'hr.department,' + str(employee.department_id.id)),('reference', '!=', 'hr.job,' + str(employee.job_id.id))]

        return {'domain': domain,'value': {'previous': False ,'reference':False }}

    def onchange_reference(self, cr, uid, ids, reference, employee_id, context=None):
        """
	Onchange reference method to set the previous job of the employee or its previous 
	detartment based on the selected reference.
	
	@return: dictionary of fields value to be updated
	"""
        if context is None: context = {}
        res = {}
        employee_obj = self.pool.get('hr.employee') 
        if reference and employee_id:
            (model_name, id) = reference.split(',')   
            row =  self.read(cr, uid, id, context=context)
            if not row :
                return res       
            emp = employee_obj.browse(cr, uid, employee_id , context=context)
            if model_name  == 'hr.department': 
                res = {'value': {'previous': emp.department_id.name}}                              
            if model_name == 'hr.job':    
                res = {'value': {'previous': emp.job_id.name}} 
            res['value'].update({'employee_id':employee_id})                
        return res
    
    def create_new(self, cr, uid, ids,context=None):
        """
	Workflow function change record state to 'approved' and updates employee's record as fellow:
            changes employee's job and writes the date of changing if the refrence is hr.job or 
            changes employee's department if the refrence is hr.department
        @return: boolean True 
        """

        employee_obj = self.pool.get('hr.employee')  
        for row in self.read(cr, uid, ids, context=context):
            (model_name, id) = row['reference'].split(',')
            if model_name  == 'hr.department':
                employee_obj.write(cr,uid,[row['employee_id'][0]],{'department_id': id })
            if model_name == 'hr.job':    
                employee_obj.write(cr,uid,[row['employee_id'][0]],{'job_id': id,'join_date': row['approve_date'] })                
            #search for all the children and all consolidated children (recursively) of the given process ids    
            ids2 = self.search(cr, uid, [('associated_id', 'child_of', ids)], context=context)
            ids3 = []  
            for rec in self.browse(cr, uid, ids2, context=context):
                for child in rec.associated_ids:
                    ids3.append(child.id)
            if ids3:
                ids3 = self.create_new(cr, uid, ids3, context) 

        return self.write(cr, uid, ids, {'state':'approved'}) 

    def _check_reference(self, cr, uid,ids,context=None):

        for record in self.browse(cr, uid, ids, context=context):
        	if record.state != 'approved':
		    if record.reference._name == 'hr.department':
		        if record.reference.id == record.employee_id.department_id.id:
		           raise orm.except_orm(_('Warning'), _("You can not choose the employee's current department!")) 
		    if record.reference._name  == 'hr.job':
		        if record.reference.id == record.employee_id.job_id.id:
		           raise orm.except_orm(_('Warning'), _("You can not choose the employee's current job!")) 
		    if record.associated_ids:
		       for associated in record.associated_ids:
		          if associated.reference._name == record.reference._name: 
		             raise orm.except_orm(_('Warning'), _("You can not choose same reference in associated!")) 
        return True

    _constraints = [
        (_check_reference, "You can not choose an employee's current job/department!", ['reference']),
    ]  
    
#----------------------------------------
#Employee delegation
#----------------------------------------
class hr_employee_delegation(osv.Model):
    _name = "hr.employee.delegation"
    _description = "Employee Delegation"
    _rec_name= 'employee_id'
    _order= 'id desc'
    _columns = {
         'employee_id' : fields.many2one('hr.employee', "Employee", required=True,readonly=True, states={'draft':[('readonly',False)]}),
         'start_date' :fields.date("Start Date",readonly=True, states={'draft':[('readonly',False)]}),
         'destination' : fields.char("Destination", size=500, required=True,readonly=True, states={'draft':[('readonly',False)]}),
         'end_date' :fields.date("End Date",readonly=True, states={'draft':[('readonly',False)]}),
         'message': fields.char('Message', size=124,readonly=True),
         'comments': fields.text("Comments"),
         'type': fields.selection([('mandate','Mandate'),('loaned','Loaned'),
                                  ('transferred','Transferred')] ,'Type',required=True,readonly=True, states={'draft':[('readonly',False)]}),
         'destin': fields.selection([('1','الجهاز'),('2','القوات المسلحة'),
                                  ('3','الشرطة')] ,'Destination',required=True,readonly=True, states={'draft':[('readonly',False)]} ),                                       
         'state': fields.selection([('draft', 'Draft'),('complete', 'Complete'), ('confirm', 'Confirm'),
	                                ('approve', 'Approve'),('done', 'Done'),('cancel', 'Cancel')], 'State', readonly=True),
	  'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly',False)]}),
         'number' : fields.char("Number", size=500, required=True,readonly=True, states={'draft':[('readonly',False)]}),
    }  
    _defaults = {
        'state' : 'draft',   
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee.delegation', context=c), 
   }
    def _check_date(self, cr, uid, ids):
        """
	 Constrain method to sure that delegation start_date is before the end_date.

	 @return: boolean True or False
	"""
        for deleg in self.browse(cr, uid, ids):
            deleg_ids = self.search(cr, uid, [('start_date', '<=', deleg.end_date), ('end_date', '>=', deleg.start_date), ('employee_id', '=', deleg.employee_id.id),('id', '<>', deleg.id)])
            if deleg_ids:
                return False
        return True
 
    _constraints = [
        (_check_date, 'You can not have 2 delegation that overlaps on same day!', ['date_from','date_to']),
    ]
    _sql_constraints = [ ('date_check2', "CHECK ( date_from <= date_to)", "The start date must be anterior to the end date."),  
    ] 
    def duplicate(self, cr, uid, ids, context=None):
        process_obj = self.pool.get('hr.employee.delegation')
        for record in self.browse(cr, uid,ids):
            if record.employee_id.state=='approved':
               raise orm.except_orm(_('Warning'), _('This employee already has been Re-employment')) 
        return super(osv.osv, self).duplicate(cr, uid, ids, context)
     
    def copy(self, cr, uid, id, default=None, context=None):
        """
	Override duplication method to reset message to False.
	
	@return: super copy method
        """
        default = {} if default is None else default.copy()
        default['start_date'] = False
        default['end_date'] = False
        default.update({'message': '',})
        return super(hr_employee_delegation, self).copy(cr, uid, id, default=default, context=context)
        
    def check_loan(self, cr, uid, delegation, context=None):
        """
	Depicts the capacity of the delegation workflow to deal with loans.
        By default, it's True. Overwritten by hr_loan module.

	@return: boolean True
        """
        return True
        
    def check_holidays(self, cr, uid, delegation, context=None):
        """
	Depicts the capacity of the delegation workflow to deal with holidays.
        By default, it's True. Overwritten by hr_holidays_custom module.

	@return: boolean True
        """
        return True
        
    def check_punishment(self, cr, uid, delegation, context=None):
        """
	Depicts the capacity of the delegation workflow to deal with punishment.
        By default, it's True. Overwritten by hr_violation_punishment module.

	@return: boolean True
        """
        return True

    def my_done(self, cr, uid, ids,context=None):
		"""
        Workflow function change employee record state to 'approved' and 
        stop delegation, and change the delegation state to done
        @return: boolean True    
        """
		wf_service = netsvc.LocalService("workflow")
		emp_obj = self.pool.get('hr.employee')
		for rec in self.browse(cr, uid , ids):
			wf_service.trg_validate(uid, 'hr.employee',rec.employee_id.id ,'approve', cr)
			update = emp_obj.write(cr, uid, [rec.employee_id.id], {'delegation':False ,'state':'approved'})
		return self.write(cr, uid, ids, {'state':'done'})
    
    def approved(self, cr, uid, ids,context=None):
        """
        Workflow function change employee record state to 'refuse' and 
        set the employee in delegation state.

        @return: boolean True    
        """
        wf_service = netsvc.LocalService("workflow")
        emp_obj = self.pool.get('hr.employee')
        for rec in self.browse(cr, uid , ids):
            delegation = True
            if rec.type == 'loaned':
			    wf_service.trg_validate(uid, 'hr.employee',rec.employee_id.id ,'refuse', cr)
            if rec.type == 'transferred':
				delegation = False
				wf_service.trg_validate(uid, 'hr.employee',rec.employee_id.id ,'refuse', cr)
            emp_obj.write(cr, uid, [rec.employee_id.id], {'delegation':delegation}) 		
        self.write(cr, uid, ids, {'state':'approve'})

        return True

    def unlink(self, cr, uid, ids, context=None):
        """ 
        function to prevent deletion of employee delegation 
        record which is not in draft state  
        """
        for e in self.browse(cr, uid, ids):
            if e.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete an Employee Delegation Record Which Is Not In Draft State !'))
            check_reference = self.pool.get("hr.employee").search(cr, uid, [('delegation', '=', True)])
            if check_reference:
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete This Employee Delegation Record Which Is Referenced!'))
        return super(osv.osv, self).unlink(cr, uid, ids, context)   
#----------------------------------------
#RE-Employement
#----------------------------------------
class hr_employee_reemployment(osv.Model):
    _name ='hr.employee.reemployment'
    _description = "RE-Employement"
    _rec_name= 'employee_id'
    _order= 'id desc'
    _columns = {
        'employee_id': fields.many2one('hr.employee','Employee',required=True , readonly=True, states={'draft':[('readonly', False)]}),
        'reemployment_date' :fields.date("Re-employment Date", required= True, readonly=True, states={'draft':[('readonly', False)]}),
	    'comments':fields.text("Comments",size=300),
	    'qualification_ids':fields.one2many('hr.employee.qualification', 'reemployment', "New Qualifications", readonly=True, states={'draft':[('readonly', False)]}),
	    'state': fields.selection( [('draft', 'Draft'),('done', 'Done')], 'State', readonly=True),
	    'job_id': fields.many2one('hr.job','Job',required=True, readonly=True, states={'draft':[('readonly', False)]}),
	    'department_id': fields.many2one('hr.department','Department',required=True, readonly=True, states={'draft':[('readonly', False)]}),
	    'process_ids':fields.one2many('hr.process.archive', 'associated_reemployment' , 'Employee Processes', readonly=True, states={'draft':[('readonly', False)]}), 
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=False),
    }
    _defaults = {
        'state' : 'draft', 
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee.delegation', context=c), 
  
   }
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """
        Onchange method in employee field to reset job and the department of employee.
	
	@return: dictionary of values to be updated
        """
        if context is None: context = {}
        emp = self.pool.get('hr.employee').browse(cr, uid, employee_id , context=context)
        
        return {'value':{'job_id': emp.job_id.id,'department_id':emp.department_id.id }}

    def action_done(self, cr, uid, ids, context=None):
        """
        Method for reemployement for ended services employee.

        @return: True 
        """
        emp_obj = self.pool.get('hr.employee')
        wf_service = netsvc.LocalService("workflow")
        process_obj = self.pool.get('hr.process.archive')
        for record in self.browse(cr, uid,ids):
            if record.employee_id.state=='approved':
               raise osv.except_osv(_('Warning'), _('This employee already has been Re-employment'))
            emp_obj.write(cr, uid, [record.employee_id.id], {'re_employment_date': record.reemployment_date,} , context=context)
            wf_service.trg_validate(uid, 'hr.employee',record.employee_id.id ,'set_to_draft', cr)
            wf_service.trg_validate(uid, 'hr.employee',record.employee_id.id ,'approve', cr)
            vals= {
                   'code':record.employee_id.code,
                   'employee_id':record.employee_id.id,
                   'date': record.reemployment_date ,
                   'approve_date': time.strftime('%Y-%m-%d') ,
                   'company_id':record.company_id.id,
                   'comments':'Reemployement',
                   'associated_reemployment':record.id,
                   
            }
            if record.department_id.id!=record.employee_id.department_id.id:
                vals.update({'reference':'hr.department'+','+str(record.department_id.id),
                             'previous': record.employee_id.department_id.name,})
                process_id=process_obj.create(cr,uid,vals,context=context)
                wf_service.trg_validate(uid, 'hr.process.archive',process_id ,'approve', cr)

            if record.job_id.id!=record.employee_id.job_id.id:
                vals.update({'reference':'hr.job'+','+str(record.job_id.id),
                              'previous': record.employee_id.job_id.name })
                process_id=process_obj.create(cr,uid,vals,context=context)
                wf_service.trg_validate(uid, 'hr.process.archive',process_id ,'approve', cr)

            self.write(cr, uid, ids, { 'state' : 'done' }, context=context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Warning!'), _('You Cannot Duplicate Employee Reemployment !'))
        return super(hr_employee_reemployment, self).copy(cr, uid, id, default=default, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """ 
        function to prevent deletion of employee reemployment 
        record which is not in draft state  
        """
        for rec in self.browse(cr, uid, ids):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete Record Which Is Not In Draft State !'))
        return super(hr_employee_reemployment, self).unlink(cr, uid, ids, context)   
	
class hr_employee_qualification(osv.osv):
    _inherit = "hr.employee.qualification"
    _columns = {
        'reemployment' : fields.many2one('hr.employee.reemployment', "Reemployment"),
    }    	





