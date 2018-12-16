#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw


# hospitality service wiz report  
# Report to print hospitality service in a certain period of time, according to certain options
# 1 - Department
# 2 - States       ----------------------------------------------------------------------------------------------------------------
class hospitality_service(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hospitality_service, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self._getlines,
            'line4':self._getcount,
            'line5':self._getcount_done,
            'line6':self._getcount_notdone,

        })



    def _getdata(self,data):
	   date_from= data['form']['Date_from']
	   date_to= data['form']['Date_to']
           data_department = data['form']['department_id']
	   data_state = data['form']['state']	

			##### If you select to display all done hospitality service Request #####
			

# check if You choose to display all done hospitality service Reuest
	   if data_state == 'done':
# check if You choose to display all done hospitality service Reuest and for specific department 
	     if data_department !=0:

           	self.cr.execute("""
				select s.name as service_name ,
 					s.id as id ,
 					s.date as request_date,
 					s.date_of_execution as exceution_date,
 					pa.name as partner , 
 					h.name as dept,
					s.cost as cost ,
					s.state ,
					CASE s.state WHEN 'done' THEN 'تم'
                     				     WHEN 'draft'  THEN 'مبدئي'
                     				     WHEN 'cancel'  THEN 'ملغي'
                     		 		     WHEN 'confirmed' THEN 'فى انتظار تصديق مدير الإدارة'
                     		   		     WHEN 'confirmed1' THEN ' فى انتظار تصديق مدير الإدارة العامة'
                     				     WHEN 'confirmed2' THEN 'فى انتظار تصديق مدير الموارد البشرية والمالية والإدارية والامداد'
                     		     		     WHEN 'approve' THEN 'فى انتظار مدير إدارة الشئون الإدارية للاجراء'
                     				     WHEN 'approve1' THEN 'فى انتظار مدير قسم الإعلام للاجراء'
                     				     WHEN 'approve2' THEN 'فى انتظار التنفيذ'
            				END "service_state" 

				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state = 'done' and s.department_id= %s  and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
       				 """,(data['form']['department_id'][0],date_from,date_to)) 

# display all done hospitality service Reuest for all Department


	     else :


           	self.cr.execute("""
				select s.name as service_name ,
 					s.id as id ,
 					s.date as request_date,
 					s.date_of_execution as exceution_date,
 					pa.name as partner , 
 					h.name as dept,
					s.cost as cost ,
					s.state as state 


				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state = 'done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
       			
       				 """,(date_from,date_to))


			##### If you select to display all incomplete hospitality service #####



# check if You choose to display all incompelete hospitality service Reuest
	   elif data_state == 'notdone' :
# check if You choose to display all incompelete hospitality service Reuest and for specific department 
	     if data_department !=0:

           	self.cr.execute("""
				select s.name as service_name ,
 					s.id as id ,
 					s.date as request_date,
 					s.date_of_execution as exceution_date,
 					pa.name as partner , 
 					h.name as dept,
					s.cost as cost ,
					s.state as state 


				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state != 'done' and s.department_id= %s  and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)

       				 """,(data['form']['department_id'][0],date_from,date_to)) 

# display all incomplete hospitality service Reuest for all Department

	     else :


           	self.cr.execute("""
				select s.name as service_name ,
 					s.id as id ,
 					s.date as request_date,
 					s.date_of_execution as exceution_date,
 					pa.name as partner , 
 					h.name as dept,
					s.cost as cost ,
					s.state as state 


				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state != 'done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
       				 
       				 """,(date_from,date_to)) 


			##### If you not select anything ... it will select all hospitality service Request Records#####



	   else:
