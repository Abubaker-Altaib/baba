# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
#
# Model definition
#
class stock_move(osv.Model):
    """
    TO remove pricelist """

    _inherit = 'stock.move'
    _columns = {
        'note': fields.text('Specification'),
    }


    def _create_chained_picking(self, cr, uid, pick_name, picking, purchase_type, move, context=None):
        """
        This method creates chained picking and fix the problem of adding accounts for picking.

        @param pick_name: The name from the picking which is created
        @param picking: The id of the picking which is created
        @param purchase_type: Purchase type 
        @param move: The move id 
        @return: id of creating picking 
        """
        res = super(stock_move, self)._create_chained_picking(cr, uid, pick_name, picking, purchase_type, move, context=context)
        if picking.purchase_id:
            self.pool.get('stock.picking').write(cr, uid, [res], {'purchase_id': picking.purchase_id.id})
            self.pool.get('stock.picking').write(cr, uid, [res], {'invoice_state': picking.invoice_state})
        return res

    def _get_reference_accounting_values_for_valuation(self, cr, uid, move, context=None):
        """
        This method Overrides the default stock valuation to take into account the currency that was specified
        on the purchase order in case the valuation data was not directly specified during picking
        confirmation.

        @param move: The move id 
        @return: price and currency  
        """
        reference_amount, reference_currency_id = super(stock_move, self)._get_reference_accounting_values_for_valuation(cr, uid, move, context=context)
        if move.product_id.cost_method != 'average' or not move.price_unit:
            # no average price costing or cost not specified during picking validation, we will
            # plug the purchase line values if they are found.
            if move.purchase_line_id and move.picking_id.purchase_id.company_id:
                reference_amount, reference_currency_id = move.purchase_line_id.price_unit, move.picking_id.purchase_id.company_id.currency_id.id
        return reference_amount, reference_currency_id

#----------------------------------------------------------
# Stock Picking In
#----------------------------------------------------------
class stock_picking_in(osv.osv):
    _inherit="stock.picking.in"
    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order',readonly='True',
            ondelete='set null', select=True),
    }

#
# Model definition
#

class stock_picking(osv.osv):
    """
    To let functions read data from company and purchase order and remove price list """
    _inherit = 'stock.picking'
    # To change purchase_id to be readonly 
    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order',readonly='True',
            ondelete='set null', select=True),
    }
    _defaults = {
        'purchase_id': False,
    }


    def get_currency_id(self, cursor, user, picking):
        """ 
        Get currency from company instaed of pricelist.

        @param picking: The picking id
        @return: returns currency id  
        """
        if picking.purchase_id:
            return picking.purchase_id.company_id.currency_id.id
        return super(stock_picking, self).get_currency_id(cursor, user, picking)


    def _get_taxes_invoice(self, cursor, user, move_line, type):
        """ 
        To get taxes from purchase_order instead of getting them from purchase_order_line.

        @param move_line: The move id 
        @return: dictionary contain the id of the taxes  
        """
        if move_line.purchase_line_id:
            return [x.id for x in move_line.purchase_line_id.order_id.taxes_id]
        return super(stock_picking, self)._get_taxes_invoice(cursor, user, move_line, type)

    def _get_account_analytic_invoice(self, cursor, user, picking, move_line):
        """
        Overridden to send the analytic account from purchase order if the picking related to purchase order.

        @param picking: The picking id
        @param move_line: The move id 
        @return: returns account id  
        """
        if move_line.purchase_line_id:
            return move_line.purchase_line_id.order_id.account_analytic_id.id
        return super(stock_picking, self)._get_account_analytic_invoice(cursor, user, picking, move_line)



 
class stock_partial_picking(osv.osv_memory):
    """
    TO get the currency from company not from pricelist """

    _inherit = 'stock.partial.picking' 

    def _product_cost_for_average_update(self, cr, uid, move):
        """ 
        Overridden to inject the purchase price as true 'cost price' when processing.

        @param move: The move id 
        @return: returns price and currency  
        """
        if move.picking_id.purchase_id:
        	price=move.purchase_line_id.price_unit_total
        	currency_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
        	return {'cost': price,
                    'currency': currency_id
                    }
        
        return super(stock_partial_picking, self)._product_cost_for_average_update(cr, uid, move)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
