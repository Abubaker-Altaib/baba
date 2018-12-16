# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import pooler
import time
import datetime
from tools.translate import _

class hr_attendance(osv.osv):
    _inherit='hr.attendance' 

    def sign_out_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
       """Scheduler to sign_out employee automatically at the end of the day if the employee not sign_out by the attendance device
       @return True
       """
       date=time.strftime('%Y-%m-%d')
       date_time=time.strftime('%Y-%m-%d %H:%M:%S')
       #emp_attend_ids=self.search(cr,uid,[('day','=',date),('action','=','sign_in')])
       cr.execute('''select max(name) as date , employee_id as emp from hr_attendance where day=%s and action='sign_in' group by employee_id ''',(date,))          
       emp_attend_res= cr.dictfetchall() 
       print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>" , emp_attend_res
       if emp_attend_res:
          for emp_attend in emp_attend_res:
             #check_sign_out=self.search(cr,uid,[('employee_id','=',emp_attend.employee_id.id),('action','=','sign_out'),('day','=',date)])
             cr.execute('''select  max(name) as date , employee_id as emp from hr_attendance where day =%s and action='sign_out' and name >=%s and employee_id =%s group by employee_id ''',(date,emp_attend['date'],emp_attend['emp'],))          
             check_sign_out= cr.dictfetchall() 
             if not check_sign_out:
                create_sign_out=super(osv.osv, self).create(cr, uid,{'employee_id':emp_attend['emp'], 'action':'sign_out', 'name':date_time} , context)
       return True

hr_attendance()
