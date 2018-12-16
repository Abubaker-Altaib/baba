#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw


class car_operation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(car_operation, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
	    'line2':self._getdata2,
            'line3':self._getdata3,
	    'line4':self._getdata4,
        'line5':self._getdata5,


        })
    
########################################### License Section Report ############################### 
    globals()['different']=[]
    def _getdata2(self,data):

           date_from= data['form']['Date_from']
           date_to= data['form']['Date_to']
           date_operation = data['form']['operation_type']
           data_type = data['form']['type']
	

	   if data_type == 'main':
           	self.cr.execute("""
                  	SELECT 
                                  l.id as id ,
				  l.name as name ,
				  l.operation_date as start_date , 
				  l.end_date as end_date , 
				  l.type as license_type 


                	FROM car_operation l

			where l.operation_type='license' and l.state = 'done' and l.type ='main' and (to_char(l.operation_date,'YYYY-mm-dd')>=%s and 	to_char	(l.end_date,'YYYY-mm-dd')<=%s)""",(date_from,date_to))

	   elif data_type == 'extension':
           	self.cr.execute("""
                  	SELECT 
                                  l.id as id ,
				  l.name as name ,
				  l.operation_date as start_date , 
				  l.end_date as end_date ,  
				  l.type as license_type 




                	FROM car_operation l

			where l.operation_type='license' and l.state = 'done' and l.type ='extension' and (to_char(l.operation_date,'YYYY-mm-dd')>=%s and 	to_char	(l.end_date,'YYYY-mm-dd')<=%s)""",(date_from,date_to))

	   else:
           	self.cr.execute("""
                  	SELECT 
                                  l.id as id ,
				  l.name as name , 
				  l.operation_date as start_date , 
				  l.end_date as end_date , 
				  l.type as license_type 


                	FROM car_operation l
			
		where l.operation_type='license' and l.state = 'done' and (to_char(l.operation_date,'YYYY-mm-dd')>=%s and to_char(l.end_date,'YYYY-mm-dd')<=%s)
		""",(date_from,date_to))

           res = self.cr.dictfetchall()
           return res

    def _getdata(self,data,num):

           date_from= data['form']['Date_from']
           date_to= data['form']['Date_to']
           date_operation = data['form']['operation_type']
           data_type = data['form']['type']


	   self.cr.execute("""
                  	SELECT 
                                  l.name as detail_name ,
				  f.name as car_name ,
				  f.license_plate as car_number ,
				  f.vin_sn as chassis ,
				  f.machine_no as machine ,
				  h.name as dept ,
				  m.name as model ,
				  f.year as year ,
				  f.type as car_type  ,
				  l.type as license_type 


                	FROM car_operation l

			left join license_cars lc on (l.id = lc.license_id)
			left join fleet_vehicle f on (lc.car_id = f.id)
			left join fleet_vehicle_model m on (f.model_id = m.id)
			left join hr_department h on (f.department_id = h.id)


			where l.id = %s"""%(num))

           res = self.cr.dictfetchall()
           return res


