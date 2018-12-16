# coding: utf-8
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from datetime import datetime
from openerp import SUPERUSER_ID


class hall_calendar_late_report(report_sxw.rml_parse):
    """ To manage hall calendar late report """

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(hall_calendar_late_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line': self._getdata,
        })
    def get_date_time(self,str):
        return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")
    def get_date(self,str):
        return datetime.strptime(str, "%Y-%m-%d")
    def _getdata(self, data):
        """
        Function finds hall calendar report data.

        @return: List of dictionary to  service report data
        """
        log_contract_obj = self.pool.get('fleet.vehicle.log.contract')

        date = data['form']['date']
        department = data['form']['department']
        user = data['form']['user']
        halls_ids = data['form']['halls_ids']

        date_to = data['form']['date_to']
        

        if department:
            department = department[0]
        if not department:
            department = self.pool.get('hr.department').search(self.cr, SUPERUSER_ID, [],context=self.context)
        
        if not halls_ids:
            halls_ids = self.pool.get('fleet.service.type').search(self.cr, SUPERUSER_ID, [],context=self.context)
        #start_date = datetime.strptime(str(date) , "%Y-%m-%d")
        #end_date = datetime.strptime(str(date), "%Y-%m-%d")
        start_date = date + " 00:00:00"
        end_date = date + " 23:59:59"
        if date_to:
            end_date = date_to + " 23:59:59"
        resource_calendar = self.pool.get('resource.calendar.attendance')
        hall_obj = self.pool.get('service.hall_availability')
        hall_ids = hall_obj.search(self.cr, SUPERUSER_ID, [(
            'date_start', '>=', start_date), ('date_stop', '<=', end_date), ('department_id', '=', department), ('hall_id', 'in', halls_ids)])
        lines = []
        for line in hall_obj.browse(self.cr, SUPERUSER_ID, hall_ids, context=self.context):
            if line.contract_id.state not in ['open']:
                continue
            #attendance.dayofweek
            attendance_ids = resource_calendar.search(self.cr, SUPERUSER_ID, [('dayofweek','=',str(self.get_date_time(line.date_start).weekday()) )])
            attendance = resource_calendar.browse(self.cr, SUPERUSER_ID, attendance_ids)

            calendar = filter(lambda x : self.get_date_time(x.date_from+ " 00:00:00") <= self.get_date_time(line.date_start) ,attendance)
            calendar = calendar and max( calendar, key = lambda x: self.get_date(x.date_from) ) or False
            if calendar:
                hour_to = int(calendar.hour_to)
                min_to = calendar.hour_to - hour_to
                hour_to *= 60.0
                min_to = 100 * int(min_to) / 60
                min_to += hour_to

                over_out = (self.get_date_time(line.date_stop).hour * 60.0) + self.get_date_time(line.date_stop).minute - min_to
                if over_out > 0:
                    lines.append(line)
            if not calendar:
                lines.append(line)
        
        return lines

report_sxw.report_sxw('report.hall_availability_late.report', 'service.hall_availability',
                      'addons/service/report/hall_calendar_late.rml', parser=hall_calendar_late_report, header=False)
