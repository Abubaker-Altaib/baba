# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import osv
from osv import fields
from tools.translate import _

#from common_tools.voucher import action_move_line_create as action_move_line_create

class purchase(osv.osv):
    """ 
    To add transportaion to purchase order and restrict order workflow """
   
    _inherit = 'purchase.order'
    _columns = {
        'transportation_ids':fields.one2many('transportation.order', 'purchase_order_id' , 'Transportation'),              
    }
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        """ 
        Workflow function override to restrict the workflow of purchase if its transportaion not done yet.

        @return: True
        """
        for purchases in self.browse(cr, uid, ids):
            if purchases.transportation_ids not in []:
               for clearnace in purchases.transportation_ids:
                   if clearnace.state not in ['done','cancel']:
                       raise osv.except_osv(_('not complete process!'), _(' you have transportation that not complete yet..'))                     
        return super(purchase, self).wkf_confirm_order(cr, uid, ids, context)

  
    

class purchase_line(osv.osv):
    """ 
    To add clearance price to purchase order line """

    _inherit = 'purchase.order.line'  
    _columns = {   
    'transportation_price': fields.float('Transportation Price',  digits=(16,2)),
               }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
