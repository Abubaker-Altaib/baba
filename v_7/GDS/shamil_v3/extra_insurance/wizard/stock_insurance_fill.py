# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

#----------------------------------------
# Class stock fill insurance
#----------------------------------------
class stock_fill_insurance(osv.osv_memory):
    _name = "stock.insurance.wiz.fill"
    _description = "stock Fill Insurance"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'recursive': fields.boolean("Include children",help="If checked, items contained in child location of selected location will be included as well."),
        'set_qty_zero': fields.boolean("Set Qty to zero",help="If checked, all items qty will be set to zero."),
        'qty_zero': fields.boolean("Include zero Qty",help="If checked, all items with qty zero will be ."),
    }
    def view_init(self, cr, uid, fields_list, context=None):
        """
           Creates view dynamically and adding fields at runtime.
           @return: Boolean True.
        """
        if context is None:
            context = {}
        super(stock_fill_insurance, self).view_init(cr, uid, fields_list, context=context)

        if len(context.get('active_ids',[])) > 1:
            raise osv.except_osv(_('Error!'), _('You cannot perform this operation on more than one Location.'))

        if context.get('active_id', False):
            insurance = self.pool.get('stock.insurance').browse(cr, uid, context.get('active_id', False))

            if not insurance.state in ('draft'):
                raise osv.except_osv(_('Warning!'), _('Stock insurance is already confirmed.'))
        return True

    def fill_insurance(self, cr, uid, ids, context=None):
        """ 
           Method To Import items according to stock available in the selected buildings.
           @return: Dictionary
        """
        if context is None:
            context = {}
            
        stock_ins_line_obj = self.pool.get('stock.insurance.line')
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        stock_location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        if ids and len(ids):
            ids = ids[0]
        else:
            return {'type': 'ir.actions.act_window_close'}
        fill_insurance = self.browse(cr, uid, ids, context=context)
        res = {}
        res_location = {}


        if fill_insurance.recursive:
            location_ids = location_obj.search(cr, uid, [('location_id',
                             'child_of', [fill_insurance.location_id.id])], order="id",
                             context=context)
        else:
            location_ids = [fill_insurance.location_id.id]


        res = {}
        flag = False

        for location in location_ids:
            datas = {}
            res[location] = {}
            move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done')], context=context)

            for move in move_obj.browse(cr, uid, move_ids, context=context):
                prod_id = move.product_id.id
                if move.location_dest_id.id == location:
                    qty = uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)
                else:
                    qty = -uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)


                if datas.get((prod_id)):
                    qty += datas[(prod_id)]['product_qty']

                datas[(prod_id)] = {'product_id': prod_id, 'location_id': location, 'product_qty': qty, 'product_uom': move.product_id.uom_id.id,'unit_price':move.product_id.standard_price}

            if datas:
                flag = True
                res[location] = datas

        if not flag:
            raise osv.except_osv(_('Warning !'), _('No product in this location.'))

        for stock_move in res.values():
            for stock_move_details in stock_move.values():
                stock_move_details.update({'insurance_id': context['active_ids'][0]})
                domain = []

                if fill_insurance.set_qty_zero:
                    stock_move_details.update({'product_qty': 0})

                for field, value in stock_move_details.items():
                    if not fill_insurance.qty_zero and stock_move_details['product_qty'] > 0 :
                        domain.append((field, '=', value))
                    elif fill_insurance.qty_zero:
                        domain.append((field, '=', value))


                line_ids = stock_ins_line_obj.search(cr, uid, domain, context=context)

                if not line_ids:
                    stock_ins_line_obj.create(cr, uid, stock_move_details, context=context)

        return {'type': 'ir.actions.act_window_close'}


stock_fill_insurance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
