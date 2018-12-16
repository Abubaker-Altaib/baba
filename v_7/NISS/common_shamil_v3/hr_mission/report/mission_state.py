
import mx
from report import report_sxw
from osv import osv
from tools.translate import _

import time
import re
import pooler
 
import calendar
import datetime

class mission_state_report(report_sxw.rml_parse):
       _name = 'mission.state.report'
       def __init__(self, cr, uid, name, context):
        super(mission_state_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_emp':self._get_emp,
            'lines':self.get_mission,
               })
                self.context = context
        def get_mission(self,df,dt,state):
            transmission_obj=self.pool.get('hr.employee.mission')
            if state != 'illness':
                transmission_ids=transmission_obj.search(self.cr,self.uid, [('start_date', '>=', df),('end_date', '<=', dt),('state','=',state)],context=self.context)
            elif:
                transmission_ids=transmission_obj.search(self.cr,self.uid, [('start_date', '>=', df),('end_date', '<=', dt),('illness','!=',False)],context=self.context)
            if transmission_ids:

            return res
    
        def _get_emp(self,data):
            #transmission_obj=self.pool.get('hr.employee.mission')
            df = data['form']['start_date']
            dt = data['form']['end_date'] 
            state = data['form']['state']
            if state != 'illness':
                transmission_ids=transmission_obj.search(self.cr,self.uid, [('start_date', '>=', df),('end_date', '<=', dt),('state','=',state)],context=self.context)
            elif:
                transmission_ids=transmission_obj.search(self.cr,self.uid, [('start_date', '>=', df),('end_date', '<=', dt),('illness','!=',False)],context=self.context)
            if transmission_ids:
                self.cr.execute('''SELECT e.employee as code,r.name as emp,p.approve_date as date,
d.name AS degree FROM hr_process_archive AS p 
left join hr_employee AS e on (p.employee_id=e.id) 
left join  resource_resource AS r on (e.resource_id=r.id) 
left join hr_salary_degree AS d on (e.degree_id=d.id)
where 
e.employment_date < p.approve_date and
p.approve_date between %s and %s 
''',(date1,date2)) 
                res = self.cr.dictfetchall()
            return res
      

report_sxw.report_sxw('mission.state.report', 'hr.employee.mission','addons/hr_mission/report/mission_state.rml', parser=mission_state_report, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
