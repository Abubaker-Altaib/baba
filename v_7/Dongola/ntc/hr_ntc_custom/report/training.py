import time
import datetime
import mx
from openerp.report import report_sxw


class course_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(course_form, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'time1': self._get_time,
            'course':self._get_course,
            'line':self._get_data,
            'user':self._get_user,
           })
        self.year = int(time.strftime('%Y'))

    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name

    def _get_course(self,data):
        training_category_obj = self.pool.get('hr.training.category')
        training_category_id = data['training_category_id']
        training_category_id = not training_category_id and training_category_obj.browse(self.cr,self.uid,[]) or training_category_id
        self.cr.execute(" select distinct c.id as course_id , c.name as course_name "\
                        "from hr_training_course as c "\
                        "where c.training_category_id in %s",(tuple(training_category_id),))
        res = self.cr.dictfetchall()
        return res

    def _get_data(self, data,course_id):
        date1 = data['date_from']
        date2 = data['date_to']
        side = data['type'] == '3' and 'inside' or 'outside'
        self.year = date1 and mx.DateTime.Parser.DateTimeFromString(date1).year or self.year
        res=[]
        if date1 and date2:
            self.cr.execute(" select distinct emp.marital as marital, "\
            "t.end_date as end,"\
            "t.start_date as start,"\
            "c.name as country,"\
            "t.course_type as type,"\
            "t.location as location,"\
            "res.name as name " \
            "from hr_employee_training t "\
            "left join hr_employee_training_line line on (line.training_employee_id=t.id) "\
            "left join  hr_employee emp on (emp.id=line.employee_id) "\
            "left join hr_job jop on (jop.id=emp.job_id) "\
            "left join resource_resource res on (res.id=emp.resource_id) "\
            "left join hr_training_course cou on(cou.id=t.course_id) "\
            "left join res_country c on(t.country_id=c.id) "\
            "where t.course_id = %s and "\
            "t.type ='hr.approved.course' and t.training_place = %s and "\
            "t.start_date >= %s and t.end_date <= %s ",(tuple([course_id]),side,date1,date2))
        elif date1 and not date2:
            self.cr.execute(" select distinct emp.marital as marital, "\
            "t.end_date as end,"\
            "t.start_date as start,"\
            "c.name as country,"\
            "t.course_type as type,"\
            "t.location as location,"\
            "res.name as name " \
            "from hr_employee_training t "\
            "left join hr_employee_training_line line on (line.training_employee_id=t.id) "\
            "left join  hr_employee emp on (emp.id=line.employee_id) "\
            "left join hr_job jop on (jop.id=emp.job_id) "\
            "left join resource_resource res on (res.id=emp.resource_id) "\
            "left join hr_training_course cou on(cou.id=t.course_id) "\
            "left join res_country c on(t.country_id=c.id) "\
            "where t.course_id = %s and "\
            "t.type ='hr.approved.course' and t.training_place = %s and "\
            "t.start_date >= %s",(tuple([course_id]),side,date1))
        elif date2 and not date1:
            self.cr.execute(" select distinct emp.marital as marital, "\
            "t.end_date as end,"\
            "t.start_date as start,"\
            "c.name as country,"\
            "t.course_type as type,"\
            "t.location as location,"\
            "res.name as name " \
            "from hr_employee_training t "\
            "left join hr_employee_training_line line on (line.training_employee_id=t.id) "\
            "left join  hr_employee emp on (emp.id=line.employee_id) "\
            "left join hr_job jop on (jop.id=emp.job_id) "\
            "left join resource_resource res on (res.id=emp.resource_id) "\
            "left join hr_training_course cou on(cou.id=t.course_id) "\
            "left join res_country c on(t.country_id=c.id) "\
            "where t.course_id = %s and "\
            "t.type ='hr.approved.course' and t.training_place = %s and "\
            "t.end_date <= %s ",(tuple([course_id]),side,date2))
        else:
            self.cr.execute(" select distinct emp.marital as marital, "\
            "t.end_date as end,"\
            "t.start_date as start,"\
            "c.name as country,"\
            "t.course_type as type,"\
            "t.location as location,"\
            "res.name as name " \
            "from hr_employee_training t "\
            "left join hr_employee_training_line line on (line.training_employee_id=t.id) "\
            "left join  hr_employee emp on (emp.id=line.employee_id) "\
            "left join hr_job jop on (jop.id=emp.job_id) "\
            "left join resource_resource res on (res.id=emp.resource_id) "\
            "left join hr_training_course cou on(cou.id=t.course_id) "\
            "left join res_country c on(t.country_id=c.id) "\
            "where t.course_id = %s and "\
            "t.type ='hr.approved.course' and t.training_place = %s ",(tuple([course_id]),side))

        
        res=self.cr.dictfetchall()

        return res

        
    def _get_time(self):
        return self.year

report_sxw.report_sxw('report.course.outside', 'hr.employee.training', 'addons/hr_ntc_custom/report/training.rml' ,parser=course_form ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
