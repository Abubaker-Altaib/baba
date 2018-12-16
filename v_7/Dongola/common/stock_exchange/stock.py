# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv,fields
import time
from openerp.tools.translate import _

#----------------------------------------------------------
# Inherit of stock move to add the link to the Rec line
#----------------------------------------------------------
class stock_move(osv.Model):
    _inherit = 'stock.move'
    _columns = {
        'exchange_line_id': fields.many2one('exchange.order.line','Exchange Order Line', ondelete='set null', readonly=True),
    }
    def _create_chained_picking(self, cr, uid, pick_name, picking, ptype, move, context=None):
        """
        This method creates chained picking and write exchange_id in stock picking move.

        @param pick_name: The name from the picking which is created
        @param picking: The id of the picking which is created
        @param ptype: Purchase type 
        @param move: The move id 
        @return: id of creating picking
        """
        res = super(stock_move, self)._create_chained_picking(cr, uid, pick_name, picking, ptype, move, context=context)
        if picking.exchange_id:
            self.pool.get('stock.picking').write(cr, uid, [res], {'exchange_id': picking.exchange_id.id})
        return res

    def create(self, cr, uid, vals, context={}):
        """
        Inherit create function to add constrain in location
        @param vals: dictionary of object values
        @return: super of stock_move or raise
        """
        if 'location_dest_id'  in vals :
            if vals['location_dest_id']:
                return super(stock_move, self).create(cr, uid, vals, context=context) 
        raise osv.except_osv(_('Error!'), _('Please insert destination location!.'))      

    def _create_account_move_line(self, cr, uid, move,date, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):

		"""
		Generate the account.move.line values to post to track the stock valuation difference due to the
		processing of the given stock move.
        @param move: move_id
        @param date: date of move line
        @param src_account_id: account_id of location
        @param dest_account_id: account_id of destnation location
        @param reference_amount: amount
        @param reference_currency_id: currency_id
        @return: list of tuple [(0,0,move_line)] 
		"""
		# prepare default values considering that the destination accounts have the reference_currency_id as their main currency
		partner_id = (move.picking_id and move.picking_id.partner_id and move.picking_id.partner_id.id) or False
		acc_bud_confirm_id = (move.exchange_line_id and move.exchange_line_id.order_id and move.exchange_line_id.order_id.acc_bud_confirm_id.id) or False
		period = self.pool.get('account.period').find(cr, uid, dt=date, context=context)
		if move.picking_id and move.picking_id.type=='in':
			debit_line_vals = {
					'name': move.name,
					'product_id': move.product_id and move.product_id.id or False,
					'quantity': move.product_qty,
					'ref': move.picking_id and move.picking_id.name or False,
					'date': date,
					'partner_id': partner_id,
					'debit': reference_amount,
					'account_id': dest_account_id,
					'period_id':period[0], 
			
			}
			credit_line_vals = {
					'name': move.name,
					'product_id': move.product_id and move.product_id.id or False,
					'quantity': move.product_qty,
					'ref': move.picking_id and move.picking_id.name or False,
					'date': date,
					'partner_id': partner_id,
					'credit': reference_amount,
					'account_id': src_account_id,
					'period_id':period[0],
					'analytic_account_id':move.picking_id and move.picking_id.analytic_account_id.id or False,


			}
		else:
			debit_line_vals = {
					'name': move.name,
					'product_id': move.product_id and move.product_id.id or False,
					'quantity': move.product_qty,
					'ref': move.picking_id and move.picking_id.name or False,
					'date': date,
					'partner_id': partner_id,
					'debit': reference_amount,
					'account_id': dest_account_id,
					'analytic_account_id':move.picking_id and move.picking_id.analytic_account_id.id or False, 
					'period_id':period[0],
					'budget_confirm_id':acc_bud_confirm_id, 
			}
			credit_line_vals = {
					'name': move.name,
					'product_id': move.product_id and move.product_id.id or False,
					'quantity': move.product_qty,
					'ref': move.picking_id and move.picking_id.name or False,
					'date': date,
					'partner_id': partner_id,
					'credit': reference_amount,
					'account_id': src_account_id,
					'period_id':period[0], 
			}

		account_obj = self.pool.get('account.account')
		src_acct, dest_acct = account_obj.browse(cr, uid, [src_account_id, dest_account_id], context=context)
		src_main_currency_id = src_acct.company_id.currency_id.id
		dest_main_currency_id = dest_acct.company_id.currency_id.id
		cur_obj = self.pool.get('res.currency')
		if reference_currency_id != src_main_currency_id:
			# fix credit line:
			credit_line_vals['credit'] = cur_obj.compute(cr, uid, reference_currency_id, src_main_currency_id, reference_amount, context=context)
			if (not src_acct.currency_id) or src_acct.currency_id.id == reference_currency_id:
				credit_line_vals.update(currency_id=reference_currency_id, amount_currency=reference_amount)
		if reference_currency_id != dest_main_currency_id:
			# fix debit line:
			debit_line_vals['debit'] = cur_obj.compute(cr, uid, reference_currency_id, dest_main_currency_id, reference_amount, context=context)
			if (not dest_acct.currency_id) or dest_acct.currency_id.id == reference_currency_id:
				debit_line_vals.update(currency_id=reference_currency_id, amount_currency=reference_amount)

		return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]



#----------------------------------------------------------
# Inherit of picking to add the link to the Rec
#----------------------------------------------------------
class stock_picking(osv.Model):
    _inherit = 'stock.picking'
    _columns = {
        'exchange_id': fields.many2one('exchange.order', 'Exchange Order',
            ondelete='set null', select=True),
    }
    _defaults = {
        'exchange_id': False,
    } 



#----------------------------------------------------------
# Stock Location (Inherit)
#----------------------------------------------------------
class stock_location(osv.Model):
    _inherit = "stock.location"

    def picking_type_get(self, cr, uid, from_location, to_location, context=None):
        """ Gets type of picking.
        @param from_location: Source location
        @param to_location: Destination location
        @return: Location type
        """
        result = super(stock_location, self).picking_type_get(cr, uid, from_location, to_location, context=context)
        if (from_location.usage == 'internal') and (to_location and to_location.usage in ('customer', 'supplier', 'transit')):
            result = 'out'
        if (from_location.usage == 'internal') and (to_location and to_location.usage =='transit' and to_location.chained_location_type=='none' ):
            result = 'internal'
        elif (from_location.usage in ('supplier', 'customer', 'transit')) and (to_location.usage in  ('internal', 'customer')):
            result = 'in'
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
