# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields,orm
import time
import netsvc
from tools.translate import _

class employee_missions(orm.Model):
    """
    To manage employee_missions """ 

    _inherit = "hr.employee.mission"
    _columns={
           'fuel_requested': fields.boolean('Fuel Requested', readonly=True),
            }

    def request_fuel(self,cr,uid,ids,context=None):
       """
       Request fuel and car for mission from mission if the transport type is car.
        
       @param ids: :List of id of mission
       @return: True or False
       """
       for mission in self.browse(cr,uid,ids,context=context):
          fuel_request_obj = self.pool.get('fuel.request')
          if mission.transport in ('1','4') and not mission.fuel_requested:
             info = mission.name + ' ' + mission.start_date + ' / ' + mission.end_date
             request_dict={
                  'description': info,
    		      'purpose': 'mission',
		          'date_of_travel':mission.start_date,
		          'date_of_return':mission.end_date,
                           
		}
             request_id = fuel_request_obj.create(cr,uid,request_dict,context=context)
             
             #creating mission request in confirmed_d state
             wf_service = netsvc.LocalService("workflow")
             wf_service.trg_validate(uid, 'fuel.request', request_id, 'confirmed_s', cr)
             wf_service.trg_validate(uid, 'fuel.request', request_id, 'confirmed_d', cr)
             
             
             for employee in mission.mission_line:
                cr.execute("INSERT into fuel_reuest_emp_rel values(%s,%s)",(request_id,employee.employee_id.id,))
             return self.write(cr,uid,ids,{'fuel_requested':True})
          else:
             return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
