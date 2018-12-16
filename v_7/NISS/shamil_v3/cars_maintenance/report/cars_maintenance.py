#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw


class car_maintenance(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(car_maintenance, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self._getfault,


        })

    def _getdata(self,data):


        date_from= data['form']['Date_from']
        date_to= data['form']['Date_to']
        data_car = data['form']['car_id']	
        maintenance_type = data['form']['maintenance_type']
        data_state= data['form']['state']
        data_company= data['form']['company_id']
        data_partner= data['form']['partner_id']
        data_department= data['form']['department_id']
        data_product= data['form']['product_id']
        where_condition = ""
        where_condition += maintenance_type and (maintenance_type == 'emergency' and " and r.maintenance_type='emergency'" or "and r.maintenance_type='regular'") or ""
        where_condition += data_state and (data_state == 'completed' and " and r.state= 'done' " or " and r.state != 'done' ") or ""
        where_condition += data_car and " and f.id=%s"%data_car[0] or ""
        where_condition += data_company and " and r.company_id=%s"%data_company[0] or ""
        where_condition += data_partner and " and r.partner_id=%s"%data_partner[0] or ""
        where_condition += data_department and " and r.department_id=%s"%data_department[0] or ""
        where_condition += data_product and " and cf.product_id=%s"%data_product[0] or ""
        self.cr.execute('''
                SELECT 
				  r.id as id ,
				  f.name as vechile_name ,  
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total ,
				  r.state as state , 
				  res.name as driver_name ,
				  h.name as dept 
                FROM car_maintenance_request r
		left join fleet_vehicle f on (r.car_id = f.id)
		left join car_faults cf on (cf.fault_id = r.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)
                where
                (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s)
                '''  + where_condition + " order by r.name",(date_from,date_to)) 
        res = self.cr.dictfetchall()
        return res

    def _getfault(self,data,ref):
           data_product= data['form']['product_id']
           where_condition = ""
           where_condition += data_product and "f.product_id=%s"%data_product[0] or ""
           where_condition += ref and " and r.id=%s"%ref or ""
           self.cr.execute("""
                SELECT 
                                  p.name_template as fault_name ,
				  f.product_qty as qty ,
				  f.price_unit as unit_price ,
				  f.price_subtotal as subtotal
                FROM car_maintenance_request r
		left join car_faults f on (f.fault_id = r.id)
		left join product_product p on (f.product_id = p.id)
                 where """ + where_condition +"order by r.id")
           res = self.cr.dictfetchall()
           return res

report_sxw.report_sxw('report.car_maintenance.report', 'car.maintenance.request', 'addons/cars_maintenance/report/cars_maintenance.rml' ,parser=car_maintenance , header=False)
