#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Fuel Request report  
# Report to print Fuel Request in a certain period of time, according to certain options
# 1 - Department
# 2 - States       ----------------------------------------------------------------------------------------------------------------
class fuel_request_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fuel_request_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
#            'line4':self._getcount,
#            'line5':self._getcount_done,
#            'line6':self._getcount_notdone,

        })



    def _getdata(self,data):
        date_from= data['form']['Date_from']
        date_to= data['form']['Date_to']
        state = data['form']['state']
        purpose = data['form']['purpose']
        car = data['form']['car_id']
        department = data['form']['department']
        gategory = data['form']['gategory']
	company = data['form']['company_id']
        where_condition = ""
        where_condition += state and " and hs.state='%s'"%state or ""
        where_condition += purpose and " and hs.purpose='%s'"%purpose or ""
        where_condition += car and " and hs.car_id=%s"%car[0] or ""
        where_condition += department and " and hs.department=%s"%department[0] or ""
        where_condition += gategory and " and hs.gategory='%s'"%gategory or ""
        where_condition += company and " and hs.company_id=%s"%company[0] or ""
                    
        self.cr.execute('''
                select hs.name as request_name,
                hs.id as id ,
                hs.date as request_date ,
                hs.state as state,
                hr.name as dept , 
                hs.notes as notes,
                pr.license_plate as car_name,
                hs.purpose as purpose ,
		hs.purpose as gategory ,
                pt.name as product_name,
                pt.product_qty as qty ,
                u.name uom                
                from fuel_request hs
                left join hr_department hr on (hs.department = hr.id)
                left join fuel_request_lines pt on (hs.id=pt.fuel_id)
                left join product_uom u on (u.id=pt.product_uom)
                left join fleet_vehicle pr on (hs.car_id = pr.id)
                where
                (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.date,'YYYY-mm-dd')<=%s)
                '''  + where_condition + " order by hs.name",(date_from,date_to)) 
        
        res = self.cr.dictfetchall()            
        return res

report_sxw.report_sxw('report.fuel.request.report.report', 'fuel.request', 'addons/fuel_management/report/fuel_request_report.rml' ,parser=fuel_request_report,header=False)
