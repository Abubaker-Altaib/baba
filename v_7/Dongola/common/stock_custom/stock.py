# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp import tools
import netsvc
from openerp.tools.translate import _
from openerp.osv import osv, fields, orm
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from admin_affairs.model.email_serivce import send_mail


class product_product(osv.Model):

    _inherit = "product.product"

    _columns = {
        'valuation': fields.selection([('manual_periodic', 'Periodical (manual)'),('real_time','Real Time (automated)'),
                                       ('special_real_time','Inventory/Scrap Real Time (automated)')], 'Inventory Valuation', required=True,
                                        help="If real-time valuation is enabled for a product, the system will automatically write journal entries corresponding to stock moves." \
                                             "The inventory variation account set on the product category will represent the current inventory value, and the stock input and stock output account will hold the counterpart moves for incoming and outgoing products.\n"\
                                             "If inventory/scrap real-time valuation is enabled for a product, the system will automatically write journal entries corresponding to inventory/scrap moves"),
    }

    _sql_constraints = [('default_code_unique', 'unique(default_code)','Default Code must be Unique')]

class stock_move(osv.Model):





    def _real_stock_dest(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute real stock destnation quanity 
        @param field_names: Name of field
        @param args: other arguments
        @return Dictinory of value
        """
        res = {}
        if context is None:
            context = {}
        stock_location_obj=self.pool.get('stock.location')

        for line in self.browse(cr, uid, ids, context=context):
            context.update({'uom': line.product_id.uom_id.id,})
            res[line.id] = {
                'stock_available': 0, 
                #'product_name_fnc': line.product_id.name,
            }
            
            location_id = line.picking_id.location_id and line.picking_id.location_id.id 
            if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
               res[line.id] = {
                'stock_available': stock_location_obj._product_get(cr, uid, location_id, [line.product_id.id], context = context)[line.product_id.id],
                #'product_name_fnc': line.product_id.name, 
                              } 
        return res
    
    
    def action_confirm(self, cr, uid, ids, context=None):
        """ Inherit  action_confirm to write Product Name.
        @return: True
        """
        super( stock_move, self).action_confirm(cr, uid, ids, context=context)
        for line in self.browse(cr,uid,ids):
            self.write(cr,uid,ids,{'product_name_spec' : line.product_id.name})
        return True
    
    
    def _check_products(self, cr, uid, ids, context=None):
        """ 
        Constrain function to check the product, should be in one order line.
        @return Boolean True or False
        """
        line = self.browse(cr, uid, ids[0], context=context)
        pord = self.search(cr, uid, [ ('product_id', '=', line.product_id.id), ('picking_id', '=', line.picking_id.id)])
        if len(pord) > 1:
            return False
        return True


    _inherit = "stock.move"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Source Location', required=False, select=True,states={'done': [('readonly', True)],'confirmed': [('required', True)]}, help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations."),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', required=False,states={'done': [('readonly', True)],'confirmed': [('required', True)]}, select=True, help="Location where the system will stock the finished products."),
        'state': fields.selection([
                                    ('draft', 'New'),('complete', 'Complete'),
                                    ('cancel', 'Cancelled'), ('waiting', 'Waiting Another Move'),
                                    ('confirmed', 'Waiting Availability'), ('assigned', 'Available'),
                                    ('validated' , 'Waiting Approval'),
                                    ('done', 'Done')], 'Status', readonly=True, select=True,),
        'qty':fields.float("Quantity"),
        #'product_name_fnc': fields.function(_real_stock_dest,type="char", method=True , multi='sums', string="Product Name Desc",store=True),
        'product_name_spec': fields.char('Product Reference Name', size=128, readonly=True,),
        'stock_available': fields.function(_real_stock_dest,type="integer", method=True , multi='sums', string="Available",),

    }

 

    _constraints = [

        (_check_products,
          'Product must be Unique ',
           ['product_id']),
    ]
    

    def _default_location_destination(self, cr, uid, context=None):
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        #if picking_type == 'out':
            #if context.get('stock_journal_id', False):
                #location_out = self.pool.get('stock.journal').browse(cr, uid, context['stock_journal_id'], context).location_id
                #location_id = location_out and location_out.id or False
        if not location_id:
            location_id = super(stock_move, self)._default_location_destination(cr, uid, context=context)
        return location_id

    _defaults = {
        'location_dest_id': _default_location_destination
    }

    def onchange_qty(self, cr, uid, ids, qty):
        return {'value': 
        {
            'product_qty':qty
        }
        }
    
    
        
        
        
    def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
                          product_uom, product_uos):

        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_qty: Changed Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'product_uos_qty': 0.00,
                  'qty':product_qty,
          }
        warning = {}
        if (not product_id) or (product_qty <=0.0):
            result['product_qty'] = 0.0
            return {'value': result}

#         product_obj = self.pool.get('product.product')
#         uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])
#         acctual_qty = product_obj.read(cr, uid, product_id, ['qty_available'])
#         acctual_qty = acctual_qty['qty_available']
#         if ( acctual_qty <= 0 ) or ( acctual_qty < product_qty):
#             warning.update({
#                        'title': _('Information'),
#                        'message': _("the approved quantity is not available in the stock") })
        # Warn if the quantity was decreased 
        if ids:
            for move in self.read(cr, uid, ids, ['product_qty']):
                if product_qty < move['product_qty']:
                    warning.update({
                       'title': _('Information'),
                       'message': _("By changing this quantity here, you accept the "
                                "new quantity as complete: OpenERP will not "
                                "automatically generate a back order.") })
                break

        if product_uos and product_uom and (product_uom != product_uos):
            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product UoS')
            result['product_uos_qty'] = float_round(product_qty * uos_coeff['uos_coeff'], precision_digits=precision)
        else:
            result['product_uos_qty'] = product_qty

        return {'value': result, 'warning': warning}




    def check_access_rule_location(self, cr, uid, ids, operation, context=None):
        """
        Verifies that the operation given by ``operation`` is allowed for the user
        according to ir.rules in a location.

        @param operation: one of ``write``, ``unlink``
        @return: None if the operation is allowed
        """
        where_clause, where_params, tables = self.pool.get('ir.rule').domain_get(cr, uid, 'stock.location', operation, context=context)
        if where_clause:
            where_clause = ' and ' + ' and '.join(where_clause)
            for sub_ids in cr.split_for_in_conditions(ids):
                cr.execute('SELECT ' + 'stock_location' + '.id FROM ' + ','.join(tables) +
                           ' WHERE ' + 'stock_location' + '.id IN %s' + where_clause,
                           [sub_ids] + where_params)
                if cr.rowcount != len(sub_ids):
                    return False
        return True


    def check_assign(self, cr, uid, ids, context=None):
        """ Change method of the super no check the product type.
        @return: No. of moves done
        """
        done = []
        count = 0
        pickings = {}
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.location_id.usage == 'supplier':
                if move.state in ('confirmed', 'waiting'):
                    done.append(move.id)
                pickings[move.picking_id.id] = 1
                continue
            if move.state in ('confirmed', 'waiting'):
                res = self.pool.get('stock.location')._product_reserve(cr, uid, [move.location_id.id], move.product_id.id, move.product_qty, {'uom': move.product_uom.id}, lock=True)
                if res:
                    self.write(cr, uid, [move.id], {'state':'assigned'})
                    done.append(move.id)
                    pickings[move.picking_id.id] = 1
                    r = res.pop(0)
                    product_uos_qty = self.pool.get('stock.move').onchange_quantity(cr, uid, [move.id], move.product_id.id, r[0], move.product_id.uom_id.id, move.product_id.uos_id.id)['value']['product_uos_qty']
                    cr.execute('update stock_move set location_id=%s, product_qty=%s, product_uos_qty=%s where id=%s', (r[1], r[0],product_uos_qty, move.id))

                    while res:
                        r = res.pop(0)
                        product_uos_qty = self.pool.get('stock.move').onchange_quantity(cr, uid, [move.id], move.product_id.id, r[0], move.product_id.uom_id.id, move.product_id.uos_id.id)['value']['product_uos_qty']
                        move_id = self.copy(cr, uid, move.id, {'product_uos_qty': product_uos_qty, 'product_qty': r[0], 'location_id': r[1]})
                        done.append(move_id)
        if done:
            count += len(done)
            self.write(cr, uid, done, {'state': 'assigned'})
        if count:
            for pick_id in pickings:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_write(uid, 'stock.picking', pick_id, cr)
        return count
    
    def draft_complete(self, cr, uid, ids, context=None):
        """ Confirms picking directly from draft state.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'complete'})
        wf_service = netsvc.LocalService('workflow')
        for move in self.browse(cr, uid, ids, context):
            if move.picking_id:
                wf_service.trg_write(uid, 'stock.picking','button_complete', cr)
        return True


    def validate_confirme(self, cr, uid, ids, context=None):
        """ Confirms picking directly from complete state.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'validated'})
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            wf_service.trg_validate(uid, 'stock.picking', pick.id,
                'button_validate', cr)
        return True

    def action_complete(self, cr, uid, ids, context=None):
        """ complete stock move.
        @return: List of ids.
        """
        self.write(cr, uid, ids, {'state': 'complete'})

    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        """
        Generate the appropriate accounting moves if the product being moves is subject
        to real_time valuation tracking, and the source or destination location is
        a transit location or is outside of the company.
        """
        account_moves = []
        if move.product_id.valuation == 'real_time' or (move.product_id.valuation == 'special_real_time' and \
        (move.scrapped or move.location_id.usage == 'inventory' or move.location_dest_id.usage == 'inventory' )): # FIXME: product valuation should perhaps be a property?
            if context is None:
                context = {}
            src_company_ctx = dict(context, force_company=move.location_id.company_id.id)
            dest_company_ctx = dict(context, force_company=move.location_dest_id.company_id.id)
            # Outgoing moves (or cross-company output part)
            if move.location_id.company_id \
                and (move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                #returning goods to supplier
                if move.location_dest_id.usage == 'supplier':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_src, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_dest, reference_amount, reference_currency_id, context))]
            # Incoming moves (or cross-company input part)
            if move.location_dest_id.company_id \
                and (move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                #goods return from customer
                if move.location_id.usage == 'customer':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_dest, acc_valuation, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_src, acc_valuation, reference_amount, reference_currency_id, context))]
        return account_moves

    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        picking_ids = []
        move_ids = []
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state == "draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
            todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done', 'cancel']:
                continue
            move_ids.append(move.id)
            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                # Downstream move should only be triggered if this move is the last pending upstream move
                other_upstream_move_ids = self.search(cr, uid, [('id', '!=', move.id), ('state', 'not in', ['done', 'cancel']),
                                            ('move_dest_id', '=', move.move_dest_id.id)], context=context)
                if not other_upstream_move_ids:
                    self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                    if move.move_dest_id.state in ('waiting', 'confirmed'):
                        self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                        if move.move_dest_id.picking_id:
                            wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                        if move.move_dest_id.auto_validate:
                            self.action_done(cr, uid, [move.move_dest_id.id], context=context)
            #self._create_product_valuation_moves(cr, uid, move, context=context)
            if move.state not in ('confirmed', 'done', 'assigned'):
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
        self.write(cr, uid, move_ids, {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
        for id in move_ids:
            wf_service.trg_trigger(uid, 'stock.move', id, cr)
        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)
        return True

class stock_picking(osv.Model):
    
    
    
    
    
    
    
    
    
    
    def button_dummy(self, cr, uid, ids, context={}):
        """ 
        Dummy function to recomputes the functional felids. 

        @return: True
        """
        return True
    
    
    
    _name = "stock.picking"
    _inherit = ['mail.thread', 'ir.needaction_mixin','stock.picking']


    _columns = {
        'backorder': fields.boolean('Back Order', help=" Does not generate a  backorder."),
        'account_move_id': fields.many2one('account.move', 'Journal Entry', readonly=True),
        'department_id': fields.many2one('hr.department',string ='Department',required=True),
        'category_id': fields.many2one('product.category',string ='Category',required=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('complete', 'Complete'),
            ('cancel', 'Cancelled'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Transfer'),
            ('validated' , 'Waiting Approval'),
            ('done', 'Transferred'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange', help="""
            * Draft: not confirmed yet and will not be scheduled until confirmed\n
            * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
            * Waiting Availability: still waiting for the availability of products\n
            * Ready to Transfer: products reserved, simply waiting for confirmation.\n
            * Transferred: has been processed, can't be modified or cancelled anymore\n
            * Cancelled: has been cancelled, can't be confirmed anymore""" ),
    }


    



    
    def _default_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        context['picking_type'] = 'internal'
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        else:
            location_xml_id = False
            if picking_type == 'in':
                location_xml_id = 'stock_location_suppliers'
            elif picking_type in ('out', 'internal'):
                location_xml_id = 'stock_location_stock'
            if location_xml_id:
                try:
                    location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                    with tools.mute_logger('openerp.osv.orm'):
                        self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
                except (orm.except_orm, ValueError):
                    location_id = False
        return location_id


    def action_cancel_draft(self, cr, uid, ids, context=None):
        """ Cancels the stock move and change picking out state to draft.
        @return: True
        """
        for order in self.browse(cr, uid, ids, context=context):

            self.write(cr, uid, [order.id], {'state':'draft'}, context=context)
            for move in order.move_lines:
                print move
                self.pool.get('stock.move').write(cr, uid, [move.id], {'state':'draft'}, context=context)
        return True

    def _default_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for destination location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        else:
            location_xml_id = False
            if picking_type in ('in', 'internal'):
                location_xml_id = 'stock_location_stock'
            elif picking_type == 'out':
                location_xml_id = 'stock_location_customers'
            if location_xml_id:
                try:
                    location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                    with tools.mute_logger('openerp.osv.orm'):
                        self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
                except (orm.except_orm, ValueError):
                    location_id = False

        return location_id
        
    _defaults = {
        'backorder': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid, context=ctx).company_id.backorder,
        #'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
    }
    
    def onchange_location_dest_id(self, cr, uid ,ids,location,move_lines,name):
        """
        Onchange location_id and location_dest_id in moves
        @return: Value
        """
        if move_lines:
            if name=='location_id':
                    for idss in move_lines:
                        if idss[0]==0:    
                            idss[2].update({'location_id':location})
                        else:
                            self.pool.get('stock.move').browse(cr, uid, [idss[1]])[0].write({'location_id':location_id})
                    return {'value':{'move_lines':move_lines}}
            else:
                    for idss in move_lines:
                        if idss[0]==0:    
                            idss[2].update({'location_dest_id':location})
                        else:
                            self.pool.get('stock.move').browse(cr, uid, [idss[1]])[0].write({'location_dest_id':location_id})
                    return {'value':{'move_lines':move_lines}}
        return True
            
    def onchange_category_id(self, cr, uid ,ids,category_id,move_lines,context=None):
         res = {}
         if move_lines:
             if move_lines[0][2]!=False:
                product_id = move_lines[0][2]['product_id'] 
                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)           
                value = {'category_id': product.categ_id.id}
                value.update({'category_id': product.categ_id.id}) 
                if (category_id != product.categ_id):
                    error={'title': _('Warning!'), 'message': _('You Can Not Change Category You Have Moves Line')}
                    return {'value':value,'warning':error}
             else:
                lines = self.pool.get('stock.move').browse(cr, uid, [move_lines[0][1]])[0]
                value = {'category_id': lines.product_id.categ_id.id}
                value.update({'category_id': lines.product_id.categ_id.id}) 
                if (category_id != lines.product_id.categ_id.id):
                    error={'title': _('Warning!'), 'message': _('You Can Not Change Category You Have Moves Line')}
                    return {'value':value,'warning':error}
         return res
                
    def draft_complete(self, cr, uid, ids, *args):
        """ Confirms picking directly from draft state.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            if not pick.move_lines:
                raise osv.except_osv(_('Error!'),_('You cannot process picking without stock moves.'))
            wf_service.trg_validate(uid, 'stock.picking', pick.id,
                'button_complete', cr)
        return True
        
    def validate_confirme(self, cr, uid, ids, context=None):
        """ Confirms picking directly from complete state.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            wf_service.trg_validate(uid, 'stock.picking', pick.id,
                'button_validate', cr)
        return True

    def action_complete(self, cr, uid, ids, context=None):
        """ Complete picking.
        @return: True
        """
        pickings = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'complete'})
        todo = []
        for picking in pickings:
            for r in picking.move_lines:
                if r.state == 'draft':
                    todo.append(r.id)
        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').action_complete(cr, uid, todo, context=context)
        return True

    def action_validate(self, cr, uid, ids, context=None):
        """ Validate picking.
        @return: True
        """
        return self.write(cr, uid, ids, {'state': 'validated'})

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """

        pickings = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'confirmed'})
        todo = []
        for picking in pickings:
            for r in picking.move_lines:
                if r.state in ('draft','complete'):
                    todo.append(r.id)
        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').action_confirm(cr, uid, todo, context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        """ Changes picking state to done and generate the appropriate accounting moves 
        if the product being moves is subject to real_time valuation tracking
        @return: True
        """
        super(stock_picking, self).action_done(cr, uid, ids, context=context)
        account_move_pool = self.pool.get('account.move')
        stock_move_pool = self.pool.get('stock.move')
        for pick in self.browse(cr, uid, ids, context=context):
            account_move_id = False
            account_moves=[]
            for move in pick.move_lines:
                if move.state=='cancel':
                    continue
                move_ids = stock_move_pool._create_product_valuation_moves(cr, uid, move, context=context)
                account_moves += move_ids and move_ids[0][1] or []
            if account_moves:
                stock_journal = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.stock_journal_id
                if not stock_journal:
                    raise osv.except_osv(_('No Stock Journal!'),_("There is no journal defined on your Company"))
                #period =  period_pool.find(cr, uid, dt=pick.date, context=context)
                account_move_id = account_move_pool.create(cr, uid, {'journal_id':stock_journal.id, 
                                                                     'line_id':account_moves, 'ref':pick.name}, context=context)
                account_move_pool.post(cr, uid, [account_move_id], context=context)
            self.write(cr, uid, [pick.id], {'account_move_id':account_move_id}, context=context)
        return True

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)
                product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)
 
                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
 
                    if product.id not in product_avail:
                        # keep track of stock on hand including processed lines not yet marked as done
                        product_avail[product.id] = product.qty_available
 
                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price, round=False)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product_avail[product.id] <= 0:
                            product_avail[product.id] = 0
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id])\
                                + (new_price * qty))/(product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
 
                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})
 
                        product_avail[product.id] += qty
 
 
 
            for move in too_few:
                product_qty = move_product_qty[move.id]
                if pick.backorder and not new_picking:
                     
                    new_picking_name = pick.name
                    self.write(cr, uid, [pick.id], 
                               {'name': sequence_obj.get(cr, uid,
                                            'stock.picking.%s'%(pick.type)),
                               })
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': new_picking_name,
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id]
                    }
                    if pick.backorder:
                        defaults.update(picking_id=new_picking)
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty': move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
                            'prodlot_id': False,
                            'tracking_id': False,
                        })
 
            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
 
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
 
                move_obj.write(cr, uid, [move.id], defaults)
            if  not pick.backorder:  
                move_obj.action_done(cr, uid, [c.id for c in complete + too_few], context=context)    
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)
 
            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context=context)
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = pick.id
                back_order_name = self.browse(cr, uid, delivered_pack_id, context=context).name
                self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (back_order_name), context=context)
            else:
                if pick.backorder:
                    self.action_move(cr, uid, [pick.id], context=context)
                    wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id
 
            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}
 
        return res


class stock_picking_in(osv.Model):

    _inherit = "stock.picking.in"
    _columns = {
        'department_id': fields.many2one('hr.department',string ='Department',required=True),
        'category_id': fields.many2one('product.category',string ='Category',required=True),
    }
    
    def onchange_location_dest_id(self, cr, uid ,ids,location,move_lines,name):
        """
        Onchange location_dest_id in in moves
        @return: Value
        """
        if move_lines:
            if name=='location_dest_id':
                    for idss in move_lines:
                        if idss[0]==0:    
                            idss[2].update({'location_dest_id':location})
                        else:
                            self.pool.get('stock.move').browse(cr, uid, [idss[1]])[0].write({'location_dest_id':location_id})
                    return {'value':{'move_lines':move_lines}}
        return True
 
    def onchange_category_id(self, cr, uid ,ids,category_id,move_lines,context=None):
         res = {}
         if move_lines:
             if move_lines[0][2]!=False:
                product_id = move_lines[0][2]['product_id'] 
                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)           
                value = {'category_id': product.categ_id.id}
                value.update({'category_id': product.categ_id.id}) 
                if (category_id != product.categ_id):
                    error={'title': _('Warning!'), 'message': _('You Can Not Change Category You Have Moves Line')}
                    return {'value':value,'warning':error}
             else:
                lines = self.pool.get('stock.move').browse(cr, uid, [move_lines[0][1]])[0]
                value = {'category_id': lines.product_id.categ_id.id}
                value.update({'category_id': lines.product_id.categ_id.id}) 
                if (category_id != lines.product_id.categ_id.id):
                    error={'title': _('Warning!'), 'message': _('You Can Not Change Category You Have Moves Line')}
                    return {'value':value,'warning':error}
         return res

    def _default_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        context['picking_type'] = 'in'
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        else:
            location_xml_id = False
            if picking_type == 'in':
                location_xml_id = 'stock_location_suppliers'
            elif picking_type in ('out', 'internal'):
                location_xml_id = 'stock_location_stock'
            if location_xml_id:
                try:
                    location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                    with tools.mute_logger('openerp.osv.orm'):
                        self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
                except (orm.except_orm, ValueError):
                    location_id = False

        return location_id
    
    def _default_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for destination location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        context['picking_type'] = 'in'
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        else:
            location_xml_id = False
            if picking_type in ('in', 'internal'):
                location_xml_id = 'stock_location_stock'
            elif picking_type == 'out':
                location_xml_id = 'stock_location_customers'
            if location_xml_id:
                try:
                    location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                    with tools.mute_logger('openerp.osv.orm'):
                        self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
                except (orm.except_orm, ValueError):
                    location_id = False

        return location_id
        
    _defaults = {
        'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
    }
        
class stock_picking_out(osv.osv):
    
    
    
    
    _inherit = "stock.picking.out"
    
    def button_dummy(self, cr, uid, ids, context={}):
        """ 
        Dummy function to recomputes the functional felids. 

        @return: True
        """
        return True
    
    
    
    
    
    
    
    message = "Dear Sir, You have Stock Exchange Order Waiting for Your Signature"
    _columns = {    
        'backorder': fields.boolean('Back Order', help=" Does not generate a  backorder."),
        'department_id': fields.many2one('hr.department',string ='Department',required=True),
        'category_id': fields.many2one('product.category',string ='Category',required=True),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('complete', 'Complete'),
            ('validated' , 'Waiting Approval'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Deliver'),
            ('done', 'Delivered'),
            ('cancel', 'Cancelled'),],
            'Status', readonly=True, select=True,
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Deliver: products reserved, simply waiting for confirmation.\n
                 * Delivered: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""),
    }



    





    def action_cancel_draft(self, cr, uid, ids, context=None):
        """ Cancels the stock move and change picking out state to draft.
        @return: True
        """
        for order in self.browse(cr, uid, ids, context=context):

            self.write(cr, uid, [order.id], {'state':'draft'}, context=context)
            for move in order.move_lines:
                self.pool.get('stock.move').write(cr, uid, [move.id], {'state':'draft'}, context=context)
        return True

    def _check_product_quant(self, cr, uid, ids, context=None):
        """
        Method checks that product category is chiled of order category.

        @return: Boolean True Or False
        """
        for record in self.browse(cr, uid, ids[0]).move_lines:

            if record.product_qty < 1 or record.qty < 1:
                raise osv.except_osv(_('Error'), _('Products Quantity must be greater than zero!'))
        return True
    
    
    
    
    
    
    
    _constraints = [
        (_check_product_quant, '',['']),
        
    ]
    
    def onchange_location_dest_id(self, cr, uid ,ids,location,move_lines,name):
        """
        Onchange location_id in in moves
        @return: Value
        """
        vals = {}
        if move_lines:
            
            
            if name=='location_id':
                    
                    for idss in move_lines:
                        if idss[0]==0:    
                            idss[2].update({'location_id':location})
                        else:
                            self.pool.get('stock.move').browse(cr, uid, [idss[1]])[0].write({'location_id':location})
                    return {'value':{'move_lines':move_lines}}            
        return vals
    
    def onchange_category_id(self, cr, uid ,ids,category_id,move_lines,context=None):
         res = {}
         if move_lines:
             if move_lines[0][2]!=False:
                product_id = move_lines[0][2]['product_id'] 
                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)           
                value = {'category_id': product.categ_id.id}
                value.update({'category_id': product.categ_id.id}) 
                if (category_id != product.categ_id):
                    error={'title': _('Warning!'), 'message': _('You Can Not Change Category You Have Moves Line')}
                    return {'value':value,'warning':error}
             else:
                lines = self.pool.get('stock.move').browse(cr, uid, [move_lines[0][1]])[0]
                value = {'category_id': lines.product_id.categ_id.id}
                value.update({'category_id': lines.product_id.categ_id.id}) 
                if (category_id != lines.product_id.categ_id.id):
                    error={'title': _('Warning!'), 'message': _('You Can Not Change Category You Have Moves Line')}
                    return {'value':value,'warning':error}
         return res
                
    def _default_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        context['picking_type'] = 'out'
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        else:
            location_xml_id = False
            if picking_type == 'in':
                location_xml_id = 'stock_location_suppliers'
            elif picking_type in ('out', 'internal'):
                location_xml_id = 'stock_location_stock'
            if location_xml_id:
                try:
                    location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                    with tools.mute_logger('openerp.osv.orm'):
                        self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
                except (orm.except_orm, ValueError):
                    location_id = False

        return location_id
    
    def _default_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for destination location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        else:
            location_xml_id = False
            if picking_type in ('in', 'internal'):
                location_xml_id = 'stock_location_stock'
            elif picking_type == 'out':
                location_xml_id = 'stock_location_customers'
            if location_xml_id:
                try:
                    location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                    with tools.mute_logger('openerp.osv.orm'):
                        self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
                except (orm.except_orm, ValueError):
                    location_id = False

        return location_id
        
    _defaults = {
        'backorder': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid, context=ctx).company_id.backorder,
        #'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
    }
    
    def get_manager_id(self, cr, uid,  ids, user, context=None):
        """ Getting Manager ID """
        
        if user:
            emp_obj = self.pool.get('hr.employee')
            dept_obj = self.pool.get('hr.department')
            
            
            emp_id = emp_obj.search( cr, uid, [('user_id' , '=' , user)])
            parent_id = emp_obj.browse( cr, uid, emp_id[0]).department_id.parent_id.id
            cr.execute('SELECT res_users.id as user_id, res_users.login as login, hr_department.manager_id as manager_id, res_partner.email as email ' \
            'FROM public.res_users, public.hr_employee, public.resource_resource, public.hr_department, public.res_partner ' \
            'WHERE hr_department.manager_id = hr_employee.id '\
            'AND hr_employee.resource_id = resource_resource.id '\
            'AND resource_resource.user_id = res_users.id '\
            'AND res_users.partner_id = res_partner.id '\
            'AND hr_department.id = %s', (parent_id,))
            res = cr.dictfetchall()
            #manager_user_id = emp_obj.browse( cr, uid,manager_id[0]).user_id.id 
            return [res[0]['user_id']]
        
        
        
        return False
        
        
        
        
    def draft_complete(self, cr, uid, ids, context={}):
        """ Confirms picking directly from draft state.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        flag = self.pool.get('res.users').has_group(cr, uid, 'base.group_unit_manager')
        flag1 = self.pool.get('res.users').has_group(cr, uid, 'base.group_department_manager')
        flag2 = self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_general_department_manager')
        flag3 = self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_general_hr_manager')
        flag4 = self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_account_general_manager')
        flag5 = self.pool.get('res.users').has_group(cr, uid, 'purchase_ntc.group_administrative_user')
        flag6 = self.pool.get('res.users').has_group(cr, uid, 'purchase_ntc.group_technical_user')
        flag7 = self.pool.get('res.users').has_group(cr, uid, 'stock_custom.group_warehouse_keeper')
        
        
        wf_service = netsvc.LocalService('workflow')
        for pick in self.browse(cr, uid, ids):
            if not pick.move_lines:
                raise osv.except_osv(_('Error!'),_('You cannot process picking without stock moves.')) 
            if flag:

               wf_service.trg_validate(uid, 'stock.picking', pick.id,
                'button_complete', cr)

            if flag1:

                wf_service.trg_validate(uid, 'stock.picking', pick.id,
                'button_validate', cr)

          
            if flag2:
                wf_service.trg_validate(uid, 'stock.picking', pick.id,
                    'button_confirm', cr)

                 
            if flag4:
                wf_service.trg_validate(uid, 'stock.picking', pick.id,
                    'button_confirm', cr)
                
            if (flag2 or flag3 or flag4):

               if pick.order_type == 'admin' :     
                   send_mail(self, cr, uid, ids[0] , 'purchase_ntc.group_administrative_user', "New Stock Exchange Order", self.message,context=context)
               else:
                   send_mail(self, cr, uid, ids[0] , 'purchase_ntc.group_technical_user', "New Stock Exchange Order", self.message,context=context)
   
                 

            if (flag or flag1) and (not flag2 and not flag3 and not flag4)   :

                send_mail(self, cr, uid, ids[0] , '', "New Stock Exchange Order", self.message , user=self.get_manager_id( cr, uid, ids, uid)  , department=False,context=context)


        return True

    def validate_confirme(self, cr, uid, ids, context=None):
        """ Confirms picking directly from complete state.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            wf_service.trg_validate(uid, 'stock.picking', pick.id,
                'button_validate', cr)
            
            send_mail(self, cr, uid, ids[0] , '', "New Stock Exchange Order", self.message , user=self.get_manager_id( cr, uid, ids, uid)  , department=False,context=context)

        return True
    
    
    
    def draft_force_assign(self, cr, uid, ids, context=None):
        """ Confirms picking directly from draft state.
        @return: True
        """
        super(stock_picking_out,self).draft_force_assign(cr, uid, ids)

        for pick in self.browse(cr, uid, ids):
            if pick.order_type == 'admin' :     
                       send_mail(self, cr, uid, ids[0] , 'purchase_ntc.group_administrative_user', "New Stock Exchange Order", self.message,context=context)
            else:
                       send_mail(self, cr, uid, ids[0] , 'purchase_ntc.group_technical_user', "New Stock Exchange Order", self.message,context=context)


        return True    
        
        
    def action_complete(self, cr, uid, ids, context=None):
        """ Complete picking.
        @return: True
        """
        pickings = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'complete'})
        todo = []
        for picking in pickings:
            for r in picking.move_lines:
                if r.state in ('draft','complete'):
                    todo.append(r.id)
        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').action_complete(cr, uid, todo, context=context)
        return True

    def action_validate(self, cr, uid, ids, context=None):
        """ Validate picking.
        @return: True
        """
        return self.write(cr, uid, ids, {'state': 'validated'})

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """
        pickings = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'confirmed'})
        todo = []
        for picking in pickings:
            for r in picking.move_lines:
                if r.state in ('draft','complete'):
                    todo.append(r.id)
        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').action_confirm(cr, uid, todo, context=context)
        return True


