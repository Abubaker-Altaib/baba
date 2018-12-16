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
    

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get in order to change the label of the process button and the separator accordingly to the shipping type
        if context is None:
            context={}
        res = super(stock_partial_picking, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        type = context.get('default_type', False)
        request = context.get('request', False)
        if type:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//button[@name='do_partial']"):
                if type == 'in':
                    node.set('string', _('_Receive'))
                elif type == 'out':
                    if request:
                        node.set('string', _('_Ask New Products'))
                    else:    
                        node.set('string', _('_Deliver'))
            for node in doc.xpath("//separator[@name='product_separator']"):
                if type == 'in':
                    node.set('string', _('Receive Products'))
                elif type == 'out':
                    if request:
                        node.set('string', _('Request Products'))
                    else:
                        node.set('string', _('Deliver Products'))
            res['arch'] = etree.tostring(doc)
        return res
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        request = context.get('request', False)
        picking_id, = context.get('active_ids', [])
        if request:
            if 'move_ids' in fields:
                picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
                moves = [self._partial_move_for1(cr, uid, m, context=context) for m in picking.move_lines if m.state == 'confirmed']
                res.update(move_ids=moves)
        return res
    
    def _partial_move_for1(self, cr, uid, move, context=None):
        partial_move = {
            'product_id' : move.product_id.id,
            'quantity' : move.product_qty ,
            'product_uom' : move.product_uom.id,
            'prodlot_id' : move.prodlot_id.id,
            'move_id' : move.id,
            'location_id' : move.location_id.id,
            'location_dest_id' : move.location_dest_id.id,
        }
        return partial_move
    
    def do_partial(self, cr, uid, ids, context=None):
        requestion_lines= []
        request = context.get('request', False)
        wf_service = netsvc.LocalService("workflow")
        if request:
            assert len(ids) == 1, 'request product processing may only be done one at a time.'
            requestion_obj = self.pool.get('purchase.requisition')
            uom_obj = self.pool.get('product.uom')
            partial = self.browse(cr, uid, ids[0], context=context)

            for wizard_line in self.pool.get('stock.picking').browse(cr,uid,[partial.picking_id.id])[0].move_lines:
                line_uom = wizard_line.product_uom
                move_id = wizard_line.id
    
                #Quantiny must be Positive
                if wizard_line.product_qty < 0:
                    raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))
    
                #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
                qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.product_qty, line_uom.id)
    
                if line_uom.factor and line_uom.factor <> 0:
                    if float_compare(qty_in_line_uom, wizard_line.product_qty, precision_rounding=line_uom.rounding) != 0:
                        raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.product_qty, line_uom.name, line_uom.rounding, line_uom.name))
                if move_id:                   
                    initial_uom = wizard_line.product_uom
                    qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.product_qty, initial_uom.id)
                    without_rounding_qty = (wizard_line.product_qty / line_uom.factor) * initial_uom.factor
                    if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                        raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.product_qty, line_uom.name, wizard_line.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
               
                    
                    line = {'name': wizard_line.name,
                            'product_id': wizard_line.product_id.id,
                            'product_qty': wizard_line.product_qty,
                            'product_uom_id': wizard_line.product_uom.id,
                    } 
                    requestion_lines.append((0, 0, line))
            if requestion_lines:
               if partial.picking_id.purchase_requisition_id:
                  raise osv.except_osv(_('Duplication!'), _('You are Already Created Purchase Requisition Before "%s" ') % (partial.picking_id.purchase_requisition_id.name) ) 
               requestion_id = requestion_obj.create(cr, uid , {
                    
                    'origin': partial.picking_id.name,
                    'department_id': partial.picking_id.department_id.id,
                    'category_id':partial.picking_id.category_id.id,
                    'line_ids': requestion_lines}, context = context)
            
            self.pool.get('stock.picking').write( cr, uid, partial.picking_id.id, {'purchase_requisition_id' : requestion_id})
            wf_service.trg_validate(uid, 'purchase.requisition', requestion_id, 'draft_to_approve', cr)
        else:
            return super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)

        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

