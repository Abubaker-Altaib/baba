# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.report import report_sxw
from openerp.osv import fields, osv, orm
import time
class report_custom(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_custom, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process':self._main_process,  
        })

    def _main_process(self,data):
       return [self._process(data)]


    def _process(self,data , dep_ids = None, outsite_scale=False):
        list_to_str = lambda items : ",".join(str(i) for i in items)
        #raise osv.except_osv(('Warning!'),('Sorry employees %s!') %data )
        self.cr.execute(
            '''
            SELECT 
              public.hr_employee.id as emp_id ,
              public.hr_employee.name_related as emp_name ,
              public.hr_employee.birthday as birth_date , 
              public.hr_employee.first_employement_date as first_employement_date ,
              public.hr_employee.promotion_date as promotion_date,
              public.hr_job.name as emp_job,
              public.hr_salary_degree.name as emp_degree ,
              public.resource_resource.id as res_id,
              public.res_users.company_id as company_id
            FROM 
              public.hr_employee,
              public.hr_salary_degree,
              public.hr_job,
              public.resource_resource ,
              public.res_users
            WHERE public.hr_job.id=hr_employee.job_id
                AND public.hr_salary_degree.id = public.hr_employee.degree_id
                AND public.resource_resource.id = public.hr_employee.resource_id
                AND public.resource_resource.user_id = public.res_users.id
                AND public.res_users.company_id IN (%s)
                order by public.hr_employee.name_related
               ;
            '''% (tuple([data['company_id'][0]]))  )
        emp_res = self.cr.dictfetchall()       
        emp_data = []
        for j , emp in enumerate(emp_res) :
          self.cr.execute(
            '''
            SELECT 
              public.hr_employee_qualification.id as emp_qualif_id ,
              public.hr_employee_qualification.employee_id as q_employee_id ,
              public.hr_employee_qualification.emp_qual_id as qualif_id ,
              public.hr_qualification.name as qualif_name,
              public.hr_qualification.order as qualif_order
            FROM 
              public.hr_employee_qualification,
              public.hr_qualification
            WHERE public.hr_qualification.id=public.hr_employee_qualification.emp_qual_id
                AND public.hr_employee_qualification.employee_id = %s 
                order by public.hr_employee_qualification.qual_date desc
               ;
            '''% (emp['emp_id'])  )
          qualif_res = self.cr.dictfetchall()    
          #raise osv.except_osv(('Warning!'),('Sorry employees %s!') %qualif_res[0] ) 
          if qualif_res:
             emp_row = {
            'emp_name' : emp['emp_name'] or ' ',
            'birth' :emp['birth_date'] or ' ',
            'employee_date':emp['first_employement_date'] or ' ',
            'emp_job' : emp['emp_job'] or ' ',
            'emp_degree':emp['emp_degree'] or ' ',
            'degree_date':emp['promotion_date'] or ' ',
            'qualif':qualif_res[0]['qualif_name'] or ' ',
             }
          else:
            emp_row = {
            'emp_name' : emp['emp_name'] or ' ',
            'birth' :emp['birth_date'] or ' ',
            'employee_date':emp['first_employement_date'] or ' ',
            'emp_job' : emp['emp_job'] or ' ',
            'emp_degree':emp['emp_degree'] or ' ',
            'degree_date':emp['promotion_date'] or ' ',
            'qualif':' ',
          }
          emp_data.append(emp_row)
        res = {
            'emp_data' : emp_data
          }
        return res


 
report_sxw.report_sxw('report.hr.common.report', 'hr.employee', 'addons/hr_custom/report/hr_employee_report.mako',parser=report_custom,header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
