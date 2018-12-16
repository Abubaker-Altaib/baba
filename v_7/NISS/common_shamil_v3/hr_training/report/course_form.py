import time
import re
import pooler
from report import report_sxw
import calendar
import datetime


class course_form(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(course_form, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'place':self._get_place,
            'course':self._get_course,
            'total':self._get_total,
           


      
           }) 
        self.context = context
        self.total = 0
        self.final_total = 0

      def _get_place(self):
          self.cr.execute(''' select distinct training_place from hr_employee_training as tr where tr.type ='hr.approved.course' ''')
          res=self.cr.dictfetchall()
          return res

      def _get_course(self, data,training_place):
        date1 = data['From']
        date2 = data['to']
        no=0
        self.final_total = 0
        top_res=[]
        self.cr.execute(''' select distinct course_id.id as course_id , course_id.name as course_name
            from hr_training_course as course_id,
            hr_employee_training as tr
            where tr.course_id =course_id.id and
            tr.type ='hr.approved.course' and
            tr.training_place =%s and
            tr.start_date >=%s and
            tr.start_date <=%s  group by course_id.id ,course_id.name''' ,(training_place['training_place'] ,date1,date2))
        res=self.cr.dictfetchall()
        for c in res :
            course_ids = self.pool.get('hr.employee.training').search(self.cr, self.uid, [('start_date','>=',date1),('start_date','<=',date2) ,('course_id' ,'=',c['course_id']),('training_place' ,'=', training_place['training_place'])], context=self.context)
            department_ids = self.pool.get('hr.employee.training.department').search(self.cr, self.uid, [('employee_training_id','in',course_ids)], context=self.context)
            candidate = self.pool.get('hr.employee.training.department').browse(self.cr, self.uid, department_ids, context=self.context)
            no+=1
            self.total = sum(ca.candidate_no for ca in candidate)
            #for b in candidate :
                #self.total = sum(ca.candidate_no for ca in candidate)
            dic ={  'course':c['course_name'], 'no':no ,'total' :self.total}
            top_res.append(dic)
            #print ">>>>>>>>>top_res" ,top_res
            self.final_total=self.total+self.final_total

        return top_res

      def _get_total(self):
        return [self.final_total]      

report_sxw.report_sxw('report.course_form', 'hr.employee.training', 'addons/hr_training/report/course_form.rml' ,parser=course_form ,header="True")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
