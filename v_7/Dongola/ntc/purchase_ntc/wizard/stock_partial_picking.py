# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class stock_partial_picking(osv.osv_memory):
      _inherit = "stock.partial.picking"
      
      
      
      def do_partial(self, cr, uid, ids, context=None):
        requestion_lines= []
        request = context.get('request', False)
        wf_service = netsvc.LocalService("workflow")
        #super(stock_partial_picking,self).do_partial(self, cr, uid, ids, context=context)
        if request:
           super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)
           partial = self.browse(cr, uid, ids[0], context=context)
           pick_rec = self.pool.get('stock.picking').browse(cr,uid,[partial.picking_id.id])[0]  
           wf_service.trg_validate(uid, 'stock.picking', pick_rec.id,
                                                               'send_to_purchase', cr)  
        else:
            return super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)

        return True




class stock_picking(osv.osv):


      _inherit = "stock.picking"


      
      def action_done(self, cr, uid, ids, context=None):
        """
        Checks if Goods avaiable in stock after Purchases Procedure done

        @return: True
        """
        wf_service = netsvc.LocalService('workflow')
        super(stock_picking, self).action_done(cr, uid, ids, context=context)
        picking_obj = self.pool.get('stock.picking')
        for picking_record in self.browse(cr,uid,ids):
            if picking_record.type == 'in' :
             if picking_record.purchase_id:
               if picking_record.purchase_id.requisition_id.origin :
                  picking_src_origin = picking_record.purchase_id.requisition_id.origin
                  picking_src_id = picking_obj.search(cr , uid , [('name' , '=' , picking_src_origin)])
                  for pick_record in picking_obj.browse(cr ,uid , picking_src_id ):
                      if pick_record.state == 'in_progress' :
                         wf_service.trg_validate(uid, 'stock.picking', pick_record.id,
                                                               'goods_recieved', cr)       
        return True
    
    
    
    
    
      def goods_recieved(self, cr, uid, ids, context=None):
          
          """ Change State To Picking confirmed """
          wf_service = netsvc.LocalService("workflow")
          for rec in self.browse(cr,uid,ids):
              wf_service.trg_validate(uid, 'stock.picking', rec.id ,
                                                                   'button_confirm', cr) 
          return True
          
          
          
          
          
          
          
          