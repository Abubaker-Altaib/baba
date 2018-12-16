# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
###############################################################################

import time
from datetime import datetime
from openerp.osv import fields, osv ,orm
from openerp.tools.translate import _
import mx.DateTime as dt
import mx

#----------------------------------------
#hr job(inherit)
#----------------------------------------

class hr_job(osv.Model):

    def _get_job_approved(self, cr, uid, ids, context=None):
        """
	Method that returns the ID of job approval updated to update the 
	functional field in the job consequently.

        @return: List of the ids of the approved job
        """
        res = []
        for apr in self.pool.get('hr.employment.approval').browse(cr, uid, ids, context=context):
            if apr.state=='approved':
                res.append(apr.job_id.id)
        return res

    def _no_of_employee(self, cr, uid, ids, name, args, context=None):
        """
	Functional fields method that calculates the total aprroved, occupied 
	and the available job positions.
        
	@param name: name of field to be updated
	@param args: other arguments
	@return: Dictionary of values	
        """
        res = {}
        for job in self.browse(cr, uid, ids, context=context):
            nb_employees = len(job.employee_ids or [])
            no_of_recruitment=sum([line.approved  for line in job.approved_ids if job.approved_ids])
            #expected = 0.0
            #if no_of_recruitment != 0.0 :
                #expected=no_of_recruitment-nb_employees
            res[job.id] = {
                'no_of_employee': nb_employees,
                'expected_employees': (job.no_of_recruitment+no_of_recruitment)-nb_employees ,
                'no_of_recruitment':job.no_of_recruitment+no_of_recruitment,
                          }
        return res

    def _get_job_position(self, cr, uid, ids, context=None):
        """
	Method that returns the ID of employee record updated to update the 
	functional field in the job consequently.

        @return: List contains the changed job id
        """
        res = []
        for employee in self.pool.get('hr.employee').browse(cr, uid, ids, context=context):
            if employee.job_id and employee.state!='refused':
                res.append(employee.job_id.id)
        return res

    def job_open(self, cr, uid, ids, *args):
        """
	Method that overwrites job_open to update hr.employment.approval record by 
	setting its state to 'no_recruitment'.

        @return: Boolean True
        """
        for job in self.browse(cr, uid, ids, context=None):
            job_ids=self.pool.get('hr.employment.approval').search(cr, uid, [('job_id','=',job.id)], context=None)
            job_ids and self.pool.get('hr.employment.approval').write(cr, uid, job_ids, {'state': 'no_recruitment'})
        self.write(cr, uid, ids, {'state': 'open'})
        return True

    _inherit="hr.job"
    _columns = {
  
            'no_of_recruitment': fields.function(_no_of_employee, string="Expected In Recruitment",type='float', method=True, 
                 help='Number of new employees you expect in job .',
                 store = { 'hr.job': (lambda self,cr,uid,ids,ctx={}: ids, ['no_of_recruitment'], 10),
                           'hr.employment.approval': (_get_job_approved, ['state'], 10),},multi='no_of_employee'),
            'approved_ids':fields.one2many('hr.employment.approval','job_id',"Approved jobs", readonly=True,domain=[('state','=','approved')]),
              
            'expected_employees': fields.function(_no_of_employee, string='Available position',
            help='Free position of this job position after new recruitment.',
            store = {
                'hr.job': (lambda self,cr,uid,ids,c=None: ids, ['no_of_recruitment'], 10),
                'hr.employment.approval': (_get_job_approved, ['state'], 10),
                'hr.employee': (_get_job_position, ['job_id'], 10),
                    },
            multi='no_of_employee'),
            'no_of_employee': fields.function(_no_of_employee, string="Current Number of Employees",
            help='Number of employees currently occupying this job position.',
            store = {
                'hr.employee': (_get_job_position, ['job_id'], 10),
                'hr.employment.approval': (_get_job_approved, ['state'], 10),
            },  multi='no_of_employee'),
 }
    _defaults = {
            'no_of_recruitment': lambda *a: 0.0, 
                 }

#----------------------------------------
# hr employment needs 
#----------------------------------------