# check Department 
	     if data_department !=0:

           	self.cr.execute("""
				select s.name as service_name ,
 					s.id as id ,
 					s.date as request_date,
 					s.date_of_execution as exceution_date,
 					pa.name as partner , 
 					h.name as dept,
					s.cost as cost ,
					s.state as state 


				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.department_id= %s  and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)

       				 """,(data['form']['department_id'][0],date_from,date_to)) 
	     else :

           	self.cr.execute("""
				select s.name as service_name ,
 					s.id as id ,
 					s.date as request_date,
 					s.date_of_execution as exceution_date,
 					pa.name as partner , 
 					h.name as dept,
					s.cost as cost ,
					s.state as state 


				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
				""",(date_from,date_to)) 
  
  
           res = self.cr.dictfetchall()
           return res


####################################### Request Counter ##########################################





    def _getcount(self,data):

           date_from= data['form']['Date_from']
	   date_to= data['form']['Date_to']
           data_department = data['form']['department_id']
	   data_state = data['form']['state']	

			##### If you select to display all done hospitality service #####
			

# check if You choose to display all done Foreigners Procedur Reuest
	   if data_state == 'done':
# check if You choose to display all done Foreigners Procedur Reuest and for specific department 
	     if data_department !=0:

           	self.cr.execute("""
				select count(s.id) as counter 
 				

				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state = 'done' and s.department_id= %s  and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
       				 """,(data['form']['department_id'][0],date_from,date_to)) 

# display all done hospitality service Reuest for all Department


	     else :


           	self.cr.execute("""
					select count(s.id) as counter 
				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state = 'done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
       			
       				 """,(date_from,date_to))


			##### If you select to display all incomplete hospitality service #####



# check if You choose to display all incompelete hospitality service Reuest
	   elif data_state == 'notdone' :
# check if You choose to display all incompelete hospitality service Reuest and for specific department 
	     if data_department !=0:

           	self.cr.execute("""
					select count(s.id) as counter 

				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state != 'done' and s.department_id= %s  and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)

       				 """,(data['form']['department_id'][0],date_from,date_to)) 

# display all incomplete hospitality service Reuest for all Department

	     else :


           	self.cr.execute("""
					select count(s.id) as counter 
				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state != 'done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
       				 
       				 """,(date_from,date_to)) 


			##### If you not select anything ... it will select all hospitality service Records#####



	   else:
# check Department 
	     if data_department !=0:

           	self.cr.execute("""
					select count(s.id) as counter  

				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.department_id= %s  and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)

       				 """,(data['form']['department_id'][0],date_from,date_to)) 
	     else :

           	self.cr.execute("""
					select count(s.id) as counter  

				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
				""",(date_from,date_to)) 
  
  
           res = self.cr.dictfetchall()
           return res

##################################### Count All Done Request ########################################

    def _getcount_done(self,data):
	   date_from= data['form']['Date_from']
	   date_to= data['form']['Date_to']

           self.cr.execute("""
									select count(s.id) as counter 
				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state = 'done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
       			
       				 """,(date_from,date_to))
  
  
           res = self.cr.dictfetchall()
           return res



################################### count All Not Done Request #######################################
    def _getcount_notdone(self,data):
	   date_from= data['form']['Date_from']
	   date_to= data['form']['Date_to']

           self.cr.execute("""
					select count(s.id) as counter 
				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)



				where s.state != 'done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date_of_execution,'YYYY-mm-dd')<=%s)
       				 
       				 """,(date_from,date_to)) 
  
           res = self.cr.dictfetchall()
           return res

########################################### Get hospitality service Lines ##################################


    def _getlines(self,request_id):

           self.cr.execute("""
				select 
 					st.name as service_lines ,
 					o.service_qty as service_qty 

				from hospitality_service s

					left join res_partner pa on (s.partner_id = pa.id)
					left join hr_department h on (s.department_id = h.id)
					left join order_lines o on (s.id = o.order_id)
					left join hospitality_service_type st on (o.service_type = st.id)
			where o.order_id = %s
				"""%(request_id)) 
  
  
           res = self.cr.dictfetchall()
           return res












report_sxw.report_sxw('report.hospitality_service.report', 'hospitality.service', 'addons/services/report/hospitality_service.rml' ,parser=hospitality_service,header=False)
