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


class hall_calendar_report(report_sxw.rml_parse):
    """ To manage hall calendar report """

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(hall_calendar_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line': self._getdata,
        })

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

        hall_obj = self.pool.get('service.hall_availability')
        hall_ids = hall_obj.search(self.cr, SUPERUSER_ID, [(
            'date_start', '>=', start_date), ('date_stop', '<=', end_date), ('department_id', '=', department), ('hall_id', 'in', halls_ids)])
        lines = hall_obj.browse(self.cr, SUPERUSER_ID, hall_ids, context=self.context)
        return lines

report_sxw.report_sxw('report.hall_availability.report', 'service.hall_availability',
                      'addons/service/report/hall_calendar.rml', parser=hall_calendar_report, header=False)
