# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from datetime import datetime

class service_cars_fuel_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(service_cars_fuel_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line':self._getdata,
        })

    def _getdata(self, data):
        """
        the data that came from the report wizard.

        @return: dictionary of report data
        """
        lines = []
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        department_ids = data['form']['department_ids']

        vehicles_ids = self.pool.get('fleet.vehicle').search(self.cr, self.uid,\
            [('department_id', 'in', department_ids)], context=self.context)

        fuel_qty_line_obj = self.pool.get('fuel.qty.line')

        sdate = datetime.strptime(start_date, "%Y-%m-%d")
        syear = sdate.year
        smonth = sdate.month
        edate = datetime.strptime(end_date, "%Y-%m-%d")
        eyear = edate.year
        emonth = edate.month

        fuel_qty_line_ids = fuel_qty_line_obj.search(self.cr, self.uid,\
        [('vehicles_id', 'in', vehicles_ids)], context=self.context)



        counter = 1
        for qty_line in fuel_qty_line_obj.browse(self.cr, self.uid, \
            fuel_qty_line_ids, context=self.context):
            current_m = int(qty_line.month)
            current_y = int(qty_line.year)
            start = current_m >= smonth and current_y >= syear
            end = current_m <= emonth and current_y <= eyear
            if start and end:
                line = {'type':str(counter)+" : "+\
                qty_line.vehicles_id.type.name}
                line['vehicle_no'] = qty_line.vehicles_id.vin_sn
                line['spent'] = qty_line.spent_qty
                line['counter_no'] = str(qty_line.vehicles_id.odometer)+" "+\
                qty_line.vehicles_id.odometer_unit
                line['date'] = qty_line.month+"/"+qty_line.year
                lines.append(line)
                counter += 1
        return lines


report_sxw.report_sxw('report.service_cars.report', 'fuel.qty.line',\
    'addons/fuel_management/report/service_cars_fuel_report.rml',\
    parser=service_cars_fuel_report, header=True)
