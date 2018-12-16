#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Hotel services report  
# Report to print Hotes Services in a certain period of time, according to certain options
# 1 - Department
# 2 - States       ----------------------------------------------------------------------------------------------------------------
class hotel_service_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hotel_service_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line4':self._getcount,
            'line5':self._getcount_done,
            'line6':self._getcount_notdone,

        })



    def _getdata(self,data):
        date_from= data['form']['Date_from']
        date_to= data['form']['Date_to']
        data_department = data['form']['department_id']
        data_state = data['form']['state']
  
##### If you select to display all done Hotel services #####
# check if You choose to display all done hotel services
        if data_state == "done":
# check if You choose to display all done hotel services and for specific department 
            if data_department !=0:

# select Request Number & Request Date  & Department  & service type & State & Notes          
                self.cr.execute("""
                select hs.name as request_name,
                hs.id as id ,
                    hs.create_date as request_date ,
                    hs.date as procedure_date ,
                hs.state as state,
                hr.name as dept , 
                hs.notes as notes,
                pr.name as partner_id 
                from hotel_service hs
                left join hr_department hr on (hs.department_id = hr.id)
		left join res_partner pr on (hs.partner_id = pr.id)
               where hs.state = "done" and hs.department_id= %s  and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)
                """,(data['form']['department_id'][0],date_from,date_to)) 
#,hs.service_type as service_type
# display all done Hotel Servicesfor all Department


            else :
# select Request Number & Request  & State & Notes          

                self.cr.execute("""
                select hs.name as request_name,
                    hs.state as state,
                    hs.id as id ,
                    hr.name as dept , 
                    hs.create_date as request_date ,
                    hs.date as procedure_date ,
                   hs.notes as notes,
                pr.name as partner_id 
                  from hotel_service hs

                left join hr_department hr on (hs.department_id = hr.id)
		left join res_partner pr on (hs.partner_id = pr.id)

            where hs.state = 'done' and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)
                   
                        """,(date_from,date_to))


#,hs.service_type as service_type       
##### If you select to display all incomplete Hotel services #####



# check if You choose to display all incompelete Hotel services Reuest
        elif data_state == 'notdone' :
# check if You choose to display all incompeleteHotel services Reuest and for specific department 
            if data_department !=0:
# select Request Number & Request Date & Procedur Date & Department & hotel services & Procedur & State & Notes          
                self.cr.execute("""
                    select hs.name as request_name,
                    hs.id as id ,
                    hs.create_date as request_date ,
                    hs.date as procedure_date ,
                    hs.state as state,
                    hr.name as dept , 
                    hs.notes as notes,
                pr.name as partner_id 
                from hotel_service hs
		left join res_partner pr on (hs.partner_id = pr.id)
                left join hr_department hr on (hs.department_id = hr.id)
            where hs.state != 'done' and hs.department_id= %s  and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)
                        """,(data['form']['department_id'][0],date_from,date_to))
#                    hs.meal_type as meal_type, 
#,hs.service_type as service_type 
# display all incomplete Hotel services Reuest for all Department

            else :
# select Request Number & Request Date & Procedur Date & Department & hotel services & Procedur & State & Notes          

                self.cr.execute("""
                    select hs.name as request_name,
                    hs.id as id ,
                    hs.create_date as request_date ,
                    hs.date as procedure_date ,
                    hs.state as state,
                    hr.name as dept , 
                    hs.notes as notes,
                pr.name as partner_id
                from hotel_service hs
		left join res_partner pr on (hs.partner_id = pr.id)
                left join hr_department hr on (hs.department_id = hr.id)
            where hs.state != 'done' and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)                        
                """,(date_from,date_to)) 
#                    hs.meal_type as meal_type,
#hs.service_type as service_type  
            ##### If you not select anything ... it will select all Hotel service Records#####



        else:
# check Department 
            if data_department !=0:

                self.cr.execute("""
                    select hs.name as request_name,
                    hs.id as id ,
                    hs.create_date as request_date ,
                    hs.date as procedure_date ,
                    hs.state as state,
                    hr.name as dept , 
                    hs.notes as notes,
                pr.name as partner_id
                from hotel_service hs
		left join res_partner pr on (hs.partner_id = pr.id)
                left join hr_department hr on (hs.department_id = hr.id)
            where hs.department_id= %s  and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)

                        """,(data['form']['department_id'][0],date_from,date_to)) 
