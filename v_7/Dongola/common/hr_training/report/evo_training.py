import time
import re
import pooler
from report import report_sxw
import calendar
import datetime


class evo_training(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(evo_training, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'dept' :self._get_dept,
            'count':self.count_emps,

      
           }) 
        self.context = context
        self.total = 0
        self.final_total = 0

    def get_child_dept(self,cr,uid,dept_id,context=None):
        department_obj = self.pool.get('hr.department')
        reads = department_obj.read(self.cr, self.uid, [dept_id], ['id','child_ids'], context=context)
        child_ids=[]
        for record in reads:
           if record['child_ids']:
              child_ids=record['child_ids']
              for child in record['child_ids']:
                 child_ids+=self.get_child_dept(self.cr,self.uid,child,context=context)
        return child_ids
###############################department#################################
    def count_emps(self,child_ids,data):
       emp_ids = self.pool.get('hr.employee.training.line').search(self.cr, self.uid, [('start_date','>=',data['From']),('start_date','<=',data['to']),
                                                                            ('department_id','in',child_ids),('type','=','hr.approved.course')], context=self.context)
       return len(emp_ids)
##############################################################################


    def _get_dept(self,data):
       top_res=[]
       ap_count=0
       cu_count=0
       sums=0
       sumss=0
       sumsss=0
       avg=0
       no=0
       if data['department_ids']:
          for b in  data['department_ids']:
 
            no+=1
            child_ids= []
            self.cr.execute(''' SELECT name as nn from hr_department where id=%s'''%b)
            do = self.cr.dictfetchall()
            cu_count=0
            child_ids=self.get_child_dept(self.cr,self.uid,b,{})
            child_ids+=[b]
            cu_count=self.count_emps(child_ids ,data)
            sumss+=cu_count
            data_dec={'name': do[0]['nn'],'cu_count':cu_count,'no':no,'sumss':sumss,}

            top_res.append(data_dec)
       return top_res
####################################################################

report_sxw.report_sxw('report.evo_training', 'hr.employee.training', 'addons/hr_training/report/evo_training.rml' ,parser=evo_training ,header="True")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
