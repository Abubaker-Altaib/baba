# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields,orm,osv
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
          fuel_request_obj = self.pool.get('fleet.vehicle.log.fuel')
          if mission.transport in ('1','4') and not mission.fuel_requested:
             info = 'Mission:\t' + mission.name + '\nStart date:\t' + mission.start_date + ' - End date:\t' + mission.end_date + '\nTravel path:\t' + mission.travel_path
             request_dict={
                  'notes': info,
    		      'purpose': 'mission',
                  'payment_method':'plan',
                  'plan_type':'extra_fuel',
                  'state':'draft',
		          #'date_of_travel':mission.start_date,
		          #'date_of_return':mission.end_date,
                           
		}
             request_id = fuel_request_obj.create(cr,uid,request_dict,context=context)
             
             #creating mission request in confirmed_d state
             #wf_service = netsvc.LocalService("workflow")
             #wf_service.trg_validate(uid, 'fuel.request', request_id, 'confirmed_s', cr)
             #wf_service.trg_validate(uid, 'fuel.request', request_id, 'confirmed_d', cr)
             
             
             #for employee in mission.mission_line:
                #cr.execute("INSERT into fuel_reuest_emp_rel values(%s,%s)",(request_id,employee.employee_id.id,))
             return self.write(cr,uid,ids,{'fuel_requested':True})

    def mission_approved(self, cr, uid, ids, context=None):
        """
        Workflow method change record state to 'approved' and 
        Transfer Mission mission_fee to move

        @return: Boolean True
        """
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        account_period_obj = self.pool.get('account.period')
        for mission in self.browse(cr, uid, ids, context=context):
            mission_amount = mission.mission_fee
            if mission_amount <= 0:
                raise osv.except_osv(_('Warning!'),_('Mission fee should be more than zero'))
            
            if mission.mission_id.fees_account_id and mission.mission_id.journal_id and mission.mission_id.account_analytic_id:
                date = time.strftime('%Y-%m-%d')
                period = account_period_obj.find(cr, uid, dt=date, context={'company_id':mission.company_id.id})[0]
                voucher_dict = {
                    'company_id':mission.company_id.id,
                    'journal_id':mission.mission_id.journal_id.id,
                    'account_id':mission.mission_id.fees_account_id.id,
                    'period_id': period,
                    'name': mission.name + ' - ' + mission.start_date,
                    'amount':mission_amount,
                    'type':'purchase',
                    'date': date,
                    'reference':'HR/Mission/' + mission.name + ' - ' + mission.start_date,
 					'department_id': mission.department_id.id,
					'currency': mission.mission_id.fees_currency_id.id,
               }
                voucher = voucher_obj.create(cr, uid, voucher_dict, context=context)
                voucher_line_dict = {
                     'voucher_id':voucher,
                     'account_id':mission.mission_id.fees_account_id.id,
                     'account_analytic_id':mission.mission_id.account_analytic_id.id,
                     'amount':mission_amount,
                     'type':'dr',
                }
                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
                
                vouch = voucher_obj.browse(cr, uid, voucher, context=context)
                self.request_fuel(cr, uid, ids, context=context)
                self.create_grant_rights(cr,uid,ids,context=context)
                return self.write(cr, uid, ids, {'state':'approved', 'voucher_number': vouch.number, })
            else:
                raise osv.except_osv(_('Error!'),_("Please enter mission accounting details at the configuration of the mission destination"))
        self.create_grant_rights(cr,uid,ids,context=context)
        return self.write(cr, uid, ids, {'state':'approved'}, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
