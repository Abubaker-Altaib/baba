#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw


class cars_mission(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cars_mission, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self._getdata2,
            'line3':self._getcount,

        })

    def _getdata2(self,data):


        date_from= data['form']['Date_from']
        date_to= data['form']['Date_to']
        data_car = data['form']['car_id']	

	if data_car !=0:

           self.cr.execute("""
                SELECT 
                                  distinct f.id as id ,
				  f.license_plate as num ,
                                  f."name" as name 

  
                FROM fuel_request r

		left join fleet_vehicle f on (r.car_id = f.id)

                where r.car_id =%s and r.state='done' and r.purpose='mission' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s)""",(data['form']['car_id'][0],date_from,date_to))
	else  :

           self.cr.execute("""
                SELECT 
                                  distinct f.id as id ,
				  f.license_plate  as num ,
                                  f."name" as name 

  
                FROM 
                                  fuel_request r
		left join fleet_vehicle f on (r.car_id = f.id)

                where  r.state='done' and r.purpose='mission' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s)
               """,(date_from,date_to))

 
        res = self.cr.dictfetchall()
        return res

    def _getdata(self,data , num ):

           date_from= data['form']['Date_from']
           date_to= data['form']['Date_to']
           data_car = num
           self.cr.execute("""
                 select r.name as req_name , r.date as date  , l.name as product , l.product_qty  as qty , h.name as dept

				from fuel_request r 

		left join fuel_request_lines l on (l.fuel_id=r.id)

		left join fleet_vehicle f on (r.car_id = f.id)
		left join hr_department h on (f.department_id = h.id)


		where r.purpose='mission' and r.car_id =%s and r.state = 'done' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s)""",(data_car,date_from,date_to)) 
           res = self.cr.dictfetchall()
           return res


    def _getcount(self,data , num ):

           date_from= data['form']['Date_from']
           date_to= data['form']['Date_to']
           data_car = num
           self.cr.execute("""
                 select count(r.id) as count 

				from fuel_request r 

		where r.purpose='mission' and r.car_id =%s and r.state = 'done' and (to_char(r.date,'YYYY-mm-dd')>=%s and to_char(r.date,'YYYY-mm-dd')<=%s)""",(data_car,date_from,date_to)) 
           res = self.cr.dictfetchall()
           return res
report_sxw.report_sxw('report.cars_mission.report', 'fuel.request', 'addons/fuel_management/report/cars_mission.rml' ,parser=cars_mission , header=False)
