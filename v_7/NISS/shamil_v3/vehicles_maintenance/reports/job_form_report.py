# -*- coding: utf-8 -*-

from report import report_sxw
from tools.translate import _
from openerp.osv import osv, fields, orm
import time
import datetime



class job_form_report(report_sxw.rml_parse):
    '''
    @return maintenance job data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('maintenance.job').browse(self.cr , self.uid , [self.context['active_id']]) :
            if i.state not in ('recieved','done'):
                res = {
                    'ref' : i.ref ,
                    'vehicle_id' : i.vehicle_id ,
                    'job_date' : i.start_datetime ,
                    'date' :datetime.date.today().strftime('%Y-%m-%d'),
                    'eng_ids': [e.name for e in i.eng_ids],
                    'lines':self.get_lines(i.spares_ids),
                    'driver': i.vehicle_id.employee_id or i.vehicle_id.driver
                }
                print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>res",res
                time=datetime.datetime.time(datetime.datetime.now()).strftime('%H:%M:%S')
                date=datetime.date.today().strftime('%Y-%m-%d')
                report_log_temp = str(_("Printed in ").encode('utf-8')+ date + "  "+time+"\n")
                if i.report_log:
                    report_log=str(i.report_log.encode('utf-8'))+"\n".encode('utf-8')+report_log_temp
                else:
                    report_log=report_log_temp
                self.pool.get('maintenance.job').write(self.cr , self.uid , [self.context['active_id']],{'report_log': report_log})
            else:
                raise osv.except_osv(_('ValidateError'), _("This report can't Printed in Spares Recieved or Done State"))
        return res

    def get_lines(self , objs):
        line_data = []
        for line in objs:
            data = {
                'product_id' : line.product_id.name ,
                'quantity' : line.quantity,
                'description' : line.product_id.description  or "",
            }
            line_data.append(data)
        return line_data

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(job_form_report, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)

report_sxw.report_sxw('report.maintenance_job_report','maintenance.job','addons/vehicles_maintenance/reports/job_form.mako',parser=job_form_report,header=False)