class hr_employment_needs(osv.Model):

    _name = "hr.employment.needs"
    _description = "Employment Needs"
    _columns = {  
                 'department_id': fields.many2one('hr.department',"Department", required= True ),
                 'year': fields.integer("Year", required= True ),
                 'reasons':fields.text("Reasons", size=180),
		 'job_id':fields.many2one("hr.job", "Job",required= True),
		 'need':fields.integer("Needed Positions" ,required= True),
                 'approve_id': fields.many2one('hr.employment.approval',"approval" ),
               } 
  
    _defaults = {
        'year' : int(time.strftime('%Y')), 
                }

    def unlink(self, cr, uid, ids, context=None, check=True):
        """
	Method that prevents the deletion of under approval employment needs.

        @return: Super unlink mehtod
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.approve_id :
                raise orm.except_orm(_('UserError'), _('Sorry this need is under approval You can not delete it !') )
        return super(hr_employment_needs, self).unlink(cr, uid, ids, context=context)

#----------------------------------------
# hr employment approval
#----------------------------------------

class hr_employment_approval(osv.Model):

    def requested_job(self, cr, uid, ids, name, args, context=None):
        """
	Functional field method that calculates the total requested job.
	        
	@param name: name of field to be updated
	@param args: other arguments
        @return: Dictionary that contains the total requested job
        """
        result={}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id]=sum([line.need for line in rec.need_ids if rec.need_ids])
        return result

    def check_no_of_request(self, cr, uid, ids, context={}):
        """
	Constrain method that checks if the approved position exceeds the requested position or not.

        @return: Boolean True or False
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.approved>rec.requested :
                return False
        return True

    _name = "hr.employment.approval"
    _description = "Employment Needs Approval"
    _columns = {  
         'job_id': fields.many2one('hr.job', "Job", required=True),
         'year': fields.integer("Year", required=True ),
         'requested': fields.function(requested_job, string='Requested Positions', type='integer', method=True, 
					store={
					'hr.employment.approval': (lambda self, cr, uid, ids, c={}: ids, ['need_ids'], 10),
					}),
         'approved': fields.integer("Approved Positions", required= True),
         'state':fields.selection([
                                   ('draft','Draft'),
                                   ('confirmed','Confirmed'),
                                   ('approved','Approved'),
                                   ('refused', 'Refused'),
                                   ('no_recruitment','No Recruitment'), ],"State", readonly=True),
         'need_ids': fields.one2many('hr.employment.needs','approve_id',"Needs", readonly=True),
         'rejection_reason' : fields.text("Rejection Reason ", size=500 ),
               } 

    _defaults = {
            'state': 'draft',
            'year' : int(time.strftime('%Y')),
            'requested': lambda *a: 0, 
            'approved': lambda *a: 0, 
                 }

    _constraints = [
        (check_no_of_request, 'Sorry you can not exceed the maximum requested jobs %s',['approved']),
                    ]

    def draft(self, cr, uid, ids, context=None):
        """
	Method that sets the state to 'draft'.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'draft'}) 
        return True

    def confirmed(self, cr, uid, ids, context=None):
        """
	Workflow function that changes the state to 'confirmed'.

        @return: Boolean True
        """
	for r in self.browse(cr, uid, ids, context):
	    if r.approved<1:
                raise osv.except_osv(_('Warning'), _('Unvaild number of approved job, should be greater than zero'))			
        self.write(cr, uid, ids, {'state':'confirmed'}) 
        return True

    def approved(self, cr, uid, ids, context=None):
        """
	Workflow function that changes the state to 'approved'.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'approved'}) 
        return True

    def refused(self, cr, uid, ids, context=None):
        """
	Workflow function that changes the state to 'refused'.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'refused'}) 
        return True

    def set_to_draft(self, cr, uid, ids, context=None):
        """
	Method that sets the state to 'draft'.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft',})
        return True

    def change_year(self, cr, uid, ids, year,context={}):
        """
	Method returns all the requested job  in the selected year.

        @param year: Year to get its requested job 
        @return: Dictionary that contains all the the requested job
        """
        domain = {}
        if year:
            cr.execute('''SELECT DISTINCT job_id FROM hr_employment_needs WHERE approve_id is null AND year=%s'''%year)
            domain = {'job_id':[('id', 'in', sorted(rec['job_id'] for rec in cr.dictfetchall() if  cr.dictfetchall ))]} 
        return {'value': {'job_id':False} , 'domain': domain}

    def create(self, cr, uid, data, context=None):
        """
	Method creates job approval record from the requested job and if there is two approval records
        for the same job in the draft state it merges them in single approval record.

        @param data: Dictionary contains the enterred data 
        @return: ID of the created record
        """
        cr.execute('''SELECT id need_id FROM hr_employment_needs WHERE year=%s AND job_id=%s AND approve_id is null''',(data['year'],data['job_id']))
        result = sorted(rec['need_id'] for rec in cr.dictfetchall() if  cr.dictfetchall )
        draft_need=self.search(cr,uid,[('year','=',data['year']),('job_id','=',data['job_id']),('state','=','draft')])
        if draft_need :
            for x in result:
               self.write(cr, uid, draft_need[0], {'need_ids':[(4, x, False)] }, context=context)
            return draft_need[0]
        approve_id = super(hr_employment_approval, self).create(cr, uid, data, context=context)
        for x in result:
             self.write(cr, uid, approve_id, {'need_ids':[(4, x, False)] }, context=context)
        return approve_id

    def write(self, cr, uid, ids,vals, context=None):
        """
	Method prevents changing the job.

        @param vals: Dictionary contains the updated data 
        @return: Super write mehtod
        """
        if 'job_id' in vals:
            raise orm.except_orm(_('Warrning'), _('Sorry the job in this record is not changable !') )
        return super(hr_employment_approval, self).write(cr, uid, ids, vals, context=context)