########################################### Insurance Section Report ############################### 

    def _getdata3(self,data):
       date_from= data['form']['Date_from']
       date_to= data['form']['Date_to']
       date_operation = data['form']['operation_type']
       data_type = data['form']['type']
    

       if data_type == 'main':
               self.cr.execute("""
                      SELECT 
                                  l.id as id ,
                  l.name as name ,
                  l.operation_date as start_date , 
                  l.end_date as end_date , 
                  l.type as license_type 


                    FROM car_operation l

            where l.operation_type='insurance' and l.state = 'done' and l.type ='main' and (to_char(l.operation_date,'YYYY-mm-dd')>=%s and     to_char    (l.end_date,'YYYY-mm-dd')<=%s)""",(date_from,date_to))

       elif data_type == 'extension':
               self.cr.execute("""
                      SELECT 
                                  l.id as id ,
                  l.name as name ,
                  l.operation_date as start_date , 
                  l.end_date as end_date ,  
                  l.type as license_type 




                    FROM car_operation l

            where l.operation_type='insurance' and l.state = 'done' and l.type ='extension' and (to_char(l.operation_date,'YYYY-mm-dd')>=%s and     to_char    (l.end_date,'YYYY-mm-dd')<=%s)""",(date_from,date_to))

       else:
               self.cr.execute("""
                      SELECT 
                                  l.id as id ,
                  l.name as name , 
                  l.operation_date as start_date , 
                  l.end_date as end_date , 
                  l.type as license_type 


                    FROM car_operation l
            
        where l.operation_type='insurance' and l.state = 'done' and (to_char(l.operation_date,'YYYY-mm-dd')>=%s and to_char(l.end_date,'YYYY-mm-dd')<=%s)
        """,(date_from,date_to))

       res = self.cr.dictfetchall()
       return res


    def _getdata4(self,data,num):
       
       end_list=[]
       list_end=[]
       lists=[]
       data_end_insur = data['form']['end_period']
       #if data_end_insur == 'insure_car' :
       self.cr.execute(""" select id as car_id from fleet_vehicle where status='active' """)
       all_id=self.cr.dictfetchall()
       for m in all_id:
               lists.append(m['car_id']) 
       self.cr.execute(""" SELECT  f.id as car_id FROM car_operation  l left join car_operation_line lc on (l.id = lc.operation_id)
            left join fleet_vehicle f on (lc.car_id = f.id)
            where l.id = %s """ %num)
       inur_id=self.cr.dictfetchall()
       for car in inur_id:
                      end_list.append(car['car_id'])
                      self.cr.execute('''SELECT 
                  l.name as detail_name ,
				  f.name as car_name ,
				  f.license_plate as car_number ,
				  f.vin_sn as chassis ,
				  f.machine_no as machine ,
				  h.name as dept ,
				  m.name as model ,
				  f.year as year ,
				  f.type as car_type  ,
				  lc.cost as total ,
				  lc.document as doc , 
				  l.type as license_type 
                	FROM car_operation l
			   left join car_operation_line lc on (l.id = lc.operation_id)
			   left join fleet_vehicle f on (lc.car_id = f.id)
			   left join fleet_vehicle_model m on (f.model_id = m.id)
			   left join hr_department h on (f.department_id = h.id)
			   where f.id = %s and l.id=%s''',(car['car_id'],num))
                      res= self.cr.dictfetchall()
                      for n in res:   
                          dic={'car_name':n['car_name'],
                               'car_number':n['car_number'],
                               'chassis':n['chassis'],
                               'machine':n['machine'],
                               'model':n['model'],
                               'year':n['year'],
                               'car_type':n['car_type'],
                               'total':n['total'],
                               'doc':n['doc'],
                               'license_type ':n['license_type']}
                          list_end.append(dic)     
             
       globals()['different']= list(set(lists)-set(end_list))               
       return list_end
       

    def _getdata5(self,data):
       list_end=[]
       lists=[]
       data_end_insur = data['form']['end_period']
       #if data_end_insur == 'end_insure_car'  :    
       for car in globals()['different']:
                      self.cr.execute('''SELECT distinct
                  f.name as car_name ,
                  f.license_plate as car_number ,
                  f.vin_sn as chassis ,
                  f.machine_no as machine ,
                  h.name as dept ,
                  m.name as model ,
                  f.year as year ,
                  f.type as car_type              
                    FROM 
                fleet_vehicle f 
               left join fleet_vehicle_model m on (f.model_id = m.id)
               left join hr_department h on (f.department_id = h.id)
               where f.id = %s '''%car)
                      res= self.cr.dictfetchall()
                      for n in res:   
                          dic={'car_name':n['car_name'],
                               'car_number':n['car_number'],
                               'chassis':n['chassis'],
                               'machine':n['machine'],
                               'model':n['model'],
                               'year':n['year'],
                               'car_type':n['car_type'],
                               'dept':n['dept'],}
                          list_end.append(dic)
       return list_end
report_sxw.report_sxw('report.car_operation.report', 'car.operation', 'addons/car_operation/report/car_operation.rml' ,parser=car_operation , header=False)
report_sxw.report_sxw('report.car_end_operation.report', 'car.operation', 'addons/car_operation/report/car_end_operation.rml' ,parser=car_operation , header=False)
