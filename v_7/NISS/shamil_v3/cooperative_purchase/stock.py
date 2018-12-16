# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv
from osv import fields
import time
from datetime import datetime

class stock_partial_picking_cooprative_inhirt(osv.osv_memory):

    _inherit = 'stock.partial.picking'

    def default_get(self, cr, uid, fields, context=None):
        """ 
        To get default values for the wizard.

        @param fields: List of fields for which we want default values
        @return: Dictionary which of fields with values.
        """
        if context is None:
            context = {}
        pick_obj = self.pool.get('stock.picking')
        currency_obj = self.pool.get('res.currency')
        res = super(stock_partial_picking_cooprative_inhirt, self).default_get(cr, uid, fields, context=context)
    
        for pick in pick_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            has_product_cost = (pick.type == 'in')
            for m in pick.move_lines:
                if m.state in ('done','cancel') :
                    continue
                if m.location_dest_id.usage == m.location_id.usage=='supplier':
                     continue
                if has_product_cost and m.product_id.cost_method == 'average':
                    # We use the original PO unit purchase price as the basis for the cost, expressed
                    # in the currency of the PO (i.e the PO's company currency)
                    list_index = 0
                    price =  m.price_unit
                    if 'move_ids' in res.keys() :
                        for item in res['move_ids']:
                            if item['move_id'] == m.id:
                                currency_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
                                item['cost'] = price
                                item['currency'] = currency_id
                            list_index += 1
                
        return res

class stock_partial_move_cooprative_inhirt(osv.osv_memory):
    """ 
    To add clearance price to the product price unit """

    _inherit = "stock.partial.move"

    def default_get(self, cr, uid, fields, context=None):
        """ 
        To get default values for the object.

        @param fields: List of fields for which we want default values
        @return: Dictionary which of fields with values.
        """
        if context is None:
            context = {}
        res = super(stock_partial_move_cooprative_inhirt, self).default_get(cr, uid, fields, context=context)
        move_obj = self.pool.get('stock.move')
        currency_obj = self.pool.get('res.currency')
        for m in move_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            if m.location_dest_id.usage==m.location_id.usage=='supplier':
               continue
            if m.picking_id.type == 'in' and m.product_id.cost_method == 'average':
                    # We use the original PO unit purchase price as the basis for the cost, expressed
                    # in the currency of the PO (i.e the PO's company currency)
                    list_index = 0
                    price = m.price_unit
                    if 'move_ids' in res.keys() :
                        for item in res['move_ids']:
                            if item['move_id'] == m.id:
                                currency_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
                                item['cost'] = price
                                item['currency'] = currency_id
                            list_index += 1
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
