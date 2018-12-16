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

class employee_by_department(osv.osv_memory):


    _name= "hr.report.jobs"
    _columns = {
    'company': fields.many2one( 'res.company', 'Company'),   
    'department_ids':fields.many2many( 'hr.department','hr_report_dep_rel','report_id','department_id', 'Departments'),  
    'job_ids': fields.many2many( 'hr.job', 'hr_report_job_rel','report_id','job_id', 'Jobs'),  


    'state':fields.selection([
                             ('draft', 'Draft'),
                             ('experiment', 'In Experiment'),
                             ('approved', 'In Service'),
                             ('refuse', 'Out of Service')] , "Employee State"),
    'report_type':fields.selection([
                             ('jobs', 'Job Positions'),
                             ('manager', 'Department Managers')] , "Report Type", required=True),
      }
    _defaults = {
        'report_type' : 'jobs',
                } 
    def print_report(self, cr, uid, ids, context={}):
	print ids
        data ={'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.employee.jobs', 'datas': data}
	data = self.read(cr, uid, ids, ['job_ids','department_ids','report_type','company'])[0]
	select_query = False
	append_where = "  "
        label = {}
	if  data['report_type'] == 'jobs':
                title="Based On Jobs"
		if data['company']:
		    print  data['company']
		    append_where += " and j.company=%s  " % str(data.get('company')[0])
		if data['job_ids']:
		    append_where += " and j.id in (%s) "   % ','.join(map(str, data['job_ids']))
		if data['department_ids']:
		    append_where += " and e.department_id in (%s) " % ','.join(map(str, data['department_ids']))
		groupby_dic =  [{'job_id': 1 }]
		groupby_data = {'job_id':['job_name','planned','available'] }
		list_data = []
	        #label = { 'department_name': _('Department'), 'name':_('Manager'), 'level':1}
		view_query = ''' SELECT j.id as job_id, j.name as job_name, d.name as department_name,
				  l.no_emp as no_emp, e.id as emp_id,
				  no_of_recruitment as planned,
				  expected_employees as available, 
				  code as code, 
				  no_of_employee as current
				FROM   hr_job as j 
				  left join department_jobs l on (j.id = l.job)
				  left join hr_department d on (d.id = l.department_id)
				  left join hr_employee e on (e.job_id = j.id and d.id = e.department_id)
				where j.id is not null
				''' + append_where 
		select_query = " SELECT   %s as level, \
					CASE WHEN min(department_name) is not null THEN  min(department_name) ELSE '_' END AS  department_name,\
					sum(no_emp)          as ab,  \
					count(emp_id)        as bb  \
					FROM  hr_common_report  "	 	
		#TODO: don't display nul sum
	else:
                title="Based On Departments Managers"
		append_where = data['department_ids'] and " where h.department_id in (%s) " % ','.join(map(str, data['department_ids'])) or "  "
		groupby_dic =  []
		groupby_data = False
		view_query = False
		list_data = ['department_name','name']
	        label = { 'department_name': _('Department'),'name':_('Manager'),'level':1}
		view_query =  "  SELECT  1 as level, r.name,  d.name as department_name FROM\
		 			hr_department d \
					left join hr_employee h on(h.id= d.manager_id)\
		  			left join resource_resource r on (h.resource_id = r.id) " +   append_where  
        
        datas = {
             'ids': [],
	     'wiz_id':ids,
             'model': 'hr_report_jobs',
	     'view_query':view_query,	     
	     'select_query':select_query,
	     'title':title,
	     'groupby_dic':groupby_dic,
	     'groupby_data':groupby_data,
	     'label':label,
	     'list_data': list_data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.common.report',
            'datas': datas,
            }

 
