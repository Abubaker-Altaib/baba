#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Media Service report  
# Report to print information services in a certain period of time, according to certain options
# 1 - Department
# 2 - States       ----------------------------------------------------------------------------------------------------------------
class media_service(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(media_service, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self._getcount,
            'line3':self._getcount_done,
            'line4':self._getcount_notdone,
        })

    def _getdata(self,data):
	   date_from= data['form']['Date_from']
	   date_to= data['form']['Date_to']
           data_department = data['form']['department_id']
	   data_state = data['form']['state']	

			##### If you select to display all done media service request #####
			

# check if You choose to display all done media service Reuest
	   if data_state == 'done':
# check if You choose to display all done media service Reuest and for specific department 
	     if data_department !=0:
# select Request Number & Request Date & Service Date & Department & Service & service Type & State & Notes          
           	self.cr.execute("""

                	select o.name as name ,
				o.date as service_date , 
				DATE(o.create_date) as create_date , 
				c.name category_name ,
				o.state ,
					CASE o.state WHEN 'done' THEN 'تم'
                     				     WHEN 'draft'  THEN 'مبدئي'
                     				     WHEN 'cancel'  THEN 'ملغي'
                     		 		     WHEN 'confirmed' THEN 'فى انتظار تصديق مدير الإدارة'
                     		   		     WHEN 'confirmed1' THEN ' فى انتظار تصديق مدير الإدارة العامة'
                     				     WHEN 'confirmed2' THEN 'فى انتظار تصديق مدير الموارد البشرية والمالية والإدارية والامداد'
                     		     		     WHEN 'approve' THEN 'فى انتظار مدير إدارة الشئون الإدارية للاجراء'
                     				     WHEN 'approve1' THEN 'فى انتظار مدير قسم الإعلام للاجراء'
                     				     WHEN 'approve2' THEN 'فى انتظار التنفيذ'
            				END "service_state" ,

				h.name as dept , 
				t.name as type_name ,
				l.name as lines_notes ,
				o.notes as media_notes
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state = 'done' and o.department_id= %s  and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(data['form']['department_id'][0],date_from,date_to)) 

# display all done media service Reuest for all Department


	     else :
# select Request Number & Request Date & Service Date & Department & Service & service Type & State & Notes          

           	self.cr.execute("""
                	select o.name as name ,
				o.date as service_date , 
				DATE(o.create_date) as create_date , 
				c.name category_name ,
				o.state ,
					CASE o.state WHEN 'done' THEN 'تم'
                     		WHEN 'draft'  THEN 'مبدئي'
                     		WHEN 'cancel'  THEN 'ملغي'
                     		WHEN 'confirmed' THEN 'فى انتظار تصديق مدير الإدارة '
                     		WHEN 'confirmed1' THEN 'فى انتظار تصديق مدير الإدارة العامة'
                     		WHEN 'confirmed2' THEN 'فى انتظار تصديق مدير الموارد البشرية والمالية والإدارية والامداد'
                     		WHEN 'approve' THEN 'فى انتظار مدير إدارة الشئون الإدارية للاجراء'
                     		WHEN 'approve1' THEN 'فى انتظار مدير قسم الإعلام للاجراء'
                     		WHEN 'approve2' THEN 'فى انتظار التنفيذ'
            				END "service_state" ,

				h.name as dept , 
				t.name as type_name ,
				l.name as lines_notes ,
				o.notes as media_notes
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state = 'done' and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(date_from,date_to))


			##### If you select to display all incomplete media service request #####



# check if You choose to display all incompelete media service Reuest
	   elif data_state == 'notdone' :
# check if You choose to display all incompelete media service Reuest and for specific department 
	     if data_department !=0:
