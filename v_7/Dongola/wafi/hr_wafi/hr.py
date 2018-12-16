# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp import netsvc
from openerp.tools.translate import _
import time
from openerp.osv import fields, osv
import mx


class hr_employee_reemployment(osv.osv):

    _inherit ='hr.employee.reemployment'

    _columns = {
        'state': fields.selection( [('draft', 'Draft'),('complete', 'Complete'), ('confirm', 'Confirm'),
                                    ('approve', 'Approve'),('done', 'Done'),('cancel', 'Cancel')], 'State', readonly=True),
    }

    def reemployment_check(self, cr, uid, ids, context=None):
        """
        method to prevent the re-employment for employee has dismissal or the period of termination not completed  
        return raise exception if not pass the condition or not True 
        """
        termination_obj = self.pool.get('hr.employment.termination')
        for rec in self.browse(cr, uid, ids, context=context):
            term_id=termination_obj.search(cr, uid, [('employee_id', '=', rec.employee_id.id),('state', '!=', 'draft')], order='dismissal_date', limit=1, context=context)
            for r in termination_obj.browse(cr, uid, term_id, context=context):
                if not r.dismissal_type.reemployment:
                    msg = _("You can not re-employment the employee the reason for termination is'%s' ") % (r.dismissal_type.name,)
                    cr.execute('update hr_employee_reemployment set comments=%s where id in %s', (msg, tuple(ids),))
                    return False
                start = time.mktime(time.strptime(r.dismissal_date,'%Y-%m-%d'))
                end = time.mktime(time.strptime(rec.reemployment_date,'%Y-%m-%d'))
                days= ((end - start) / (3600 * 24)) + 1
                months= days/30
                if months < r.dismissal_type.period:
                    msg = _("You cannot re-employment the employee only after '%s' months from the end of his service") % (r.dismissal_type.period,)
                    cr.execute('update hr_employee_reemployment set comments=%s where id in %s', (msg, tuple(ids),))
                    return False
        return True


class hr_process_archive(osv.osv):

    _inherit ='hr.process.archive'
    
    def _degree_level(self, cr, uid, ids, name, args, context=None):
        result = {}
        degree_obj = self.pool.get('hr.salary.degree')  
        reads = self.read(cr, uid, ids, ['reference'], context=context)
        for rec in reads:
            level=0
            (model_name, id) = rec['reference'].split(',')   
            if model_name  == 'hr.salary.degree':
				o = degree_obj.read(cr, uid, [id],['sequence'])
				sequence = o and o[0]['sequence']
				if sequence <= 3:
					level = 1
				elif sequence >= 4 and sequence <=6:
					level = 2
				else:
					level = 3 
            result[rec['id']] = level
        return result

    _columns = {
        'degree_level': fields.function(_degree_level, string='Degree level'),
        'state':fields.selection([('draft','Draft'),('hr_user','Hr User '),
                                ('section_manager','Section Manager'),('department_manager','Department Manager'),
                                ('hr_manager','Hr Manager'),('unit_manager','Unit Manager'),('minister','Minister'),
                                ('service_manager','Service Manager'),('council_ministers',' Council Ministers'),
                                ('approved','Approved') ], 'Status' ,select=True, readonly=True),
    }

 
    def to_unit_manager(self, cr, uid, ids, context=None):
        for promotion in self.browse(cr, uid, ids, context=context):
			if promotion.promotion_type:
				emp_prom = self.search(cr, uid, [('employee_id','=',promotion.employee_id.id),('id','=',promotion.id)])
				if emp_prom:
					pro_obj = self.browse(cr, uid, emp_prom[0], context=context)
					pro2_date = mx.DateTime.Parser.DateTimeFromString(pro_obj.date)
					pro_margin_days= promotion.promotion_type.margin_time
					emp_date = mx.DateTime.Parser.DateTimeFromString(promotion.employee_id.employment_date) 
					current_pro_date = mx.DateTime.Parser.DateTimeFromString( promotion.date)
					if  pro_margin_days < current_pro_date -pro2_date and pro_margin_days < current_pro_date -emp_date :
						raise osv.except_osv(_('Warning!'), _('You cannot promote this Employee until the configure days in promotion type completed  !'))          
				              
        return self.write(cr, uid, ids, {'state' : 'unit_manager' }, context=context)


class hr_employee_qualification(osv.Model):

    _inherit = "hr.employee.qualification"

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('complete','complete'),('approved', 'Approved'),
                                  ('rejected', 'Rejected'), ], 'State', readonly=True),
    }

    def complete_quali(self, cr, uid, ids, context=None):
        """
        Add qualification to the employee, change the state to complete
        """
        return self.write(cr, uid, ids, {'state': 'complete'}, context=context)


class hr_employee_family(osv.Model):

    _inherit = "hr.employee.family"

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('complete','complete'),
                                   ('approved', 'Approved'), ('rejected', 'Rejected'),
                                   ('to_stop', 'To Stop') ,('stopped', 'Stopped')],
                                  'State', readonly=True),
    }

    def family_complete(self, cr, uid, ids, context={}):
        """
        Add employee family record, change state to approved.
        """
        return self.write(cr, uid, ids, {'state': 'complete'}, context=context)

    def family_to_stop(self, cr, uid, ids, context={}):
        """
        Add employee family record, change state to approved.
        """
        return self.write(cr, uid, ids, {'state': 'to_stop'}, context=context)


class hr_job(osv.osv):

    _inherit ='hr.job'

    def _degree_level(self, cr, uid, ids, name, args, context=None):
        result = {}
        for job in self.browse(cr, uid, ids, context=context):
            level=0
            degrees = [degree.id for degree in job.degree_ids]
            if degrees:
                cr.execute("select MIN(sequence) from hr_salary_degree  where id in %s" , (tuple(degrees),))
                res = cr.fetchone()
                sequence = res and res[0] or 0
                if sequence <= 3:
                    level = 1
                elif sequence >= 4 and sequence <=6:
                    level = 2
                else:
                    level = 3 
            result[job.id] = level
        return result

    _columns = {
        'degree_level': fields.function(_degree_level, string='Degree level'),
        'degree_ids':fields.many2many('hr.salary.degree', 'job_degree_rel', 'degree_id', 'job_id', 'Degrees', readonly= True ,
                                       states={'draft':[('readonly',False)]}),
        'no_of_recruitment': fields.integer('Expected New Employees', copy=False, readonly= True,
                                            states={'draft':[('readonly',False)]},help='Number of new employees you expect to recruit.'),
        'state':fields.selection([('draft', 'Draft'),('complete', 'HR User'),
                                ('confirm', 'HR Manager'),('unit_manager', 'Unit Manager'),
                                ('minister', 'Minister'),('service_manager', 'Service Manager'),
                                ('finance_minister', 'Finance Minister'),('done', 'Done'),
                                ('cancel', 'Cancelled')], 'Status', select=True, readonly=True),
    }

    _defaults = {
        'state': "draft"
    }

    def action_request(self, cr, uid, ids, context=None):
        for job in self.browse(cr, uid, ids):
            if job.type == 'normal': 
                if not job.degree_ids:
                    raise osv.except_osv(_('Error'), _('Error Add degree '))
        return self.write(cr, uid, ids, {'state' : 'complete' }, context=context)
        
        