#                hs.service_type as service_type
#                    hs.meal_type as meal_type,  
            else :

                self.cr.execute("""
                    select hs.name as request_name,
                    hs.id as id ,
                    hs.create_date as request_date ,
                    hs.date as procedure_date ,
                    hs.state as state,
                    hr.name as dept , 
                    hs.notes as notes,
                pr.name as partner_id
                from hotel_service hs
		left join res_partner pr on (hs.partner_id = pr.id)
                left join hr_department hr on (hs.department_id = hr.id)

            where (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)
                """,(date_from,date_to)) 
        res = self.cr.dictfetchall()
        return res

#                hs.service_type as service_type 
#                    hs.meal_type as meal_type, 
####################################### Request Counter ##########################################





    def _getcount(self,data):
        date_from= data['form']['Date_from']
        date_to= data['form']['Date_to']
        data_department = data['form']['department_id']
        data_state = data['form']['state']
        ##### If you select to display all done Hotel Services #####
# check if You choose to display all done Hotel Services Reuest
        if data_state == 'done':
# check if You choose to display all done Hotel services  and for specific department 
            if data_department !=0:
                self.cr.execute("""
                select count(hs.id) as counter 
                from hotel_service hs
                left join hr_department hr on (hs.department_id = hr.id)
            where hs.state = 'done' and hs.department_id= %s  and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)
            """,(data['form']['department_id'][0],date_from,date_to)) 

# display all done Hotel Services for all Department

            else :
                self.cr.execute("""
                select count(hs.id) as counter 
                from hotel_service hs
                left join hr_department hr on (hs.department_id = hr.id)
               where hs.state = 'done' and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)                   
               """,(date_from,date_to))

 ##### If you select to display all incomplete Hotel Services #####



# check if You choose to display all incompelete Hotel Services
        elif data_state == 'notdone' :

            if data_department !=0:
                self.cr.execute("""
                select count(hs.id) as counter 
                from hotel_service hs
                left join hr_department hr on (hs.department_id = hr.id)
                where hs.state != 'done' and hs.department_id= %s  and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)
                """,(data['form']['department_id'][0],date_from,date_to,)) 

# display all incomplete Hotel Service Request for all Department

            else :
                self.cr.execute("""
                select count(hs.id) as counter 
                from hotel_service hs
                left join hr_department hr on (hs.department_id = hr.id)
                where hs.state != 'done' and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)                     
                        """,(date_from,date_to)) 


            ##### If you not select anything ... it will select all Hotel Services#####

        else:
# check Department 
            if data_department !=0:
                self.cr.execute("""
                select count(hs.id) as counter 
                from hotel_service hs
                left join hr_department hr on (hs.department_id = hr.id)
                where hs.department_id= %s  and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)
                """,(data['form']['department_id'][0],date_from,date_to)) 

            else :
                self.cr.execute("""
                select count(hs.id) as counter 
                from hotel_service hs
                left join hr_department hr on (hs.department_id = hr.id)
               where (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hr.create_date,'YYYY-mm-dd')<=%s)
                """,(date_from,date_to)) 
  
        res = self.cr.dictfetchall()
        return res
        
##################################### Count All Done Request ########################################

    def _getcount_done(self,data):
       date_from= data['form']['Date_from']
       date_to= data['form']['Date_to']
       self.cr.execute("""
                select count(hs.id) as counter 
                from hotel_service hs
                left join hr_department hr on (hs.department_id = hr.id)
                where hs.state = 'done' and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)                   
                """,(date_from,date_to))  
       res = self.cr.dictfetchall()
       return res



################################### count All Not Done Request #######################################
    def _getcount_notdone(self,data):
       date_from= data['form']['Date_from']
       date_to= data['form']['Date_to']
       self.cr.execute("""
                select count(hs.id) as counter 
                from hotel_service hs
                left join hr_department hr on (hs.department_id = hr.id)
               where hs.state != 'done' and (to_char(hs.date,'YYYY-mm-dd')>=%s and to_char(hs.create_date,'YYYY-mm-dd')<=%s)                        
                """,(date_from,date_to))   
       res = self.cr.dictfetchall()
       return res


report_sxw.report_sxw('report.hotel.service.report.report', 'hotel.service', 'addons/public_relation/report/hotel_service.rml' ,parser=hotel_service_report,header=False)
