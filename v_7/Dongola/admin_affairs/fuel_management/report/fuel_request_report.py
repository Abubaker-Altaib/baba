#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Fuel Request Report  
# Report to print Fuel Request in a certain period of time, according to certain options
# 1 - Department
# 2 - States       ----------------------------------------------------------------------------------------------------------------
class fuel_request_report(report_sxw.rml_parse):
    """ To manage fuel request report """

    def __init__(self, cr, uid, name, context):
        self.total={'total':0,'unit':''}
        super(fuel_request_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'sums':self._getdata2,
        })
        self.context=context

    def _getdata(self,data):
        """
        Function finds fuel request data.
 
        @return: List of dictionary to  fuel request data.
        """
        date_from= data['form']['Date_from']
        date_to= data['form']['Date_to']
        state = data['form']['state']
        purpose = data['form']['purpose']
        car = data['form']['car_id']
        department = data['form']['department']
        company = data['form']['company_id']
        plan_typ = data['form']['plan_type']

        log_fuel_obj= self.pool.get('fleet.vehicle.log.fuel')
        #domain_date =[]
        globals()['total_liter']=0.0
        domain=[('date','>=',date_from),('date','<=',date_to)]
        if state=='done' :
            domain +=[('state','=',state)]
        if purpose :
            domain +=[('purpose','=',purpose)]
        if department :
            domain +=[('department_id','=',department[0])]
        if plan_typ :
            domain +=[('plan_type','=',plan_typ)]
        if car:
            domain +=[('vehicle_id','=',car[0])]
        cont_ids = log_fuel_obj.search(self.cr, self.uid, domain, context=self.context)
        all = log_fuel_obj.browse(self.cr, self.uid, cont_ids, context=self.context)

        uom_obj = self.pool.get('product.uom')
        unit = all and all[0].product_uom.id or ''
        self.total['unit'] = all and all[0].product_uom.name or ''
        for liter in all:
            self.total['total'] += uom_obj._compute_qty(self.cr, self.uid, liter.product_uom.id,liter.liter, unit)
        return all

    def _getdata2(self,data):
        return [self.total]
    
report_sxw.report_sxw('report.fuel.request.report', 'fleet.vehicle.log.fuel', 'addons/fuel_management/report/fuel_request_report.rml' ,parser=fuel_request_report,header=False)












