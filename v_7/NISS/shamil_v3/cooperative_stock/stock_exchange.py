# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


import time
from openerp.osv import osv,fields
from openerp import netsvc
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp



class exchange_order(osv.osv):

     _inherit = "exchange.order"

     def action_confirm_order(self, cr, uid, ids, context=None):

         """" This Function For Convert Transition From Confirm To Done State 
             When Order For Cooperative Company """
         wf_service = netsvc.LocalService("workflow")
         for record in self.browse(cr,uid,ids):
            if record.location_dest_id.co_operative == True :
               if not record.order_line:
                  raise osv.except_osv(_('Error !'), _('You can not confirm the order without  order lines.'))
               #if not record.department_id.manager_id or  not record.department_id.manager_id.user_id or  record.department_id.manager_id.user_id.id!=uid:
                    #raise osv.except_osv(_('Error !'), _('Department  manager who only can confirm this order.'))
               self.write(cr, uid,record.id,{'state':'approved'})
               wf_service.trg_validate(uid, 'exchange.order', record.id, 'exchange_cooperative_picking', cr) 
            else :
               return super(exchange_order, self).action_confirm_order(cr, uid,  ids, context=context)
         return True



      












