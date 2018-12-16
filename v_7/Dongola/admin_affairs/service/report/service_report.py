#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from datetime import datetime

class service_report(report_sxw.rml_parse):
    """ To manage service report """

    def __init__(self, cr, uid, name, context):
        super(service_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })

    def _getdata(self,data):
        """
        Function finds service report data.
 
        @return: List of dictionary to  service report data
        """
        log_contract_obj = self.pool.get('fleet.vehicle.log.contract')
        
        date_from= data['form']['date_from']
        date_to= data['form']['date_to']
        state = data['form']['state']
        category = data['form']['category']
        service_type = data['form']['service_type']
        department = data['form']['department']
        partner = data['form']['partner_id']

        start_date = datetime.strptime(str(date_from), "%Y-%m-%d")
        end_date = datetime.strptime(str(date_to), "%Y-%m-%d")

        domain=[]
        cost_sum = 0.0
        if department:
            domain +=[('department_id','=',department[0])]
        if partner :
            domain +=[('insurer_id','=',partner[0])]
        if service_type :
            domain +=[('cost_subtype_id','=',service_type[0])]
        if category :
            domain +=[('cost_subtype_id.category','=',category)]
        if state == 'executed':
            domain+=[('state','in',['open','toclose','closed'])]
            
        cont_ids = log_contract_obj.search(self.cr, self.uid, domain)
        val = []
 
        for cont in log_contract_obj.browse(self.cr, self.uid, cont_ids):
            price = 0.0
            start = datetime.strptime(str(cont.start_date), "%Y-%m-%d")
            
            end = datetime.strptime(str(cont.expiration_date), "%Y-%m-%d")
            if ((start.month >= start_date.month) and (start_date.month <= end.month) and (start.month <= end_date.month) and (end_date.month >= end.month)):
                services =[]
                for cost in cont.cost_ids: 
                    services.append({'cost_sub' : cost.cost_subtype_id.name,
                                     'quantity' : cost.quantity,
                                     'amount_ser' : cost.amount,})
                price = cont.total_cost
                cost_sum =cont.total_cost
                val.append({
                            'name':cont.name,
                            'date':cont.date,
                            'dept':cont.department_id.name,
                            'state':cont.state,
                            'amount':cont.amount,
                            'cost_g':cont.cost_generated,
                            'cost_f':cont.cost_frequency,
                            'services':services,
                            'total_cost':  price,
                            'cost_sum':cost_sum,
                            'contract_cost_sub_type':cont.cost_subtype_id.name, 
                            'category':cont.cost_subtype_id.category, 
                            })
                services =[]
        lines = []
        lin = []
        exist = []
        for cat in val:
            cost = 0
            lin = []
            if not cat["category"] in exist:
                exist.append(cat["category"])
                service_exist=[]
                for ser in val:
                    lin_ser = []
                    if ser["category"] != cat["category"]:
                        continue
                    if ser['contract_cost_sub_type'] in service_exist:
                        continue
                    
                    service_exist.append(ser['contract_cost_sub_type'])
                    sum = 0
                    for line in val:
                        if line["contract_cost_sub_type"] == ser["contract_cost_sub_type"] :
                            sum += line["cost_sum"]
                            line["cost_sum"]=sum
                            lin_ser.append(line)
                    lin.append(lin_ser)
                lines.append(lin)
        return lines

report_sxw.report_sxw('report.service.report', 'fleet.vehicle.log.contract', 'addons/service/report/service_report.rml' ,parser=service_report,header=False)

