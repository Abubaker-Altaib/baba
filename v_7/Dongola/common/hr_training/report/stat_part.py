import time
import re
import pooler
from report import report_sxw
import calendar
import datetime



class stat_part(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(stat_part, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'center': self._get_center,
            'course': self._get_course,
            'total': self._get_total,
        })
        self.context = context
        self.total = 0
        self.final_total = 0
      globals()['deps']=[]
      
#####################################################################################

      def _get_center(self, data):
           date1 = data['from']
           date2 = data['to']
           course_ids = self.pool.get('hr.employee.training').search(self.cr, self.uid, [('partner_id','!=',False),('start_date','>=',date1),('start_date','<=',date2)], context=self.context)
           return set([p['partner_id'] for p in self.pool.get('hr.employee.training').read(self.cr, self.uid, course_ids, ['partner_id'], context=self.context)]) 



      def _get_course(self, data, partner_id):
        date1 = data['from']
        date2 = data['to']
        no=0
        self.final_total = 0
        top_res=[]
        self.cr.execute(''' select distinct course_id.id as course_id , course_id.name as course_name  
            from hr_training_course as course_id,res_partner ,
            hr_employee_training as tr
            where tr.type ='hr.approved.course' and tr.course_id =course_id.id and
            res_partner.id = tr.partner_id and
            tr.start_date >=%s and
            tr.start_date <=%s and  tr.partner_id =%s''' ,(date1,date2,partner_id))
        res=self.cr.dictfetchall()
        for c in res :
            course_ids = self.pool.get('hr.employee.training').search(self.cr, self.uid, [('type','=','hr.approved.course'),('partner_id','=',partner_id),('start_date','>=',date1),('start_date','<=',date2),('course_id' ,'=',c['course_id'])], context=self.context)
            #department_ids = self.pool.get('hr.employee.training.department').search(self.cr, self.uid, [('employee_training_id','in',course_ids)], context=self.context)
            #candidate = self.pool.get('hr.employee.training.department').browse(self.cr, self.uid, department_ids, context=self.context)
            no+=1
            #self.total = sum(ca.candidate_no for ca in candidate)
            self.total = self.pool.get('hr.employee.training').read(self.cr, self.uid, course_ids, ['line_ids'])
            self.total = self.total[0]
            self.total = self.total['line_ids'] and self.total['line_ids'] or []
            self.total = len(self.total)
            #for b in candidate :
                #self.total = sum(ca.candidate_no for ca in candidate)
            dic ={ 'course':c['course_name'], 'no':no ,'total' :self.total}
            top_res.append(dic)
            #print ">>>>>>>>>top_res" ,top_res
            self.final_total=self.total+self.final_total

        return top_res
      def _get_total(self):
        return [self.final_total]



      
report_sxw.report_sxw('report.stat_report', 'hr.employee.training', 'addons/hr_training/report/stat_part.rml' ,parser=stat_part ,header= True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
