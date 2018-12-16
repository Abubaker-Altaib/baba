#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw


class cars_maintenance_type(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cars_maintenance_type, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self._getfault,


        })


    def _getdata(self,data):

           date_from= data['form']['Date_from']
           date_to= data['form']['Date_to']
           data_type = data['form']['maintenance_type']
	   data_state = data['form']['state']

# select all done or notdone or all record where Maintance Type is Regular

	   if data_type == 'regular':
		if data_state == 'done' :
			self.cr.execute("""
                SELECT 
				  r.id as id , 
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total ,
				  r.state as state , 
				  res.name as driver_name ,
				  h.name as dept 


  
                FROM car_maintenance_request r

		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)

		where r.state = 'done' and r.maintenance_type = 'regular' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s) ORDER BY r.id """,(date_from,date_to))

		elif data_state == 'notdone' :

			self.cr.execute("""
                SELECT 
				  r.id as id , 
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total , 
				  r.state as state , 
				  res.name as driver_name ,
				  h.name as dept 


  
                FROM car_maintenance_request r

		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)

		where r.state != 'done' and r.maintenance_type = 'regular' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s) ORDER BY r.id """,(date_from,date_to))



		else :

			self.cr.execute("""
                SELECT 
				  r.id as id , 
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total , 
				  r.state as state , 
				  res.name as driver_name ,
				  h.name as dept 


  
                FROM car_maintenance_request r

		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)

		where r.maintenance_type = 'regular' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s) ORDER BY r.id """,(date_from,date_to))


# select all done or notdone or all record where Maintance Type is Emergency

	   elif data_type == 'emergency':
		if data_state == 'done' :

			self.cr.execute("""
                SELECT 
				  r.id as id , 
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total ,
				  r.state as state ,  
				  res.name as driver_name ,
				  h.name as dept 


  
                FROM car_maintenance_request r

		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)

		where r.state = 'done' and r.maintenance_type = 'emergency' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s) ORDER BY r.id """,(date_from,date_to))



		elif data_state == 'notdone' :

			self.cr.execute("""
                SELECT 
				  r.id as id , 
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total ,
				  r.state as state ,  
				  res.name as driver_name ,
				  h.name as dept 


  
                FROM car_maintenance_request r

		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)

		where r.state != 'done' and r.maintenance_type = 'emergency' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s) ORDER BY r.id """,(date_from,date_to))



		else :

			self.cr.execute("""
                SELECT 
				  r.id as id , 
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total ,
				  r.state as state ,  
				  res.name as driver_name ,
				  h.name as dept 


  
                FROM car_maintenance_request r

		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)

		where r.maintenance_type = 'emergency' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s) ORDER BY r.id """,(date_from,date_to))




# select all done or notdone or all record for Regular and Emergency
	   else : 

		if data_state == 'done' :
			self.cr.execute("""
                SELECT 
				  r.id as id , 
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total ,
				  r.state as state ,  
				  res.name as driver_name ,
				  h.name as dept 


  
                FROM car_maintenance_request r

		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)

		where r.state = 'done' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s) ORDER BY r.id """,(date_from,date_to))



		elif data_state == 'notdone' :
			self.cr.execute("""
                SELECT 
				  r.id as id , 
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total , 
				  r.state as state , 
				  res.name as driver_name ,
				  h.name as dept 


  
                FROM car_maintenance_request r

		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)

		where r.state != 'done'and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s) ORDER BY r.id""",(date_from,date_to))



		else :
			self.cr.execute("""
                SELECT 
				  r.id as id , 
                                  r.name as detail_name ,
				  r.maintenance_type as type ,
				  p.name as partner ,
				  r.total_amount as total , 
				  r.state as state , 
				  res.name as driver_name ,
				  h.name as dept 


  
                FROM car_maintenance_request r

		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.driver_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)

		where (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s) ORDER BY r.id """,(date_from,date_to))



           res = self.cr.dictfetchall()
           return res


# Selecting Spare part for specfic Record 

    def _getfault(self,ref):

           self.cr.execute("""
                SELECT 
                                  p.name_template as fault_name ,
				  f.product_qty as qty ,
				  f.price_subtotal as subtotal

  
                FROM car_maintenance_request r

		left join car_faults f on (f.fault_id = r.id)
		left join product_product p on (f.product_id = p.id)



                 where r.id = %s"""%(ref))


 
           res = self.cr.dictfetchall()
           return res


report_sxw.report_sxw('report.cars_maintenance_type.report', 'car.maintenance.request', 'addons/cars_maintenance/report/cars_maintenance_type.rml' ,parser=cars_maintenance_type , header=False)