# select Request Number & Request Date & Service Date & Department & Service & service Type & State & Notes          
           	self.cr.execute("""
                	select o.name as name ,
				o.date as service_date , 
				DATE(o.create_date) as create_date , 
				c.name category_name ,
				o.state ,
					CASE o.state WHEN 'done' THEN 'تم'
                     				     WHEN 'draft'  THEN 'مبدئي'
                     				     WHEN 'cancel'  THEN 'ملغي'
                     		 		     WHEN 'confirmed' THEN 'فى انتظار تصديق مدير الإدارة'
                     		   		     WHEN 'confirmed1' THEN ' فى انتظار تصديق مدير الإدارة العامة'
                     				     WHEN 'confirmed2' THEN 'فى انتظار تصديق مدير الموارد البشرية والمالية والإدارية والامداد'
                     		     		     WHEN 'approve' THEN 'فى انتظار مدير إدارة الشئون الإدارية للاجراء'
                     				     WHEN 'approve1' THEN 'فى انتظار مدير قسم الإعلام للاجراء'
                     				     WHEN 'approve2' THEN 'فى انتظار التنفيذ'
            				END "service_state" ,

				h.name as dept , 
				t.name as type_name ,
				l.name as lines_notes ,
				o.notes as media_notes
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state!= 'done' and o.department_id= %s  and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(data['form']['department_id'][0],date_from,date_to)) 

# display all incomplete media service Reuest for all Department

	     else :
# select Request Number & Request Date & Service Date & Department & Service & service Type & State & Notes          

           	self.cr.execute("""
                	select o.name as name ,
				o.date as service_date , 
				DATE(o.create_date) as create_date , 
				c.name category_name ,
				o.state ,
					CASE o.state WHEN 'done' THEN 'تم'
                     		WHEN 'draft'  THEN 'مبدئي'
                     		WHEN 'cancel'  THEN 'ملغي'
                     		WHEN 'confirmed' THEN 'فى انتظار تصديق مدير الإدارة '
                     		WHEN 'confirmed1' THEN 'فى انتظار تصديق مدير الإدارة العامة'
                     		WHEN 'confirmed2' THEN 'فى انتظار تصديق مدير الموارد البشرية والمالية والإدارية والامداد'
                     		WHEN 'approve' THEN 'فى انتظار مدير إدارة الشئون الإدارية للاجراء'
                     		WHEN 'approve1' THEN 'فى انتظار مدير قسم الإعلام للاجراء'
                     		WHEN 'approve2' THEN 'فى انتظار التنفيذ'
            				END "service_state" ,

				h.name as dept , 
				t.name as type_name ,
				l.name as lines_notes ,
				o.notes as media_notes
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state!= 'done' and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(date_from,date_to)) 


			##### If you not select anything ... it will select all Media service Records#####



	   else:
# check Department 
	     if data_department !=0:

           	self.cr.execute("""
                	select o.name as name ,
				o.date as service_date , 
				DATE(o.create_date) as create_date , 
				c.name category_name ,
				o.state ,
					CASE o.state WHEN 'done' THEN 'تم'
                     				     WHEN 'draft'  THEN 'مبدئي'
                     				     WHEN 'cancel'  THEN 'ملغي'
                     		 		     WHEN 'confirmed' THEN 'فى انتظار تصديق مدير الإدارة'
                     		   		     WHEN 'confirmed1' THEN ' فى انتظار تصديق مدير الإدارة العامة'
                     				     WHEN 'confirmed2' THEN 'فى انتظار تصديق مدير الموارد البشرية والمالية والإدارية والامداد'
                     		     		     WHEN 'approve' THEN 'فى انتظار مدير إدارة الشئون الإدارية للاجراء'
                     				     WHEN 'approve1' THEN 'فى انتظار مدير قسم الإعلام للاجراء'
                     				     WHEN 'approve2' THEN 'فى انتظار التنفيذ'
            				END "service_state" ,

				h.name as dept , 
				t.name as type_name ,
				l.name as lines_notes ,
				o.notes as media_notes
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.department_id= %s  and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(data['form']['department_id'][0],date_from,date_to)) 
	     else :

           	self.cr.execute("""
                	select o.name as name ,
				o.date as service_date , 
				DATE(o.create_date) as create_date , 
				c.name category_name ,
				o.state ,
					CASE o.state WHEN 'done' THEN 'تم'
                     		WHEN 'draft'  THEN 'مبدئي'
                     		WHEN 'cancel'  THEN 'ملغي'
                     		WHEN 'confirmed' THEN 'فى انتظار تصديق مدير الإدارة '
                     		WHEN 'confirmed1' THEN 'فى انتظار تصديق مدير الإدارة العامة'
                     		WHEN 'confirmed2' THEN 'فى انتظار تصديق مدير الموارد البشرية والمالية والإدارية والامداد'
                     		WHEN 'approve' THEN 'فى انتظار مدير إدارة الشئون الإدارية للاجراء'
                     		WHEN 'approve1' THEN 'فى انتظار مدير قسم الإعلام للاجراء'
                     		WHEN 'approve2' THEN 'فى انتظار التنفيذ'
            				END "service_state" ,

				h.name as dept , 
				t.name as type_name ,
				l.name as lines_notes ,
				o.notes as media_notes
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(date_from,date_to)) 
  
  
           res = self.cr.dictfetchall()
           return res






