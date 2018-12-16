# -*- coding: utf-8 -*-

from report import report_sxw
from tools.translate import _
from openerp.osv import osv, fields, orm
import time
import datetime



class insurance_form_report(report_sxw.rml_parse):
    '''
    @return insurance data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('fleet.vehicle.log.contract').browse(self.cr , self.uid , [self.context['active_id']]) :
            insurance_type = ' '
            if i.category != 'insurance':
                raise osv.except_osv(_('ValidateError'), _("This report can Printed Only From Insurance."))
            else:
                if i.insurance_type == 'part':
                    insurance_type = u'طرف ثالث'
                else:
                    insurance_type = u'شامل'
                res = {
                    'ref' : i.name ,
                    'insurance_date' :datetime.datetime.strptime(i.date,"%Y-%m-%d %H:%M:%S").date() ,
                    'start_date' : i.start_date ,
                    'expiration_date' : i.expiration_date ,
                    'date' :datetime.date.today().strftime('%Y-%m-%d'),
                    'insurance_type': insurance_type,
                    'amount':i.amount,
                    'insurer_id':i.insurer_id.name or " ",
                    'purchaser_id':i.purchaser_id.name or " ",
                    'lines':self.get_lines(i.line_ids, [i.id]),
                }
                #time=datetime.datetime.time(datetime.datetime.now()).strftime('%H:%M:%S')
                #date=datetime.date.today().strftime('%Y-%m-%d')
        return res

    def get_lines(self , objs, ids):
        line_data = []
        line_ids = self.pool.get('fleet.vehicle.log.contract.line').search(self.cr , self.uid, [('fleet_contract_id','=',ids[0])])
        '''for line in objs:
            data = {
            'vin_sn':line.vehicle_id.vin_sn,
            'machine_no':line.vehicle_id.machine_no,
            'type':line.vehicle_id.type.name,
            'model':line.vehicle_id.model_id.modelname,
            'year':line.vehicle_id.year or " ",
            'amount' :line.amount,
            }
            line_data.append(data)'''

        if line_ids:

            self.cr.execute("SELECT fleet.vin_sn as vin_sn, fleet.machine_no as machine_no, fleet.year as year, "\
                                "model.name AS model, cat.name as type, line.amount as amount "\
                                "FROM fleet_vehicle_log_contract_line line " \
                                "left join fleet_vehicle fleet ON (line.vehicle_id = fleet.id) "\
                                "left join fleet_vehicle_model model ON (fleet.model_id = model.id) "\
                                "left join vehicle_category cat ON (fleet.type = cat.id) "\
                                "WHERE line.id in %s " \
                                "order by fleet.year desc", (tuple(line_ids),) )  

            line_data = self.cr.dictfetchall()
        return line_data

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(insurance_form_report, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)

report_sxw.report_sxw('report.insurance_form_report','fleet.vehicle.log.contract','addons/admin_affairs/report/insurance_form.mako',parser=insurance_form_report,header=True)
