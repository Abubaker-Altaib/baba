# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
from functools import partial



class rights_scheduler(osv.Model):

      _name = 'rights.scheduler'
      

      def check_rights_scheduler(self, cr, uid,context=None):
          
                   
           
        grant_order_obj = self.pool.get("granted.rights.order")
        grant_order_lines_obj = self.pool.get("granted.rights.order.lines")
        department_obj = self.pool.get("hr.department")
        user_obj = self.pool.get("res.users")
        
        
        order_ids =  grant_order_obj.search(cr ,uid ,['|',('start_grant_date','<=', time.strftime("%Y-%m-%d")),('end_grant_date','=', time.strftime("%Y-%m-%d"))])
           
        if order_ids :

           for order in grant_order_obj.browse(cr,uid,order_ids):
               if order.start_grant_date <= time.strftime("%Y-%m-%d") and order.state == 'draft' and order.end_grant_date >= time.strftime("%Y-%m-%d"):

                  cr.execute("SELECT gid as group_id FROM res_groups_users_rel WHERE uid='%s'" % (str(order.employee_candidate.user_id.id),)) 
                  candidate_groups = cr.fetchall()
                  for don_group in order.donor_groups_ids:
                      already_exist = False
                      for can_group in candidate_groups:
                          if don_group.group_id.id == can_group[0]:
                             already_exist = True
                      if already_exist == False:
                         user_obj.write(cr,uid,[order.employee_candidate.user_id.id],{'groups_id':[(4,don_group.group_id.id)]})
                         #cr.execute("INSERT INTO res_groups_users_rel (uid ,gid )  VALUES (%s,%s)" % (order.employee_candidate.user_id.id,don_group.group_id.id,) )
             
                      else : 
                         grant_order_lines_obj.write( cr , uid , [don_group.id] , {'already_granted' : True })
                          
                  #swap = False           
                  employee_donor_department = order.employee_donor.department_id.id
                  employee_candidate_department = order.employee_candidate.department_id.id
                  dep_don_ids = department_obj.search(cr,uid,[('manager_id','=',order.employee_donor.id)])
                  
                  
                  #department_obj.write( cr , uid , [employee_donor_department] , {'pervious_manger_id' : order.employee_donor.id , 'manager_id' : order.employee_candidate.id , 'manager_user_id' : order.employee_candidate.user_id.id })
                  if order.is_a_amanger:
                     for x in dep_don_ids:
		  	department_obj.write( cr , uid , [x] , {'pervious_manger_id' : order.employee_donor.id , 'manager_id' : order.employee_candidate.id , 'manager_user_id' : order.employee_candidate.user_id.id })
                  #user_obj.write( cr , uid , [employee_donor_department] , {'pervious_manger_id' : order.employee_donor.id , 'manager_id' : employee_candidate.id } )
                  
                  grant_order_obj.write( cr , uid , [order.id] , {'state' : 'granted'})   

               if order.end_grant_date == time.strftime("%Y-%m-%d") and order.state == 'granted':
                  for don_group in order.donor_groups_ids:
                      deletd_groups = []
                      if don_group.already_granted == False :
                         cr.execute("SELECT gid as inherit_group_id FROM res_groups_implied_rel WHERE hid=%s" % (don_group.group_id.id))
                         iherits_groups = cr.fetchall()
                         if iherits_groups:
                           for g in iherits_groups:
                              deletd_groups.append((3,g[0])) 
                         deletd_groups.append((3,don_group.group_id.id))
                         user_obj.write(cr,uid,[order.employee_candidate.user_id.id],{'groups_id':deletd_groups})
                         #cr.execute("DELETE FROM res_groups_users_rel where gid='%s' and uid='%s'" % (don_group.group_id.id,order.employee_candidate.user_id.id,) )
                  
                  employee_donor_department = order.employee_donor.department_id.id
                  employee_candidate_department = order.employee_candidate.department_id.id
		  candidate_user_deps = [x.id for x in order.employee_candidate.user_id.department_ids]
                  dep_don_ids = department_obj.search(cr,uid,[('pervious_manger_id','=',order.employee_donor.id),('id','in',candidate_user_deps)])
                  
                  #department_obj.write( cr , uid , [employee_donor_department] , {'pervious_manger_id' : order.employee_candidate.id , 'manager_id' : order.employee_donor.id , 'manager_user_id' : order.employee_donor.user_id.id })
                  if order.is_a_amanger:
                     for x in dep_don_ids:
		  	department_obj.write( cr , uid , [x] , {'pervious_manger_id' : order.employee_candidate.id , 'manager_id' : order.employee_donor.id , 'manager_user_id' : order.employee_donor.user_id.id })

                  grant_order_obj.write( cr , uid , [order.id] , {'state' : 'revoked' , 'active' : False})

               if order.end_grant_date < time.strftime("%Y-%m-%d") and order.state == 'draft':
                    
                  grant_order_obj.write( cr , uid , [order.id] , {'active' : False})


                 
        return True
      
