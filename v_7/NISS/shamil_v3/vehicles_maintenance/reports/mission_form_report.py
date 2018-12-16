# -*- coding: utf-8 -*-

from report import report_sxw
import time
import datetime



class mission_form_report(report_sxw.rml_parse):
    '''
    @return exchange.order data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('exchange.order').browse(self.cr , self.uid , [self.context['active_id']]) :
            res = {
                'time':datetime.datetime.time(datetime.datetime.now()).strftime('%H:%M:%S'),
                'mission_no' : i.mission_no or " ", 
                'mission_to' : i.mission_distance or "",
                'mission_leader': i.mission_leader or " ",
                'mission_date': i.mission_date or " ",
                'date' :datetime.date.today().strftime('%Y-%m-%d'),
                'lines':self.get_lines(i.order_line),
            }
    	return res

    def get_lines(self , objs):
        line_data = []
        for line in objs:
            data = {
                'product_id' : line.product_id.name ,
                'quantity' : line.product_qty,
                'description' : line.product_id.description  or "",
            }
            line_data.append(data)
        return line_data

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(mission_form_report, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)

report_sxw.report_sxw('report.maintenance_mission_report','exchange.order','addons/vehicles_maintenance/reports/mission_form.mako',parser=mission_form_report,header=False)
