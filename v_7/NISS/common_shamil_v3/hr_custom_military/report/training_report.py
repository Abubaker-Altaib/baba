# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from openerp.tools.translate import _



def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class training(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.context = context
        super(training, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
        })
    
    def _to_arabic(self, data):
        key = _(data)
        key = key == 'v_good' and 'very good' or key
        key = key == 'u_middle' and 'under middle' or key
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module','=', 'hr_custom_military'),('type','=', 'selection'),('src','ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key
        
        return key

    def _get_all_len(self, data):
        if self.context and 'active_model' in self.context and self.context['active_model'] == 'hr.military.training':
            id = self.context['active_id']
            query = """select training.state,training.reference,training.training_eval,
                    training.participation_type,training.course_type,training.location,
                    training.start_date,training.end_date ,cat.name as type_name, 
                    place.name as place_name,emp.otherid,emp.name_related,
                    deg.name as deg_name,job.name as job_name 
                    from hr_military_training training 
                    left join hr_employee emp on (training.employee_id=emp.id) 
                    left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                    left join hr_job job on(job.id = emp.job_id) 
                    left join hr_military_training_category cat on(cat.id = training.type) 
                    left join hr_military_training_place place on(place.id = training.place)
                    where training.id="""+str(id)
            self.cr.execute(query)
            res = self.cr.dictfetchall()
            self.all_data = res
            
            return len(self.all_data)

        employee_id = data['form']['employee_id']
        type = data['form']['type']
        start_date = data['form']['start_date']
        location = data['form']['location']
        place = data['form']['place']
        end_date = data['form']['end_date']
        course_type = data['form']['course_type']
        participation_type = data['form']['participation_type']
        training_eval = data['form']['training_eval']
        reference = data['form']['reference']
        state = data['form']['state']
        company_id = data['form']['company_id']
        who_not_take = data['form']['who_not_take']

        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']


        clouses = False

        #for who_not_take emp search

        who_not_take_clouses = False

        if employee_id:
            employee_id = employee_id[0]
            if clouses:
                clouses += " and training.employee_id="+str(employee_id)
            if not clouses:
                clouses = "training.employee_id="+str(employee_id)

        if type:
            type = type[0]
            if clouses:
                clouses += " and training.type="+str(type)
            if not clouses:
                clouses = "training.type="+str(type)

        if place:
            place = place[0]
            if clouses:
                clouses += " and training.place="+str(place)
            if not clouses:
                clouses = "training.place="+str(place)

        if course_type:
            if clouses:
                clouses += " and training.course_type='"+str(course_type)+"'"
            if not clouses:
                clouses = "training.course_type='"+str(course_type)+"'"

        if participation_type:
            if clouses:
                clouses += " and training.participation_type='"+str(participation_type)+"'"
            if not clouses:
                clouses = "training.participation_type='"+str(participation_type)+"'"

        if reference:
            if clouses:
                clouses += " and training.reference='"+str(reference)+"'"
            if not clouses:
                clouses = "training.reference='"+str(reference)+"'"

        if training_eval:
            if clouses:
                clouses += " and training.training_eval='"+str(training_eval)+"'"
            if not clouses:
                clouses = "training.training_eval='"+str(training_eval)+"'"

        if location:
            if clouses:
                clouses += " and training.location='"+str(location)+"'"
            if not clouses:
                clouses = "training.location='"+str(location)+"'"

        if state:
            if clouses:
                clouses += " and training.state='"+str(state)+"'"
            if not clouses:
                clouses = "training.state='"+str(state)+"'"

        if company_id:
            company_id = company_id[0]
            if clouses:
                clouses += " and training.company_id="+str(company_id)
            if not clouses:
                clouses = "training.company_id="+str(company_id)

        if start_date:
            if clouses:
                clouses += " and training.start_date>='"+str(start_date)+"'"
            if not clouses:
                clouses = "training.end_date<='"+str(start_date)+"'"

        if end_date:
            if clouses:
                clouses += " and training.start_date<='"+str(end_date)+"' and training.end_date>='"+str(end_date)+"'"
            if not clouses:
                clouses = "training.start_date<='"+str(end_date)+"' and training.end_date<='"+str(end_date)+"'"
        if job_id:
            job_id = job_id[0]
            if clouses:
                clouses += " and emp.job_id="+str(job_id)
            if not clouses:
                clouses = "emp.job_id="+str(job_id)

            who_not_take_clouses = " job_id="+str(job_id)
        
        if degree_id:
            degree_id = degree_id[0]
            if clouses:
                clouses += " and emp.degree_id="+str(degree_id)
            if not clouses:
                clouses = "emp.degree_id="+str(degree_id)
            
            if who_not_take_clouses:
                who_not_take_clouses += " and degree_id="+str(degree_id)
            if not who_not_take_clouses:
                who_not_take_clouses = " degree_id="+str(degree_id)

        readable_emp_ids = self.pool.get('hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in"+str(readable_emp_ids)
            if not clouses:
                clouses = "emp.in in"+str(readable_emp_ids) 
            
            if who_not_take_clouses:
                who_not_take_clouses += " and emp.id in "+str(readable_emp_ids)
            if not who_not_take_clouses:
                who_not_take_clouses = " emp.id in "+str(readable_emp_ids)

        query = """select training.state,training.reference,training.training_eval,
                    training.participation_type,training.course_type,training.location,
                    training.start_date,training.end_date ,cat.name as type_name, 
                    place.name as place_name,emp.otherid,emp.name_related,
                    deg.name as deg_name,job.name as job_name 
                    from hr_military_training training 
                    left join hr_employee emp on (training.employee_id=emp.id) 
                    left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                    left join hr_job job on(job.id = emp.job_id) 
                    left join hr_military_training_category cat on(cat.id = training.type) 
                    left join hr_military_training_place place on(place.id = training.place)
                    """
        if who_not_take:
            query = "select employee_id from hr_military_training training left join hr_employee emp on (training.employee_id=emp.id) left join hr_salary_degree deg on (emp.degree_id=deg.id)  left join hr_job job on(job.id = emp.job_id) "

        if clouses:
            query += "where "+clouses
        query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"
        self.cr.execute(query)
        res = self.cr.dictfetchall()

        if who_not_take:
            in_emps = [x['employee_id'] for x in res]
            in_emps += in_emps
            if in_emps:
                in_emps = tuple(in_emps)
                query = """select emp.otherid,emp.name_related,
                            deg.name as deg_name,job.name as job_name  
                            from hr_employee emp 
                            left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                            left join hr_job job on(job.id = emp.job_id) 
                            where emp.state='approved' and emp.id not in """+str(in_emps)
                if who_not_take_clouses:
                    query += "and "+ who_not_take_clouses
                query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"
            if not in_emps:
                query = """select emp.otherid,emp.name_related,
                            deg.name as deg_name,job.name as job_name  
                            from hr_employee emp 
                            left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                            left join hr_job job on(job.id = emp.job_id) 
                            where emp.state='approved' """
                if who_not_take_clouses:
                    query += "and "+ who_not_take_clouses
                query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"

            self.cr.execute(query)
            res = self.cr.dictfetchall()





        

        
       

        #print "......................domain",query,res

        


        self.all_data = res
        
            
        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _get_count(self):
        self.count = self.count + 1
        return self.count


report_sxw.report_sxw('report.hr.training.report', 'hr.employee',
                      'addons/hr_custom_military/report/training_report.mako', parser=training, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
