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
# Class building insurance report
#----------------------------------------
class building_insurance_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(building_insurance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line1':self._getdata1,
        })
    
    def _getdata1(self,data):
        date_from= data['form']['date_from']
        date_to= data['form']['date_to']
        building_id= data['form']['building_id']
        state= data['form']['state']
        insurance_obj = self.pool.get('building.insurance')
        insurance_line_obj = self.pool.get('building.insurance.line')
        domain = [('date','>=', date_from),('date','<=', date_to)]
        if building_id:
            insurance_line_ids = insurance_line_obj.search(self.cr, self.uid, [('building_id','=',building_id[0])])
            insurance_ids = insurance_line_ids and [line.insurance_id.id for line in insurance_line_obj.browse(self.cr, self.uid,insurance_line_ids)] or []
            domain.append(('id','in',tuple(insurance_ids)))
        if state :
            if state =='completed':
                domain.append(('state','=','done'))
            else: 
                domain.append(('state','!=','done'))
                              
        insurance_ids = insurance_obj.search(self.cr, self.uid, domain, order="id")
        return insurance_obj.browse(self.cr,self.uid,insurance_ids)
    
report_sxw.report_sxw('report.building_insurance.report', 'building.insurance', 'addons/building_management/report/building_insurance_report.rml' ,parser=building_insurance_report,header=False)
