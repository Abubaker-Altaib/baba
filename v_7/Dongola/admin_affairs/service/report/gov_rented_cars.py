#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import osv ,fields
import time
from report import report_sxw


class all_rented_cars(report_sxw.rml_parse):
    """ To manage government rented cars report """

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(all_rented_cars, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'set': self.get_data,
        })
        self.context = context

    def get_data(self,data):
        """
        Function finds rented cars data if cars is government or rented or all cars.
 
        @return: List of browse to  rented cars data
        """
        if data.get('form' , False):
            chosing=data['form']['choose_type']
            owen=()
            if chosing=='government':
               owen=('owned',)
            elif chosing=='rented':
               owen=('rented',)
            elif chosing=='all_car':
               owen=('rented','owned')
        status='active'
        obj_log_contract=self.pool.get('fleet.vehicle.log.contract')
        obj_log_vehicle=self.pool.get('fleet.vehicle')
        v_ids= obj_log_vehicle.search(self.cr, self.uid, [('status','=','active'),('ownership','in',owen)])
        searching_val= obj_log_contract.search(self.cr, self.uid, [('vehicle_id','in',v_ids)])
        return obj_log_contract.browse(self.cr, self.uid, searching_val)

report_sxw.report_sxw('report.gov_rent.report', 'fleet.vehicle.log.contract', 'addons/service/report/gov_rented_cars.rml' ,parser=all_rented_cars , header=False)

