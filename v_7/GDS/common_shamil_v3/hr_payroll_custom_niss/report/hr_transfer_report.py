# -*- coding: utf-8 -*-

import time
import pooler
#import rml_parse
import copy
from report import report_sxw
import pdb
import re
from osv import fields, osv
from tools.translate import _




class transfer_report(report_sxw.rml_parse):
       _name = 'report.transfer.report'
       def __init__(self, cr, uid, name, context):
        super(transfer_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process':self._main_process,  
        })

       def _main_process(self,data):
     		return [self._process(data)]


       def _process(self,data , dep_ids = None, outsite_scale=False):
		list_to_str = lambda items : ",".join(str(i) for i in items)
		#raise osv.except_osv(('Warning!'),('Sorry employees %s!') %data )
                company_cond=' '
                from_cond=' '
                to_cond=' '
                destination_cond=' '
                number_cond = ' '
                if data['date_from']:
                   if data['process_type']=='in':
                      from_cond="AND public.hr_employee.employment_date >= '%s'" %(data['date_from'])
                   else:
                      from_cond="AND public.hr_employee_delegation.start_date >= '%s'" %(data['date_from'])
                if data['date_to']:
                   if data['process_type']=='in':
                      to_cond="AND public.hr_employee.end_date <= '%s'" %(data['date_to'])
                   else:
                      to_cond="AND public.hr_employee_delegation.end_date <= '%s'" %(data['date_to'])
		if data['company_id']:
		       company_cond="AND public.resource_resource.company_id IN (%s)" %(tuple([data['company_id'][0]]))
                if data['destin']:
		       destination_cond="AND public.process_destin.id IN (%s)" %(tuple([data['destin'][0]]))
                if data['number']:
                   if data['process_type']=='in':
                      number_cond="AND public.hr_employee.decion_number = '%s'" %(data['number'])
                   else:
                      number_cond="AND public.hr_employee_delegation.number = '%s'" %(data['number'])
                if data['process_type']=='in':
                   self.cr.execute(
		    '''
		    SELECT 
		      public.hr_employee.id as emp_id ,
		      public.hr_employee.name_related as emp_name ,
                      public.hr_employee.emp_code as emp_code,
		      public.hr_job.name as emp_job,
		      public.hr_salary_degree.name as emp_degree ,
                      public.hr_salary_degree.sequence as emp_degree_seq ,
                      public.process_destin.name as prev_com_emp,
                      public.resource_resource.company_id as new_com_emp,
                      public.hr_employee.external_transfer as deleg_type,
                      public.hr_employee.decion_number as deleg_num,
                      public.hr_employee.employment_date as move_date,
                      public.hr_employee.end_date as move_end_date,
                      public.resource_resource.id as res_id
		    FROM 
		      public.hr_employee,
		      public.hr_salary_degree,
		      public.hr_job,
                      process_destin,
                      public.resource_resource
		    WHERE public.hr_job.id=hr_employee.job_id
                        AND public.process_destin.id=hr_employee.previous_institute
		        AND public.hr_salary_degree.id = public.hr_employee.degree_id
		        AND public.resource_resource.id = public.hr_employee.resource_id 
                        AND public.hr_employee.external_transfer in ('transfer','mandate','loaning')
                        %s %s %s %s %s
		       ;
		    '''% (company_cond,from_cond,to_cond,destination_cond,number_cond)  )
                else:
                   self.cr.execute(
			    '''
			    SELECT 
			      public.hr_employee.id as emp_id ,
			      public.hr_employee.name_related as emp_name ,
			      public.hr_employee.emp_code as emp_code,
			      public.hr_salary_degree.name as emp_degree ,
                              public.hr_salary_degree.sequence as emp_degree_seq ,
		              public.hr_employee_delegation.company_id as prev_com_delegte,
                              public.process_destin.name as new_com_delegte,
		              public.hr_employee_delegation.type as deleg_type,
		              public.hr_employee_delegation.number as deleg_num,
		              public.hr_employee_delegation.start_date as move_date,
		              public.hr_employee_delegation.end_date as move_end_date,
		              public.resource_resource.id as res_id
			    FROM 
			      public.hr_employee,
			      public.hr_salary_degree,
			      public.hr_employee_delegation,
                              process_destin,
		              public.resource_resource
			    WHERE
				public.hr_salary_degree.id = public.hr_employee.degree_id
                                AND public.process_destin.id = public.hr_employee_delegation.destin
		                AND public.hr_employee_delegation.employee_id=public.hr_employee.id
				AND public.resource_resource.id = public.hr_employee.resource_id 
		                AND public.hr_employee_delegation.state='approve'
		                %s %s %s %s %s
			       ;
                   '''% (company_cond,from_cond,to_cond,destination_cond,number_cond)  )
		emp_res = self.cr.dictfetchall()       
		emp_data = []
		for j , emp in enumerate(emp_res) : 
                  prev_comp=' '
                  new_com=' '
                  end_date=' '
                  if 'prev_com_delegte' in  emp:
                     prev_comp=self.pool.get('res.company').browse(self.cr,self.uid,emp['prev_com_delegte']).name
                  if 'prev_com_emp' in emp:
                     prev_comp=emp['prev_com_emp']
                  if 'new_com_delegte' in emp:
                      new_com=emp['new_com_delegte']
                  if 'new_com_emp' in emp:
                      new_com=self.pool.get('res.company').browse(self.cr,self.uid,emp['new_com_emp']).name
                  if 'move_end_date' in emp:
                     end_date=emp['move_end_date']
                  if prev_comp == 'GDS':
                     prev_comp = unicode('قوات الدعم السريع', 'utf-8')
                  if new_com == 'GDS':
                     new_com = unicode('قوات الدعم السريع', 'utf-8')     
		  emp_row = {
		    'emp_name' : emp['emp_name'] or ' ',
		    'emp_code' : emp['emp_code'] or ' ',
		    'emp_degree':emp['emp_degree'] or ' ',
                    'sequence'  : emp['emp_degree_seq'] or ' ',
                    'deleg_type':emp['deleg_type'] or ' ',
                    'deleg_num':emp['deleg_num'] or ' ',
		    'prev_com' :prev_comp,
		    'new_com':new_com,
		    'move_date':emp['move_date'] or ' ',
                    'move_end_date':end_date or ' ',
		     }
		  emp_data.append(emp_row)
		temp = sorted(emp_data, key=lambda k: k['emp_code']) #sorting using code
		temp2 = sorted(temp, key=lambda k: k['sequence'],reverse=True) #sorting using degree
		res = {
		    'emp_data' : temp2
		  }
		return res

report_sxw.report_sxw('report.hr.employee.transfer', 'hr.allowance.deduction.archive','common_shamil_v3/hr_payroll_custom_niss/report/hr_employee_report.mako', parser=transfer_report,header=False)
