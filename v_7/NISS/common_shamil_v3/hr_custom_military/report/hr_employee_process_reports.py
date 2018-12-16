# -*- coding: utf-8 -*-

from report import report_sxw

title = {
    'officer' : unicode('ر.البطاقة', 'utf-8') ,
    'soldier' : unicode('نمرة', 'utf-8'),
}

prosess = {

    'promotion' : unicode('الترقيات إلى رتبة ', 'utf-8') ,
    'department' : unicode('التنقلات إلى إدارة ', 'utf-8'),
    'job' : unicode('التنقلات إلى وظيفة ', 'utf-8') ,
    'bonus' : unicode('العلاوة السنوية إلى علاوة', 'utf-8'),
    'isolate' : unicode('العزل إلى رتبة ', 'utf-8') ,

}


class process_report(report_sxw.rml_parse):
    def get_record(self):
      wiz_object = self.pool.get('employee.promotion.wizard.report').browse(self.cr , self.uid , [self.context['active_id']])
      process_type = wiz_object[0].type
      if process_type == 'promotion' or process_type == 'isolate' : return self.get_promotion_record(wiz_object)
      if process_type == 'department' : return self.get_department_record(wiz_object)
      if process_type == 'job' : return self.get_job_record(wiz_object)
      if process_type == 'bonus' : return self.get_bonus_record(wiz_object)

    def get_promotion_record(self , wiz_object):
    	res = {}
    	for rec in wiz_object  :
            res['ref'] = rec.degree_id.name
            res['prosess'] = prosess[rec.type]
            res['type'] = title[rec.payroll_id.military_type]
            degree_move_type = rec.type == 'promotion' and 'promotion' or 'isolate'
            cond = [('state' , '!=' , 'draft') ,('process_type' , '=' , degree_move_type) ,('reference' , '=' , rec.degree_id.id)]
            if rec.start_date : 
                if rec.end_date : 
                    cond.append(('approve_date' , '>=' , rec.start_date))
                    cond.append(('approve_date' , '<' , rec.end_date))
                else : cond.append(('approve_date' , '=' , rec.start_date))
            pool_object = self.pool.get('hr.movements.degree')
            rec_ids = pool_object.search(self.cr , self.uid , cond)
            res['vals']=[]
            if rec_ids:
                ids_str = ",".join(str(i) for i in rec_ids)
                self.cr.execute('''
                    SELECT 
                      hr_employee.name_related as name, 
                      hr_employee.otherid as code ,
                      hr_salary_degree.name as prev ,
                      hr_salary_degree.sequence as degree_seq,
                      hr_department.name as dep_name,
                      hr_movements_degree.approve_date 
                    FROM 
                      public.hr_employee, 
                      public.hr_movements_degree, 
                      public.hr_salary_degree,
                      public.hr_department
                    WHERE 
                      hr_movements_degree.employee_id = hr_employee.id And
                      hr_movements_degree.last_degree_id = hr_salary_degree.id  And
                      hr_employee.department_id = hr_department.id  And 
                      hr_movements_degree.id in (%s)
                    order by hr_employee.otherid
                ''' %(ids_str) )
                emp_data = self.cr.dictfetchall()
                temp = sorted(emp_data, key=lambda k: k['degree_seq'],reverse=True) #sorting using degree 
                res['vals'] = temp
        return res

    def get_department_record(self , wiz_object):
      res = {}
      for rec in wiz_object  :
            res['ref'] = rec.job_id.name
            res['prosess'] = prosess[rec.type]
            res['type'] = title[rec.payroll_id.military_type]
            cond = [('state' , '!=' , 'draft') , ('reference' , '=' , rec.department_id.id)]
            if rec.start_date : 
                if rec.end_date : 
                    cond.append(('approve_date' , '>=' , rec.start_date))
                    cond.append(('approve_date' , '<' , rec.end_date))
                else : cond.append(('approve_date' , '=' , rec.start_date))
            pool_object = self.pool.get('hr.movements.department')
            rec_ids = pool_object.search(self.cr , self.uid , cond)
            res['vals']=[]
            if rec_ids:
                ids_str = ",".join(str(i) for i in rec_ids)
                self.cr.execute('''
                    SELECT 
                      hr_employee.name_related as name, 
                      hr_employee.otherid as code ,
                      hr_salary_degree.name as prev ,
                      hr_salary_degree.sequence as degree_seq,
                      hr_department.name as dep_name,
                      hr_movements_department.approve_date 
                    FROM 
                      public.hr_employee, 
                      public.hr_movements_department, 
                      public.hr_salary_degree,
                      public.hr_department
                    WHERE 
                      hr_employee.degree_id = hr_salary_degree.id And
                      hr_movements_department.employee_id = hr_employee.id  And
                      hr_employee.department_id = hr_department.id  And 
                      hr_movements_department.id in (%s)
                    order by hr_employee.otherid
                ''' %(ids_str) )
                emp_data = self.cr.dictfetchall()
                temp = sorted(emp_data, key=lambda k: k['degree_seq'],reverse=True) #sorting using degree 
                res['vals'] = temp
      return res

    def get_job_record(self , wiz_object):
      res = {}
      for rec in wiz_object  :
            res['ref'] = rec.department_id.name
            res['prosess'] = prosess[rec.type]
            res['type'] = title[rec.payroll_id.military_type]
            cond = [('state' , '!=' , 'draft') , ('reference' , '=' , rec.job_id.id)]
            if rec.start_date : 
                if rec.end_date : 
                    cond.append(('approve_date' , '>=' , rec.start_date))
                    cond.append(('approve_date' , '<' , rec.end_date))
                else : cond.append(('approve_date' , '=' , rec.start_date))
            pool_object = self.pool.get('hr.movements.job')
            rec_ids = pool_object.search(self.cr , self.uid , cond)
            res['vals']=[]
            if rec_ids:
                ids_str = ",".join(str(i) for i in rec_ids)
                self.cr.execute('''
                    SELECT 
                      hr_employee.name_related as name, 
                      hr_employee.otherid as code ,
                      hr_salary_degree.name as prev ,
                      hr_salary_degree.sequence as degree_seq,
                      hr_department.name as dep_name,
                      hr_movements_job.approve_date 
                    FROM 
                      public.hr_employee, 
                      public.hr_movements_job, 
                      public.hr_salary_degree,
                      public.hr_department
                    WHERE 
                      hr_employee.degree_id = hr_salary_degree.id And
                      hr_movements_job.employee_id = hr_employee.id  And
                      hr_employee.department_id = hr_department.id  And 
                      hr_movements_job.id in (%s)
                    order by hr_employee.otherid
                ''' %(ids_str) )
                emp_data = self.cr.dictfetchall()
                temp = sorted(emp_data, key=lambda k: k['degree_seq'],reverse=True) #sorting using degree 
                res['vals'] = temp
      return res

    def get_bonus_record(self , wiz_object):
      res = {}
      for rec in wiz_object  :
            res['ref'] = rec.bonus_id.name
            res['prosess'] = prosess[rec.type]
            res['type'] = title[rec.payroll_id.military_type]
            cond = [('state' , '!=' , 'draft') , ('reference' , '=' , rec.bonus_id.id)]
            if rec.start_date : 
                if rec.end_date : 
                    cond.append(('approve_date' , '>=' , rec.start_date))
                    cond.append(('approve_date' , '<' , rec.end_date))
                else : cond.append(('approve_date' , '=' , rec.start_date))
            pool_object = self.pool.get('hr.movements.bonus')
            rec_ids = pool_object.search(self.cr , self.uid , cond)
            res['vals']=[]
            if rec_ids:
                ids_str = ",".join(str(i) for i in rec_ids)
                self.cr.execute('''
                    SELECT 
                      hr_employee.name_related as name, 
                      hr_employee.otherid as code ,
                      hr_salary_degree.name as prev ,
                      hr_salary_degree.sequence as degree_seq,
                      hr_department.name as dep_name,
                      hr_movements_bonus.approve_date 
                    FROM 
                      public.hr_employee, 
                      public.hr_movements_bonus, 
                      public.hr_salary_degree,
                      public.hr_department
                    WHERE 
                      hr_employee.degree_id = hr_salary_degree.id And
                      hr_movements_bonus.employee_id = hr_employee.id  And
                      hr_employee.department_id = hr_department.id And 
                      hr_movements_bonus.id in (%s)
                    order by hr_employee.otherid
                ''' %(ids_str) )
                emp_data = self.cr.dictfetchall()
                temp = sorted(emp_data, key=lambda k: k['degree_seq'],reverse=True) #sorting using degree
                res['vals'] = temp
      return res
    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(process_report, self).__init__(cr, uid, name, context=context)
        records = dict()
        records = self.get_record()
        self.localcontext.update(records)



report_sxw.report_sxw('report.hr_employee_promotion_report','hr.move.order','addons/hr_custom_military/report/hr_employee_promotion_report.mako',parser=process_report,header=False)
