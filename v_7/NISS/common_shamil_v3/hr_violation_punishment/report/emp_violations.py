import time
from report import report_sxw
import calendar
import datetime
import pooler

class emp_violations(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(emp_violations, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'lines2':self._getShop,
            
        })
    
    def _getShop(self,emp_id):
      
        self.cr.execute("select m.violation_date AS date,v.name AS violation,p.name AS punishment,m.penalty_amount AS penalty FROM hr_employee_violation AS m left join hr_employee e on (m.employee_id=e.id)  left join hr_punishment AS p on (m.punishment_id=p.id) left join hr_violation AS v on (m.violation_id=v.id) where e.id=%s",(emp_id,)) 
        res = self.cr.dictfetchall()
        return res

    


report_sxw.report_sxw('report.emp_violations', 'hr.employee.violation', 'hr_violation_punishment/report/emp_violations.rml' ,parser=emp_violations,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
