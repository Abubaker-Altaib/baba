# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
import time
import datetime



class vehicles_sale_form_report(report_sxw.rml_parse):

    
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(vehicles_sale_form_report, self).__init__(cr, uid, name, context)
        record = self.get_record()
        self.localcontext.update(record)

    def get_record(self):
        res = {}
        for i in self.pool.get('vehicle.sale').browse(self.cr , self.uid , [self.context['active_id']]) :
            state = ' '            
            if i.state == 'draft':
                state = u'مبدئي'
            elif i.state == 'confirm':
                state = u'تم البيـع'

            sale_type = ' '            
            if i.sale_type == 'pension':
                sale_type = u'معاشيين'
            elif i.sale_type == 'public':
                sale_type = u'عامة'
            res = {
                'ref' : i.reference,
                'name' : i.name,
                'sale_date' : i.sale_date,
                'date' :datetime.date.today().strftime('%Y-%m-%d'),
                'state': state,
                'type':sale_type,
                'amount_total':i.amount_total,
                'actual_sale_amount_total':i.actual_sale_amount_total,
                'lines':self.get_lines(i.line_id),
            }
            #time=datetime.datetime.time(datetime.datetime.now()).strftime('%H:%M:%S')
            #date=datetime.date.today().strftime('%Y-%m-%d')
        return res

    def get_lines(self , objs):
        line_data = []
        for line in objs:
            data = {
            'vehicle':line.vehicle_id.name,
            'year':line.vehicle_id.year or " ",
            'vin_sn':line.vehicle_id.vin_sn,
            'company_assess' :line.company_assess,
            'committee_assess' :line.committee_assess,
            'agreed_amount' :line.agreed_amount,
            'actual_sale_amount' :line.actual_sale_amount,
            'purchaser' :line.purchaser or " ",
            'card_no' :line.card_no or " ",
            }
            line_data.append(data)
        return line_data


report_sxw.report_sxw('report.vehicles_sale_form', 'vehicle.sale',
                      'addons/admin_affairs/report/vehicles_sale_form.mako', parser=vehicles_sale_form_report, header=True)
