#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from datetime import timedelta,date

#----------------------------------------
# Class building maintenance report
#----------------------------------------
class building_maintenance_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(building_maintenance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })

    def _getdata(self,data):
        date_from= data['form']['date_from']
        date_to= data['form']['date_to']
        building_id= data['form']['building_id']
        maintenance_type = data['form']['maintenance_type']
        partner_id= data['form']['partner_id']
        state= data['form']['state']
        maintenance_obj = self.pool.get('building.maintenance')
        domain = [('date','>=', date_from),('date','<=', date_to)]
        if building_id:
            domain.append(('building_id','=',building_id[0]))
        if state :
            domain.append(('state','=', state))
        if partner_id :
            domain.append(('partner_id','=', partner_id[0]))    
        if maintenance_type:
            domain.append(('maintenance_type','=', maintenance_type[0]))    

        maintenance_ids = maintenance_obj.search(self.cr, self.uid, domain, order="id")
        return maintenance_obj.browse(self.cr,self.uid,maintenance_ids)

    
report_sxw.report_sxw('report.building_maintenance.report', 'building.maintenance', 'addons/building_management/report/building_maintenance_report.rml' ,parser=building_maintenance_report,header=False)