####################################### Request Counter ##########################################





    def _getcount(self,data):
	   date_from= data['form']['Date_from']
	   date_to= data['form']['Date_to']
           data_department = data['form']['department_id']
	   data_state = data['form']['state']	

			##### If you select to display all done media service request #####
			

# check if You choose to display all done media service Reuest
	   if data_state == 'done':
# check if You choose to display all done media service Reuest and for specific department 
	     if data_department !=0:

           	self.cr.execute("""

                	select count(o.id) as counter 
				
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state = 'done' and o.department_id= %s  and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(data['form']['department_id'][0],date_from,date_to)) 

# display all done media service Reuest for all Department


	     else :


           	self.cr.execute("""
                	select count(o.id) as counter 
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state = 'done' and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(date_from,date_to))


			##### If you select to display all incomplete media service request #####



# check if You choose to display all incompelete media service Reuest
	   elif data_state == 'notdone' :
# check if You choose to display all incompelete media service Reuest and for specific department 
	     if data_department !=0:

           	self.cr.execute("""
                	select count(o.id) as counter 
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state!= 'done' and o.department_id= %s  and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(data['form']['department_id'][0],date_from,date_to)) 

# display all incomplete media service Reuest for all Department

	     else :


           	self.cr.execute("""
                	select count(o.id) as counter 
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state!= 'done' and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(date_from,date_to)) 


			##### If you not select anything ... it will select all Media service Records#####



	   else:
# check Department 
	     if data_department !=0:

           	self.cr.execute("""
                	select count(o.id) as counter 
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.department_id= %s  and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(data['form']['department_id'][0],date_from,date_to)) 
	     else :

           	self.cr.execute("""
                	select count(o.id) as counter 
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(date_from,date_to)) 
           res = self.cr.dictfetchall()
           return res


##################################### Count All Done Request ########################################

    def _getcount_done(self,data):
	   date_from= data['form']['Date_from']
	   date_to= data['form']['Date_to']

           self.cr.execute("""
                	select count(o.id) as counter 
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state = 'done' and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(date_from,date_to))
  
  
           res = self.cr.dictfetchall()
           return res



################################### count All Not Done Request #######################################
    def _getcount_notdone(self,data):
	   date_from= data['form']['Date_from']
	   date_to= data['form']['Date_to']

           self.cr.execute("""
                	select count(o.id) as counter 
			from media_order o 
				left join hr_department h on (o.department_id=h.id)
				left join media_order_line l on (o.id=l.order_id)
				left join media_service_category c on (o.category_id=c.id)
				left join media_service_type t on (l.type_id=t.id)
			where o.state!= 'done' and (to_char(o.create_date,'YYYY-mm-dd')>=%s and to_char(o.date,'YYYY-mm-dd')<=%s)
       				 """,(date_from,date_to)) 
  
           res = self.cr.dictfetchall()
           return res

report_sxw.report_sxw('report.media_service.report', 'media.order', 'media/report/media_service_report.rml' ,parser=media_service,header=False)
