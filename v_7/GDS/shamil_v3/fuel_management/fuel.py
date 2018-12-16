# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
import netsvc
from tools.translate import _
import time

#----------------------------------------
# Class fuel picking inherit from stock picking
#----------------------------------------

class fuel_picking(osv.osv):
    """
    To manage fuel picking """

    _inherit = "stock.picking"
    _name = "fuel.picking"
    
    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence. 

        @param vals: dictionary of values
        @return: new object id 
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'fuel.picking.' + vals['type']
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(fuel_picking, self).create(cr, user, vals, context)
        return new_id
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict 
        @return: id of the newly created record  
        """
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, id, context=context)
        move_obj=self.pool.get('stock.move')
        if ('name' not in default) or (picking_obj.name=='/'):
            seq_obj_name =  'fuel.picking.' + picking_obj.type
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            default['origin'] = ''
            default['backorder_id'] = False
        res=super(fuel_picking, self).copy(cr, uid, id, default, context)
        if res:
            picking_obj = self.browse(cr, uid, res, context=context)
            for move in picking_obj.move_lines:
                move_obj.write(cr, uid, [move.id], {'tracking_id': False,'prodlot_id':False, 'move_history_ids2': [(6, 0, [])], 'move_history_ids': [(6, 0, [])]})
        return res
   
    def unlink(self, cr, uid, ids, context=None):
        """
        Disable delete fuel picking record

        @return: Boolean True
        """
        raise osv.except_osv(_('Invalid action !'), _('You cannot delete a fuel picking order, you just can cancel it.'))
        return True
   
    def draft_validate(self, cr, uid, ids, context=None):
        """ 
        Validates picking directly from draft state.

        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        self.draft_force_assign(cr, uid, ids)
        for pick in self.browse(cr, uid, ids, context=context):
            move_ids = [x.id for x in pick.move_lines]
            self.pool.get('stock.move').force_assign(cr, uid, move_ids)
            wf_service.trg_write(uid, 'fuel.picking', pick.id, cr)
        return self.action_process(
            cr, uid, ids, context=context)
    
    def draft_force_assign(self, cr, uid, ids, *args):
        """ 
        Confirms picking directly from draft state.

        @param args,kwargs the arguments, in list and dict respectively
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            if not pick.move_lines:
                raise osv.except_osv(_('Error !'),_('You can not process picking without stock moves'))
            wf_service.trg_validate(uid, 'fuel.picking', pick.id,
                'button_confirm', cr)
        return True
    
    def test_finished(self, cr, uid, ids):
        """ 
        Tests whether the move is in done or cancel state or not.

        @return: True or False
        """
        move_ids = self.pool.get('stock.move').search(cr, uid, [('fuel_picking_id', 'in', ids)])
        for move in self.pool.get('stock.move').browse(cr, uid, move_ids):
            if move.state not in ('done', 'cancel'):

                if move.product_qty != 0.0:
                    return False
                else:
                    move.write({'state': 'done'})
        return True
     
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ 
        Makes partial picking and moves done.

        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """ 
        return self.action_done(cr, uid, ids, context)
        
    def action_process(self, cr, uid, ids, context=None):
        """ 
        call fuel partial picking wizard.

        @return: fuel_partial_picking wizard
        """ 
        if context is None: context = {}
        context = dict(context, active_ids=ids, active_model=self._name)
        partial_id = self.pool.get("fuel.partial.picking").create(cr, uid, {}, context=context)
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'fuel.partial.picking',
            'res_id': partial_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }
        
    def action_done(self, cr, uid, ids, context=None):
        """ 
        Workflow function to change state to done and check 
        if stock moves exist

        @return: Boolean True
        """
        if context is None:
            context = {}
            
        for pick in self.browse(cr, uid, ids,context):
            if not pick.move_lines:
                raise osv.except_osv(_('No moves !'), _('You cannot complete order without moves'))  
                
        move_obj = self.pool.get('stock.move')
        for inv in self.browse(cr, uid, ids, context=context):
            move_ids = [x.id for x in inv.move_lines]
            move_obj.action_done(cr, uid, move_ids, context=context)
            # ask 'stock.move' action done are going to change to 'date' of the move,
            # we overwrite the date as moves must appear at the picking date.
            move_obj.write(cr, uid, move_ids, {'date': inv.date}, context=context)
            self.write(cr, uid, [inv.id], {'state':'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
    
    _columns = {
    'department_id':  fields.many2one('hr.department', 'Department'),
    'move_lines': fields.one2many('stock.move', 'fuel_picking_id', 'Internal Moves', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
    'fuel_request_id' : fields.many2one('fuel.request','Request for Fuel No.', readonly=1, help="It referes to Fuel Picking from which this Fuel Request created."),
    'fuel_plan_id' : fields.many2one('fuel.plan','Fuel plan.', readonly=1, help="It referes to Fuel plan from which this Fuel picking created."),
    }   
    
    _defaults = {
                }
    

class stock_move(osv.osv):
    """
    To add fuel managment to stock move """

    _inherit = "stock.move"
    
    _columns = {
        'fuel_picking_id': fields.many2one('fuel.picking', 'Fuel Reference', select=True,states={'done': [('readonly', True)]}), 
        'fuel_origin': fields.related('fuel_picking_id','origin',type='char', size=64, relation="fuel.picking", string="Fuel Origin", store=True),      
               }   
    

class stock_location(osv.osv):
    """
    To add fuel location to stock location"""

    _inherit = "stock.location"
    
    _columns = {
        'fuel_location': fields.boolean('Fuel location', help="By checking the fuel field, you determine this location as fuel location"),
                }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
