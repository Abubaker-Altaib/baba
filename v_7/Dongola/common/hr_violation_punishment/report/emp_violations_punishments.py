import time
from report import report_sxw
import calendar
import datetime
import pooler
from openerp.osv import fields, osv, orm

class emp_violations_punishments(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(emp_violations_punishments, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getShop,
            
        })
    
   
    def _getShop(self,data):


        self.cr.execute("select r.name as employee,m.violation_date AS date,v.name AS violation,p.name AS punishment,m.penalty_amount AS penalty FROM hr_employee_violation AS m left join hr_employee e on (m.employee_id=e.id) left join resource_resource AS r on (e.resource_id=r.id) left join hr_punishment AS p on (m.punishment_id=p.id) left join hr_violation AS v on (m.violation_id=v.id) where to_char(m.violation_date,'YYYY')='%s' and to_char(m.violation_date,'mm')='%s'" %(str(data['year']),str(data['month']))) 
        
        res = self.cr.dictfetchall()
        if not res:
           raise osv.except_osv(('Sorry'), ('Their is No Violation in this Month'))
        return res



    
report_sxw.report_sxw('report.emp.violations.punishments','hr.employee.violation',
'hr_violation_punishment/report/emp_violations_punishments.rml',parser=emp_violations_punishments)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