class stock_inventory(osv.Model):

    _inherit = "stock.inventory"

    _columns = {
        'account_move_id': fields.many2one('account.move', 'Journal Entry', readonly=True),
    }

    def unlink(self, cr, uid, ids, context=None):
        if self.search(cr, uid, [('id', 'in', ids), ('state', '!=', 'draft')], context=context):
            raise orm.except_orm(_('Invalid Action!'), _('You cannot delete  not draft stock inventory!'))
        return super(stock_inventory, self).unlink(cr, uid, ids, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('stock.move')
        inv_line_pool = self.pool.get('stock.inventory.line')
        if not inv_line_pool.search(cr, uid, [('inventory_id', 'in', ids)], context=context):
            raise orm.except_orm(_('Invalid Action!'), _('You cannot confirm stock inventory without lines!'))
        inv_line_ids = inv_line_pool.search(cr, uid, [('inventory_id', 'in', ids), ('subtotal', '!=', 0)], context=context)
        msg = [l.product_id.name for l in inv_line_pool.browse(cr, uid, inv_line_ids, context=context) if not l.product_id.property_stock_inventory]
        if msg:
            raise orm.except_orm(_('Configuration Error!'), _('Kindly review the inventory location for (%s)!') % (','.join(msg)))
        res = super(stock_inventory, self).action_confirm(cr, uid, ids, context=context)
        for inv in self.browse(cr, uid, ids, context=context):
            for move in inv.move_ids:
                move_pool.write(cr, uid, move.id, {'name':move.name + ':' + move.product_id.name}, context=context)
        return res

    def action_done(self, cr, uid, ids, context=None):
        """ Finish the inventory and  generate the appropriate accounting moves 
        if the product being moves is subject to real_time valuation tracking
        @return: True
        """
        account_move_pool = self.pool.get('account.move')
        stock_move_pool = self.pool.get('stock.move')
        period_pool = self.pool.get('account.period')
        for inv in self.browse(cr, uid, ids, context=context):
            account_move_id = False
            account_moves = []
            inventory_move_ids = [x.id for x in inv.move_ids]
            stock_move_pool.action_done(cr, uid, inventory_move_ids, context=context)
            # ask 'stock.move' action done are going to change to 'date' of the move,
            # we overwrite the date as moves must appear at the inventory date.
            stock_move_pool.write(cr, uid, inventory_move_ids, {'date': inv.date}, context=context)
            for move in inv.move_ids:
                move_ids = stock_move_pool._create_product_valuation_moves(cr, uid, move, context=context)
                account_moves += move_ids and move_ids[0][1] or []
            account_moves += self._create_account_move_line(cr, uid, inv, context=context)
            if account_moves:
                stock_journal = self.pool.get('res.users').browse(cr, uid, uid).company_id.stock_journal_id
                if not stock_journal:
                    raise osv.except_osv(_('No Stock Journal!'), _("There is no journal defined on your Company"))
                period = period_pool.find(cr, uid, dt=inv.date, context=context)

                account_move_id = account_move_pool.create(cr, uid, {'journal_id':stock_journal.id, 'line_id':account_moves,
                                                   'ref':inv.name, 'date':inv.date, 'period_id':period[0]}, context=context)
                account_move_pool.post(cr, uid, [account_move_id], context=context)
            self.write(cr, uid, [inv.id], {'state':'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S'),
                                           'account_move_id':account_move_id}, context=context)
        return True

    def action_cancel_inventory(self, cr, uid, ids, context=None):
        """ Cancels both stock move and inventory
        @return: True
        """
        res = super(stock_inventory, self).action_cancel_inventory(cr, uid, ids, context=context)
        move_ids = [inv.account_move_id.id for inv in self.browse(cr, uid, ids, context=context) if inv.account_move_id]
        self.pool.get('account.move').revert_move(cr, uid, move_ids, False, False, False, context=dict(context, reverse_move=True))
        return res

  
    def _create_account_move_line(self, cr, uid, inv, context=None):
        """
         Generate the account.move.line values to post to track the stock valuation difference due to the
         processing of the given stock move.
        """
        moves = []
        for line in inv.inventory_line_id:
            if line.stock_move and line.product_id.valuation == 'special_real_time' :
                src_location = line.stock_move < 0 and line.location_id or (line.stock_move > 0 and line.product_id.property_stock_inventory)
                dest_location = line.stock_move > 0 and line.location_id or (line.stock_move < 0 and line.product_id.property_stock_inventory)
                if not src_location or not dest_location:
                    raise osv.except_osv(_('Error!'),_('Make sure that your lines contain a location & your products has an inventory location.'))
                print src_location.name
                print dest_location.name
                product_obj=self.pool.get('product.product')
                accounts = product_obj.get_product_accounts(cr, uid, line.product_id.id, context)
                if src_location.valuation_out_account_id:
                    acc_src = src_location.valuation_out_account_id.id
                else:
                    acc_src = accounts['stock_account_input']
                if dest_location.valuation_in_account_id:
                    acc_dest = dest_location.valuation_in_account_id.id
                else:
                    acc_dest = accounts['stock_account_output']
                acc_valuation = accounts.get('property_stock_valuation_account_id', False)
                debit_line_vals = {
                                 'name': _('INV:') + (line.inventory_id.name or '')+ ':' + line.product_id.name,
                                 'product_id': line.product_id and line.product_id.id or False,
                                 'quantity': line.stock_move,
                                 'ref': line.inventory_id.name,
                                 'debit': abs(line.stock_move)*line.price,
                                 'credit': 0,
                                 'account_id': acc_dest,
                }
                credit_line_vals = {
                                 'name': _('INV:') + (line.inventory_id.name or '')+ ':' + line.product_id.name,
                                 'product_id': line.product_id and line.product_id.id or False,
                                 'quantity': line.stock_move,
                                 'ref': line.inventory_id.name,
                                 'debit': 0,
                                 'credit': abs(line.stock_move)*line.price,
                                 'account_id': acc_src,
                }
                moves += [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
                    #==================================================================
                    # 
                    #        # if we are posting to accounts in a different currency, provide correct values in both currencies correctly
                    #        # when compatible with the optional secondary currency on the account.
                    #        # Financial Accounts only accept amounts in secondary currencies if there's no secondary currency on the account
                    #        # or if it's the same as that of the secondary amount being posted.
                    #        account_obj = self.pool.get('account.account')
                    #        src_acct, dest_acct = account_obj.browse(cr, uid, [src_account_id, dest_account_id], context=context)
                    #        src_main_currency_id = src_acct.company_id.currency_id.id
                    #        dest_main_currency_id = dest_acct.company_id.currency_id.id
                    #        cur_obj = self.pool.get('res.currency')
                    #        if reference_currency_id != src_main_currency_id:
                    #            # fix credit line:
                    #            credit_line_vals['credit'] = cur_obj.compute(cr, uid, reference_currency_id, src_main_currency_id, reference_amount, context=context)
                    #            if (not src_acct.currency_id) or src_acct.currency_id.id == reference_currency_id:
                    #                credit_line_vals.update(currency_id=reference_currency_id, amount_currency=-reference_amount)
                    #        if reference_currency_id != dest_main_currency_id:
                    #            # fix debit line:
                    #            debit_line_vals['debit'] = cur_obj.compute(cr, uid, reference_currency_id, dest_main_currency_id, reference_amount, context=context)
                    #            if (not dest_acct.currency_id) or dest_acct.currency_id.id == reference_currency_id:
                    #                debit_line_vals.update(currency_id=reference_currency_id, amount_currency=reference_amount)
                    # 
                    #==================================================================
        return moves

class stock_inventory_line(osv.Model):

    _inherit = "stock.inventory.line"

    def _get_stock_qty(self, cr, uid, ids, field_name, arg=None, context=None):
        """ 
        
        
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary stock_qty & diff_qty of each record    
        """
        result = {}
        location_pool = self.pool.get('stock.location')
        product_context = dict(context, compute_child=False)
        for line in self.browse(cr, uid, ids, context=context):
            pid = line.product_id.id
            product_context.update(uom=line.product_uom.id, to_date=line.inventory_id.date, date=line.inventory_id.date, prodlot_id=line.prod_lot_id.id)
            amount = location_pool._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]
            cr.execute("""SELECT l.product_qty qty, s.date date
                             FROM stock_inventory_line l INNER JOIN stock_inventory s ON (l.inventory_id=s.id)
                            WHERE s.state = 'done' AND l.product_id=%d AND s.date < '%s'
                            ORDER BY s.date 
                            LIMIT 1"""
                            %(line.product_id.id,line.inventory_id.date))
            last_inv = cr.fetchone()
            last_inv = last_inv and last_inv[0] or 0
            stock_move = location_pool._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]
            result[line.id] = {
                'stock_qty': amount,
                'stock_move': amount - last_inv,
                'diff_qty': line.product_qty - amount,
                'price': line.product_id.price_get('standard_price', context=context)[line.product_id.id],
                'subtotal':  line.product_id.price_get('standard_price', context=context)[line.product_id.id] * (line.product_qty - amount)
            }
        return result

    def _get_inventory_line(self, cr, uid, ids, context=None):
        return self.pool.get('stock.inventory.line').search(cr, uid, [('inventory_id', 'in', ids)], context=context)

    _columns = {
        'stock_qty': fields.function(_get_stock_qty, method=True, type='float', string='Stock Quantity',
                                     digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True, multi='qty',
                                     store={'stock.inventory': (_get_inventory_line, ['date','state'], 10),
                                            'stock.inventory.line': (lambda self, cr, uid, ids, c={}: ids, ['location_id', 'product_id'], 10),
                                            }),
        'stock_move': fields.function(_get_stock_qty, method=True, type='float', string='Stock Move',
                                     digits_compute=dp.get_precision('Product Price'), readonly=True, multi='qty',
                                     store={'stock.inventory': (_get_inventory_line, ['date','state'], 10),
                                            'stock.inventory.line': (lambda self, cr, uid, ids, c={}: ids, ['location_id', 'product_id'], 10),
                                            }),
        'diff_qty': fields.function(_get_stock_qty, method=True, type='float', string='Quantity Differences', store=True,
                                     digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True, multi='qty'),
        'price': fields.function(_get_stock_qty, method=True, type='float', string='Price',
                                     digits_compute=dp.get_precision('Product Price'), readonly=True, multi='qty',
                                     store={'stock.inventory': (_get_inventory_line, ['date','state'], 10),
                                            'stock.inventory.line': (lambda self, cr, uid, ids, c={}: ids, ['location_id', 'product_id'], 10),
                                            }),
        'subtotal':  fields.function(_get_stock_qty, method=True, type='float', string='Subtotal', store=True,
                                     digits_compute=dp.get_precision('Product Price'), readonly=True, multi='qty'),
    }

    _sql_constraints = [
        ('location_product_uniq', 'unique(inventory_id,location_id, product_id)', 'You can\'t inventory the same product in the same location twice!'),
        ('qyt_gt_zero', 'CHECK (product_qty>=0)', 'The product inventory quantity should be greater than zero!')
    ]
# ----------------------------------------------------
# Stock Journal (Inherit)
# ----------------------------------------------------
class stock_journal(osv.Model):
    _inherit = "stock.journal"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', domain="[('usage','=','customer')]", select=True),
    }
    def _default_stock_location(self, cr, uid, context=None):
        try:
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_customers')
            with tools.mute_logger('openerp.osv.orm'):
                self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id
    _defaults = {
        'location_id': _default_stock_location,
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

