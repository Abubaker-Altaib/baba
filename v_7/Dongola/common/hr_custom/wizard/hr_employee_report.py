# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from tools.translate import _

class hr_employee_report(osv.osv_memory):
    _name= "hr.employee.reportt"
    

    def onchange_type(self, cr, uid, ids, report_type):
        return {'value':{} }

    _columns = {
    'company_id': fields.many2one('res.company', 'Company',required=True),   
    'department_ids':fields.many2many( 'hr.department','depart_common_job_rel','report_id','department_id', 'Departments'),  
    'job_ids': fields.many2many( 'hr.job', 'hr_common_job_rel','report_id','job_id', 'Jobs'),  
    'employee_ids': fields.many2many( 'hr.employee', 'hr_common_employee_rel','report_id','employee_ids', 'Employees'),  
    'date_from':fields.date('From'),
    'date_to':fields.date('To'),
    'groupby':fields.selection([
                             ('company', 'Company'),
                             ('department', 'Department')
                             ] , "Group by", required=True),
    'state':fields.selection([
                             ('draft', 'Draft'),
                             ('experiment', 'In Experiment'),
                             ('approved', 'In Service'),
                             ('refuse', 'Out of Service')] , "Employee State"),
    'report_type':fields.selection([
                             ('employee', 'Employee Record'),
                             ('relation', 'Employee Relation'),
                             ('qualif', 'Employee Qualification')] , "Report Type", required=True),

    'birthday': fields.boolean('Birthday and Age'),
    'emp_code': fields.boolean('Code'),
    'location': fields.boolean('Location'),   
    'sinid': fields.boolean('SIN ID'),   
    'summary': fields.boolean('Summary'),   
    'wizout_sinid': fields.boolean('With out social insurance'),     

      }
    def _get_companies(self, cr, uid, context=None): 
   
        return self.pool.get('res.users').browse(cr,uid,uid).company_id.id


    _defaults = {
        'company_id': _get_companies,
        'report_type' : 'employee',
        'groupby' : 'company',
                }
 
    def print_report(self, cr, uid, ids, context={}):
        data ={'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.common.report', 'datas': data}


 
