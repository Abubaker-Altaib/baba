import time
from report import report_sxw
import calendar
import datetime
import pooler

class brief_secret_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(brief_secret_report, self).__init__(cr, uid, name, context)
        records = dict()
        records = self.get_record()
        self.localcontext.update({'employees':records})

#------------------------------- line----------------------------------   

    def get_record(self):
        res=[]
        data = self.pool.get('brief.secret.report.wizard').browse(self.cr , self.uid , [self.context['active_id']])[0]
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>data",data
        for emp in data.employee_ids:
            print">>>>>>>>>>>>>>>>>>>>>>>>>>>data.employee_ids",data.employee_ids
            report=self._get_secret_report(emp,data.year)
            if report:
                res.append({
                    'name' : emp.name ,
                    'degree':emp.degree_id.name,
                    'department' : emp.department_id.name,
                    'code' : emp.otherid ,
                    'qual' : self._get_qualification(emp), 
                    'training': self._get_training(emp),
                    'report':self._get_secret_report(emp,data.year),
                })
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>res-get_record",res
        return res

    def _get_qualification(self,emp):
        res=[]
        for qual in emp.qualification_ids:
            res.append({
                'qual_name':qual.emp_qual_id.name,
                'specialization': qual.specialization.name or "",
                'qual_date':qual.qual_date,
                })
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>_get_qualification-res",res
        return res

    def _get_training(self,emp):
        res=[]
        for training in emp.military_training_id:
            res.append({
                'place':training.place.name,
                'type': training.type.name,
                'start_date':training.start_date,
                'end_date':training.end_date,
                })
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>_get_training-res",res
        return res

    def _get_secret_report(self,emp,year):
        res=[]
        secret_obj=self.pool.get('hr.secret.report.process')
        emp_ids = secret_obj.search(self.cr, self.uid, [('employee_id','=',emp.id),('year','>=',year),('state','=','confirmed')])
        for emp in secret_obj.browse(self.cr,self.uid,emp_ids):
            res.append({
                'year':emp.year,
                'direct_final_eval': emp.direct_final_eval,
                'supreme_final_eval':emp.supreme_final_eval,
                'direct_leader_id':emp.direct_leader_id.name or "",
                'supreme_leader_id':emp.supreme_leader_id.name or "",
                'department_id':emp.department_id.name,
                })
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>_get_secret_report-res",res
        return res

report_sxw.report_sxw('report.brief_secret_report', 'hr.secret.report.process', 'addons/hr_secret_report/report/brief_secret_report.rml' ,parser=brief_secret_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
