#coding: utf-8
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import mx
import time
import datetime
from dateutil.relativedelta import relativedelta
from report import report_sxw
import dateutil.parser

class rented_cars(report_sxw.rml_parse):
    """ To manage  rented cars report """

    globals()['total_amount']=0.0

    def __init__(self, cr, uid, name, context):
        super(rented_cars, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'total':self._gettotal,
        })

    def _getdata(self,data):
	"""
        Function finds rented cars data.

        @return: List of dictionary to  rented cars data
        """
        month= data['form']['month']
        year= data['form']['year']
        department = data['form']['department_id']
        partner = data['form']['partner_id']

        obj_log_contract=self.pool.get('fleet.vehicle.log.contract')
        obj_cost= self.pool.get('fleet.vehicle.cost')
        domain_date =[]
        globals()['total_amount']=0.0

        if int(month) <= 9 :
            month = '0'+str(month)
        date_min = (datetime.date (int(year), int(month), 1) + relativedelta(day=1)).strftime('%Y-%m-%d')
        date_min = dateutil.parser.parse(date_min)

        date_max = (datetime.date (int(year), int(month), 1) + relativedelta(day=1, months= +1, days= -1)).strftime('%Y-%m-%d')
        date_max = dateutil.parser.parse(date_max)

        domain=[('state','in',['open','to_close','closed'])]
        if department:
            domain +=[('department_id.name','=',department[1])]
        if partner :
            domain +=[('insurer_id.name','=',partner[1])]
        cont_ids = obj_log_contract.search(self.cr, self.uid, domain)

        val = []
        for contracts in obj_log_contract.browse(self.cr, self.uid, cont_ids):
            domain_date=[('contract_id','=',contracts.id),('date','>=',date_min),('date','<=',date_max)]
            v_ids = obj_cost.search(self.cr, self.uid, domain_date)
            amount = sum([record.amount for record in obj_cost.browse(self.cr, self.uid, v_ids)])
            globals()['total_amount'] += amount
            if amount > 0:
                val.append({'contract_name':contracts.name,
                	        'partner':contracts.insurer_id.name,
                            'employee':contracts.driver_id.name,
                            'vehicle':contracts.vehicle_id.name,
                            'license_plate':contracts.vehicle_id.license_plate,
                            'dept':contracts.department_id.name,
                            'amount':amount
                            })
        return val

    def _gettotal(self,data):
	"""
        Function finds the total amount to rented cars.

        @return: value of total amount
        """
        return globals()['total_amount']

report_sxw.report_sxw('report.rented_cars_report', 'fleet.vehicle.log.contract', 'addons/service/report/rented_cars.rml' ,parser=rented_cars , header=False)
