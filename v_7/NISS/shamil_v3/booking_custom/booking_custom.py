# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
import netsvc

def create_booking(self,cr,uid,record,record_type,department_id,info,msg,context=None):
   """
   Create ticket booking from mission or training course.

   @param record: hr.employee.mission record or hr.employee.training record
   @param record_type: mission or training
   @param department_id: Id of mission or training department
   @param info: Text of mission or training information
   @param msg: Notes if mission days less than a week
   @return: Id of creating booking
   """

   booking_obj= self.pool.get('ticket.booking')
   if record_type == 'training': 
      if record.training_place == 'inside' :
         ticket_type = 'internal'
   ticket_type = 'external'
   booking_dict={
		  'company_id':record.company_id.id,
		  'department_id':department_id and department_id,
		  'date_of_travel':record.start_date,
		  'date_of_return':record.end_date,
		  'travel_purpose':record_type,
		  'procedure_for':'sudanese',
		  'type':ticket_type,
		  'info':info,
          'notes':msg,
		}

   booking_id = booking_obj.create(cr, uid,booking_dict , context=context)
   return booking_id


class employee_missions(osv.osv):
    """
    To manage employee_missions inherit """

    _inherit = "hr.employee.mission"
    _columns={
           'booking_requested': fields.boolean('Booking Requested', readonly=True),
            }

    def request_booking(self,cr,uid,ids,context=None):
       """
       Request ticket booking from mission if the transport type is air plan.

       @param ids: :List of id of mission
       @return: Boolean True or False
       """
       for mission in self.browse(cr,uid,ids,context=context):
          if mission.transport=='3' and not mission.booking_requested:
             info = mission.name + ' ' + mission.start_date + ' / ' + mission.end_date
             num_of_days=self._get_number_of_days(mission.start_date,mission.end_date)
             week_days = 7
             if week_days >= num_of_days:
                msg='Number of days less than one week'
             else:
                msg=''
             booking_id=create_booking(self,cr,uid,mission,'mission',False , info ,msg, context=context)
             for employee in mission.mission_line:
                cr.execute("INSERT into employee_ticket_booking_rel values(%s,%s)",(booking_id,employee.employee_id.id,))
             return self.write(cr,uid,ids,{'booking_requested':True})
          else:
             return False
 

class training_approved_course(osv.osv):
    """
    To manage training approved course """

    _inherit = 'hr.employee.training'
    _columns={
           'booking_requested': fields.boolean('Booking Requested', readonly=True),
            }


    def request_booking(self,cr,uid,ids,context=None):
       """
       Request ticket booking from training courses if the training place is outside.

       @param ids: :List of id of approved courses
       @return: Boolean True or False
       """
       booking_obj= self.pool.get('ticket.booking')
       for course in self.browse(cr,uid,ids,context=context):
          if course.training_place=='outside' and not course.booking_requested:
             info = course.course_id.name + ' ' + course.start_date + ' / ' + course.end_date
             booking_id= create_booking(self,cr,uid,course,'training',False , info ,'', context=context)
             for employee in course.line_ids:
                cr.execute("INSERT into employee_ticket_booking_rel values(%s,%s)",(booking_id,employee.id,))
             return self.write(cr,uid,ids,{'booking_requested':True})
          else:
             return False
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
