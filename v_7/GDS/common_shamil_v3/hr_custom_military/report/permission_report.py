# -*- coding: utf-8 -*-

from report import report_sxw
import datetime,time
title = {
    'officer' : unicode('ر.البطاقة', 'utf-8') ,
    'soldier' : unicode('نمرة', 'utf-8'),
}

title2 = {
    'officer' : unicode('1', 'utf-8') ,
    'soldier' : unicode('2', 'utf-8'),
}
class move_permission_report(report_sxw.rml_parse):
    '''
    @return move order data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('hr.holidays').browse(self.cr , self.uid , [self.context['active_id']]) :

           res = {
		  'name': i.employee_id.name ,
                  'company_name': self.pool.get('res.users').browse(self.cr , self.uid , [self.uid])[0].company_id.name or "" ,
                  'depart' : i.employee_id.department_id.name ,
           	  'degree':i.employee_id.degree_id.name ,
           	  'code': i.employee_id.emp_code ,
                  'dest': i.holiday_place or "" ,
                  'return_place': i.return_place or "" ,
                  'source': i.source_place or "" ,
                  'type':'holiday',
                  'struct':i.employee_id.payroll_id.military_type,
                  'days': i.number_of_days_temp ,
                  'road_days': i.road_days ,
                  'start_date': i.date_from,
                  'end_date': i.date_to ,
                  'perm_code': i.holiday_status_id.name,
                  'road_days':i.road_days
		    }
        return res

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(move_permission_report, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)



report_sxw.report_sxw('report.hr_emp_holiday_report','hr.holidays','addons/hr_custom_military/report/hr_employee_permission.mako',parser=move_permission_report,header=False)

class emp_mission_permission_report(report_sxw.rml_parse):
    '''
    @return move order data in dictionary
    '''
    def get_record(self):
      res = {}
      for i in self.pool.get('hr.employee.mission.line').browse(self.cr , self.uid , [self.context['active_id']]) :
          res['name'] = i.employee_id.name
          res['company_name'] = self.pool.get('res.users').browse(self.cr , self.uid , [self.uid])[0].company_id.name or ""
          res['degree'] = i.employee_id.degree_id.name
          res['code'] = i.employee_id.emp_code
          res['dest'] = i.emp_mission_id.mission_id.name or ""
          res['return_place'] = i.emp_mission_id.return_place or ""
          res['source'] = i.emp_mission_id.source or ""
          res['type'] = 'mission',
          res['struct']=i.employee_id.payroll_id.military_type,
          res['days'] = i.emp_mission_id.days
          res['road_days'] = i.emp_mission_id.road_days
          res['start_date'] = i.start_date
          res['end_date'] = i.end_date
          res['perm_code'] = unicode('مأمورية', 'utf-8')
      return res

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(emp_mission_permission_report, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)



report_sxw.report_sxw('report.hr_emp_mission_perm_report','hr.employee.mission.line','addons/hr_custom_military/report/hr_employee_permission_mission.mako',parser=emp_mission_permission_report,header=False)
