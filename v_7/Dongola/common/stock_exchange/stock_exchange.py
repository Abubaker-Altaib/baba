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

STATE_SELECTION = [
        ('draft', 'Request for Exchange'),
        ('confirmed', 'Waiting Department Approval'),
        ('confirmed1', 'Waiting for Approval'),
        ('confirmed2', 'Waiting for meters Approval'),
        ('approved_qty', 'Waiting Budget Check'),
        ('budget_yes', 'Budget Approved'),
        ('budget_no', 'Budget Cancelled'),
        ('approved', 'Approved'),
        ('picking', 'Picking'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]
# ----------------------------------------------------
# Stock Journal (Inherit)
# ----------------------------------------------------
class stock_journal(osv.Model):
    _inherit = "stock.journal"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', domain="[('usage','=','customer')]", select=True),
        'request_no': fields.boolean('Request No.'),
    }


#----------------------------------------------------------
# Categories (Inherit)
#----------------------------------------------------------
class product_category(osv.Model):
    _inherit = "product.category"
    _columns = {
        'meters': fields.boolean('Meters'),
    }
    _defaults = {
        'meters' :0,
    }


# ----------------------------------------------------
# Exchange Order 
# ----------------------------------------------------
class exchange_order(osv.Model):
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        Calculate total amount in order line.
        @param field_name: Name of the field
        @param arg: User defined argument
        @return:  Dictionary of values
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = { 'amount_total': 0.0}
            val = 0.0
            for line in order.order_line:
                val += line.price_subtotal
            res[order.id]['total_amount'] = val        
        return res

    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        """
        Compute the progress_rate depend on sum of delivered_qty and approved_qty
        @param names: User defined argument
        @param arg: User defined argument
        @return:  Dictionary of values
        """
        res = {}.fromkeys(ids, 0.0)
        if not ids:
            return res
        cr.execute('''SELECT
                order_id, sum(delivered_qty), sum(approved_qty)
            FROM
                exchange_order_line
            WHERE
                order_id in %s AND
                state<>'cancel'
            GROUP BY
                order_id''', (tuple(ids),))
        progress = dict(map(lambda x: (x[0], (x[1], x[2])), cr.fetchall()))
        for order in self.browse(cr, uid, ids, context=context):
            s = progress.get(order.id, (0.0, 0.0))
            res[order.id] = { 'progress_rate': s[1] and round(100.0 * s[0] / s[1], 2) or 0.0}
        return res
    
    def _get_type(self, cr, uid, context=None):
        """
        Get type of location
        @return : ttype or False 
        """
        if context is None:
            context = {}
        return context.get('ttype', False)

    def _get_order(self, cr, uid, ids, context=None):
        """
        To be called by field of current  object to get value
        @return : value of field
        """
        result = {}
        exchange_line_obj=self.pool.get('exchange.order.line')
        for line in exchange_line_obj.browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()


    def _rec_by_categ(self, cr, uid, ids, context=None):
        """
        Get rec_by_categ object in res company model
        @return: value of rec_by_categ
        """
        return self.pool.get('res.users').browse(cr, uid, uid).company_id.rec_by_categ


    def create(self, cr, user, vals, context=None):
        """
        Override to add constrain of sequance
        @param vals: Dictionary of values
        @return: super of exchange_order
        """
        if ('name' not in vals) or (vals.get('name') == '/'):
            seq = self.pool.get('ir.sequence').get(cr, user, 'exchange.order')
            vals['name'] = seq and seq or '/'
            if not seq:
                raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'exchange.order\'') )
        new_id = super(exchange_order, self).create(cr, user, vals, context)
        return new_id

    _columns = {
        'name': fields.char('Order Reference', size=64, required=True, readonly=True, select=True),
        'date_order':fields.date('Date Ordered', readonly=True, required=True, states={'draft': [('readonly', False)]}, select=True),
        'date_approve':fields.date('Date Approved', readonly=1, select=True),
        'ttype': fields.selection([('other', 'Other'), ('store', 'Stock Store')], 'Type', required=True, select=True),
        'location_id': fields.many2one('stock.location', 'Location', readonly=True, states={'draft': [('readonly', False)]}),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', readonly=False, domain="[('usage','in',['internal'])]", states={'confirmed1': [('required', True)], 'cancel': [('readonly', True)] }),
        'picking_ids': fields.one2many('stock.picking', 'exchange_id', 'Related Picking', readonly=True, help="This is a list of picking that has been generated for this sales order."),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
        'order_line': fields.one2many('exchange.order.line', 'order_id', 'Order Lines'),
        'validator' : fields.many2one('res.users', 'Validated by', readonly=True),
        'notes': fields.text('Notes'),
        'purposes': fields.text('Purposes', readonly=True, states={'draft': [('readonly', False)]}),
        'shipped': fields.boolean('Delivered', readonly=True),
        'progress_rate': fields.function(_progress_rate, method=True, string='Progress', group_operator="avg",
            store={
                'exchange.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'exchange.order.line': (_get_order, ['delivered_qty', 'approved_qty'], 10),

            },multi='progress'),
        'total_amount': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Exchange Price'), string='Amount',
            store={
                'exchange.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'exchange.order.line': (_get_order, ['price_unit', 'approved_qty'], 10),
            },multi='sums'),
        'product_id': fields.related('order_line', 'name', type='many2one', relation='product.product', string='Product'),
        'create_uid':  fields.many2one('res.users', 'Responsible'),
        'acc_bud_confirm_id': fields.many2one('account.budget.confirmation', 'Budget Confirmation', readonly=True),
        'account_analytic_id': fields.related('acc_bud_confirm_id', 'analytic_account_id', type='many2one', relation='account.analytic.account', string='Analytic Account', store=True, readonly=True),
        'account_id': fields.related('acc_bud_confirm_id', 'general_account_id', type='many2one', relation='account.account', string='Account', store=True, readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
        'department_id': fields.many2one('hr.department', 'Department', readonly=True , states={'draft': [('readonly', False)]}),
        'categ_id': fields.many2one('product.category', 'Category', domain="[('type','=','normal')]" , readonly=True , states={'draft': [('readonly', False)]}),
        'stock_journal_id': fields.many2one('stock.journal', 'Stock Journal', readonly=True, states={'draft': [('readonly', False)]}, select=True),
        #'address_id': fields.many2one('res.partner.address', 'Address', readonly=True, states={'draft': [('readonly', False)]}, select=True , help="Address of partner"),
        #'partner_id': fields.related('address_id', 'partner_id', type='many2one', relation='res.partner', string='Partner', store=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=False),
        'req_no' : fields.char('Requet NO', size=128),
        'allow_req': fields.boolean('Allow request'), 
        'rec_by_categ': fields.boolean('Rec By Category',readonly=True,),
    }

    _defaults = {
        'date_order': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'name':'/',
        'shipped': 0,
        'ttype': _get_type,
        'rec_by_categ':_rec_by_categ,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'exchange.order', context=c),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Order Reference must be unique !'),
    ]
    _name = "exchange.order"
    _description = "Exchange Order"
    _order = "name desc"

    def onchange_journal_id(self, cr, uid, ids, stock_journal_id, context={}):
        """
        Changing allow_req field value
        @param stock_journal_id: stock_journal_id

        @return: dictionary conatins the new values of:
                 allow_req: journal.request_no
        """
        res = {'value':{'allow_req': False}}
        if stock_journal_id:
            journal =  self.pool.get('stock.journal').browse(cr, uid, stock_journal_id)
            res['value'].update({'allow_req':journal.request_no})
        return res 
        
    def onchange_category_id(self, cr, uid, ids, categ_id, context=None):
        line_pool = self.pool.get('exchange.order.line')
        line_ids = ids and line_pool.search(cr, uid, [('order_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)
        return{'value': {'order_line': [] } }

    def unlink(self, cr, uid, ids, context=None):
        """
        Perfom deleting exchange orders in state 'draft', 'cancel' and prohibit
        user from deleting records in other state 
        @return: super unlink function of exchange_order
        """
        exchange_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in exchange_orders:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a Exchange Order(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'exchange.order', id, 'exchange_cancel', cr)
        return super(exchange_order, self).unlink(cr, uid, unlink_ids, context=context)
   
    def copy(self, cr, uid, id, default=None, context=None):
        """
        Coping exchange order record and reset values
        @param default: dict type contains the values to be override during copy of object
        @return: super copy function of exchange_order
        """
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, id, context=context)
        if ('name' not in default) or (picking_obj.name == '/'):
            seq_obj_name = 'exchange.order'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            default['state'] = 'draft'
            default['shipped'] = False
            default['picking_ids'] = []
            default['acc_bud_confirm_id'] = False
        res = super(exchange_order, self).copy(cr, uid, id, default, context)
        return res

    def _prepare_order_budget(self, cr, uid, order, period, notes,context=None):
        """
        Prepare the dict of values to create the new budget confirmation for a
        order. This method may be overridden to implement custom
        budget confirmation generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order record 
        @param int period: optional ID of a period 
        @return: dict of values to create() the budget confirmation
        """
        return {
              'name': '/',
              'reference': order.name,
              'period_id': period[0] ,
              'amount': order.total_amount,
              'residual_amount':0.0,
              'general_account_id': order.location_id.valuation_account_id and  order.location_id.valuation_account_id.id or False,
              'note':notes,
              'type':'stock_out',
              'date':order.date_order or time.strftime('%Y-%m-%d'),
              'partner_id':order.partner_id and order.partner_id.id or False,
        }

    def action_budget_create(self, cr, uid, ids, context=None):
        """
        Creates budget confirmation

        @return: ID of budget confirmation  used/created for the given order to connect in the subflow of the order 
        """ 
        budget_confirm_obj=self.pool.get('account.budget.confirmation')
        res_user = self.pool.get('res.users').browse(cr, uid, uid)
        period_obj=self.pool.get('account.period')
        for order in self.browse(cr, uid, ids, context=context):
            period =   period_obj.find(cr, uid, dt=order.date_order, context=context)
            stock_journal = order.stock_journal_id and order.stock_journal_id.name or 'stock store'
            cr.execute('SELECT name FROM hr_department WHERE id=%s' %(order.department_id.id))
            department = cr.fetchone()[0] or 0.0

            notes = _("Location: %s \nDepartment: %s \nType: %s \nPurposes: %s. \nvalidator:%s ") % (order.location_id.name , department, stock_journal , order.purposes or 'Not Found', res_user.name)  

            if order.acc_bud_confirm_id:
                budget_confirm_obj.action_cancel_draft(cr, uid,  order.acc_bud_confirm_id.id,context=context)
                confirmation= order.acc_bud_confirm_id.id 
            else:
                confirmation_id = budget_confirm_obj.create(cr, uid, self._prepare_order_budget(cr, uid, order,period, notes, context=context))  
                self.write(cr, uid, [order.id], {'acc_bud_confirm_id': confirmation_id})
                confirmation= confirmation_id 
        return confirmation

    def changes_state(self, cr, uid, ids, vals,context=None):
        """ 
        Changes order state 
        @param vals: dict that will be used in write method

        @return: True
        """        
        for order in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [order.id], vals)
            self.pool.get('exchange.order.line').write(cr, uid, [x.id for x in order.order_line], vals,context=context)
        return True

    def action_approve_order(self, cr, uid, ids, context=None):
        """ 
        Changes order state to approved.

        @return: True
        """
        self.changes_state(cr, uid, ids,{'state': 'approved'},context=context)
        self.write(cr, uid, ids, {'date_approve': time.strftime('%Y-%m-%d')})
        return True

    def action_confirm_order(self, cr, uid, ids, context=None):
        """ 
        Changes order state to confirm.

        @return: True
        """
        for order in self.browse(cr, uid, ids, context=context):
            if not order.order_line:
                raise osv.except_osv(_('Error !'), _('You can not confirm the order without  order lines.'))
            if order.ttype=='store':
                manager_id=order.department_id.manager_id 
                if not manager_id or  not manager_id.user_id or  manager_id.user_id.id!=uid:
                    raise osv.except_osv(_('Error !'), _('Department  manager who only can confirm this order.'))
            else:
                manager_id=order.department_id.manager_id 
                if not manager_id or  not manager_id.user_id or  manager_id.user_id.id!=uid:
                    manager_id=order.department_id.parent_id.manager_id 
                    if not manager_id or  not manager_id.user_id or  manager_id.user_id.id!=uid:
                        raise osv.except_osv(_('Error !'), _('Department  manager who only can confirm this order.'))  
            self.changes_state(cr, uid, ids, {'state': 'confirmed'},context=context)
        return True

    def action_confirm1_order(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to confirmed1.

        @return: boolean True
        """
        self.changes_state(cr, uid, ids,{'state': 'confirmed1'},context=context)
        self.write(cr, uid, ids, {'validator': uid })
        return True

    def action_meter_router(self, cr, uid, ids, context=None):
        """
        Workflow function to do router between to sub flow.

        @return: boolean True
        """
        return True

    def has_meters_product(self, cr, uid, ids, context=None):
        """
        Condition Workflow function.

        @return: boolean 
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.ttype == "store" and order.categ_id.meters == True:
                return True
        return False
    
    def action_done_order(self, cr, uid, ids, context=None):
        """ 
        Workflow function Changes order state to done.

        @return: True
        """
        for order in self.browse(cr, uid, ids, context=context):
            for pick in order.picking_ids:
                if pick.id and pick.state not in ['done', 'cancel']:
                    raise osv.except_osv(
                        _('Error !'),
                        _('You can not correct it manualy , some picking attached to this exchange order are not in done or cancel state.'))
            self.write(cr, uid, ids, {'state':'done'})
        return True

    def action_cancel_draft(self, cr, uid, ids, *args):
        """ 
        Workflow function Changes order state to draft.
        @param *args: Get Tupple value

        @return: True
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for p_id in ids:
            # Deleting the existing instance of workflow for order
            wf_service.trg_delete(uid, 'exchange.order', p_id, cr)
            wf_service.trg_create(uid, 'exchange.order', p_id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("Exchange order '%s' has been set in draft state.") % name
            self.log(cr, uid, id, message)
        self.changes_state(cr, uid, ids,{'state': 'draft'},context={})
        self.write(cr, uid, ids, {'shipped':0 })
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ 
        Workflow function Changes order state to cancel.

        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for order in self.browse(cr, uid, ids, context=context):
            for pick in order.picking_ids:
                if pick.state != 'cancel':
                    raise osv.except_osv(
                        _('Could not cancel exchange order !'),
                        _('You must first cancel all picking attached to this exchange order.'))
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
            wf_service.trg_validate(uid, 'account.budget.confirmation', order.acc_bud_confirm_id.id, 'cancel', cr)
        self.changes_state(cr, uid, ids, {'state':'cancel'},context=context)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("Exchange order '%s' is cancelled.") % name
            self.log(cr, uid, id, message)
        return True

    def action_cancel_order(self, cr, uid, ids, context=None):
        """ 
        Workflow function Changes order state to cancel related by budget confirmation id.

        @return: True
        """
        self.changes_state(cr, uid, ids, {'state':'cancel'},context=context)
        wf_service = netsvc.LocalService("workflow")
        for order in self.browse(cr, uid, ids, context=context):
            if order.acc_bud_confirm_id:
                wf_service.trg_validate(uid, 'account.budget.confirmation', order.acc_bud_confirm_id.id, 'cancel', cr)
        return True

    def move_lines_get(self, cr, uid, ids, *args):
        """
        Get move from order line  
        @param *args: Get Tupple value

        @return :List of move ids
        """
        res = []
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.order_line:
                res += [x.id for x in line.move_ids]
        return res
    
    def test_state(self, cr, uid, ids, mode, *args):
        """
        Check order line 
        If mode == 'finished': returns True if all lines are done, False otherwise
        If mode == 'canceled': returns True if there is at least one canceled line, 
                                False otherwise

        @param mode : tuple contain state of wkf
        @param *args: Get Tupple value
        @return :mode
        """
        assert mode in ('finished', 'canceled'), _("invalid mode for test_state")
        finished = True
        canceled = False
        notcanceled = False
        write_done_ids = []
        write_cancel_ids = []
        new_amount = 0
        amount = 0
        exch_obj = self.pool.get('exchange.order.line')
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.order_line:
                if all([x.state == 'done' for x in line.move_ids]):
                    if line.state != 'done':
                        write_done_ids.append(line.id)
                else:
                    finished = False
                if all([x.state == 'cancel' for x in line.move_ids]):
                    canceled = True
                    if line.state != 'cancel':
                        write_cancel_ids.append(line.id)
                else:
                    notcanceled = True
                for move in line.move_ids:
                    if move.state == 'cancel' and move.picking_id.type == 'out':
                        new_amount += move.product_qty * line.price_unit
                amount = order.total_amount - new_amount
                cr.execute('update account_budget_confirmation set amount=%s where id=%s', (amount, order.acc_bud_confirm_id.id))
        if write_done_ids:
            exch_obj.write(cr, uid, write_done_ids, {'state': 'done'})
        if write_cancel_ids:
            exch_obj.write(cr, uid, write_cancel_ids, {'state': 'cancel'})
            
        if mode == 'finished':
            return finished
        elif mode == 'canceled':
            if notcanceled:
                return False
            return canceled


    def action_process(self, cr, uid, ids, context=None):
        """
        This function opens a window for exchange partial picking

        @return : Dictinory of values
        """
        if context is None:
            context = {}
        context = dict(context, active_ids=ids, active_model=self._name)
        partial_id = self.pool.get("exchange.partial.picking").create(cr, uid, {}, context=context)
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'exchange.partial.picking',
            'res_id': partial_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }
        
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id,product_qty ,context=None):
        """
        Prepare the dict of values to create the new stock move for a
        exchange order line. This method may be overridden to implement custom
        move generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order record 
        @param browse_record line: exchange.order.line record 
        @param int picking_id: ID of stock  picking 
        @param product_qty : product qty(this is used for returning products including service)

        @return: dict of values to create() the stock move
        """
        return {
            'name': line.name[:250],
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'product_qty': product_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty':product_qty,
            'product_uos':  line.product_uom.id,
            'location_id': order.location_dest_id.id ,
            'location_dest_id': (order.location_id and order.location_id.id) or order.stock_journal_id.location_id.id,
            'exchange_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            'note': line.notes,
            'price_unit': line.product_id.standard_price or 0.0
        }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
        Prepare the dict of values to create the new picking for a
        exchange order. This method may be overridden to implement custom
        picking generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order.line record to invoice

        @return: dict of values to create() the picking
        """
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': order.date_order,
            'type': 'out',
            'state': 'auto',
            'exchange_id': order.id,
            'note': order.notes,
            'department_id':order.department_id.id,
            'analytic_account_id':order.account_analytic_id.id,
            'account_id':order.account_id.id,
        }

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ 
        Creates pickings and appropriate stock moves for given order lines, then
        confirms the moves, makes them available, and confirms the picking.
        @param partial_datas : Dictionary containing details of partial picking
        like  moves with product_id, product_qty, uom

        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        pick_obj=self.pool.get('stock.picking')
        line_obj = self.pool.get('exchange.order.line')
        stock_move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        for order in self.browse(cr, uid, ids, context=context):
            picking_id = None
            todo_moves = []
            for line in order.order_line:
                if line.state in ('done', 'cancel', 'picking'):
                    continue
                partial_data = partial_datas.get('move%s' % (line.id), {})
                product_qty = partial_data.get('product_qty') or 0.0
                if not picking_id and product_qty != 0:
                    picking_id = pick_obj.create(cr, uid, self. _prepare_order_picking(cr, uid, order, context=context))
                if product_qty != 0:
                    move_id = stock_move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id,product_qty ,context=context))
                    todo_moves.append(move_id)
                stock_move_obj.action_confirm(cr, uid, todo_moves)
                stock_move_obj.force_assign(cr, uid, todo_moves)
                line_obj.write(cr, uid, [line.id], {'delivered_qty' : line.delivered_qty + product_qty})
                if line.approved_qty - line.delivered_qty == product_qty:
                    line_obj.write(cr, uid, [line.id], {'state' :'picking'})
                if picking_id:
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
                self.write(cr, uid, ids, {})
        return res
    
    def test_picking(self, cr, uid, ids):
        """ 
        Tests whether the move is in picking state or not.

        @return: True or False
        """
        for order in self.browse(cr, uid, ids):
            for move in order.order_line:
                if move.state != 'picking':
                    return False      
        return True


# ----------------------------------------------------
# Order Line
# ----------------------------------------------------
class exchange_order_line(osv.Model):

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute price from order line
        @param field_names: Name of field
        @param args: other arguments

        @return Dictinory of value
        """
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * line.approved_qty or 0.0
            res[line.id] = price
        return res
    
    def _real_stock(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute real stock quanity 
        @param field_names: Name of field
        @param args: other arguments

        @return Dictinory of value
        """
        res = {}
        if context is None:
            context = {}
        stock_location_obj=self.pool.get('stock.location')
        for line in self.browse(cr, uid, ids):
            context.update({'uom': line.product_id.uom_id.id })
            location_id = line.location_id and line.location_id.chained_location_id.id or False
            amount = stock_location_obj._product_get(cr, uid, location_id, [line.product_id.id],  )[line.product_id.id] or 0.0
            res[line.id] = amount
        return res
    
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
            res[line.id] =  0.0
            location_id = line.order_id.location_dest_id and line.order_id.location_dest_id.id 
            if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
                    res[line.id] = stock_location_obj._product_get(cr, uid, location_id, [line.product_id.id], context = context)[line.product_id.id]
        return res
        
    def _get_category(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('categ_id', False):
            return context.get('categ_id')
        return False
         
    _columns = {
        'name': fields.char('Description', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_qty': fields.float('Quantity', required=True, digits_compute=dp.get_precision('Product UoM'), readonly=True, states={'draft': [('readonly', False)]}),
        'approved_qty': fields.float('Approved Quantity', required=True, digits_compute=dp.get_precision('Product UoM'), readonly=True, states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]}),
        'delivered_qty': fields.float('Delivered Quantity', digits_compute=dp.get_precision('Product UoM'), readonly=True),
        'real_qty': fields.function(_real_stock, method=True, type="float", string='Location'),
        'stock_available': fields.function(_real_stock_dest, method=True, type="float", string="Available"),
        'product_id': fields.many2one('product.product', 'Product', required=True, domain="[('type','=','product')]",change_default=True, readonly=True, states={'draft': [('readonly', False)]}),
        'move_ids': fields.one2many('stock.move', 'exchange_line_id', 'Reservation', readonly=True, ondelete='set null'),
 
        'price_unit': fields.related('product_id', 'standard_price', type='float', relation='product.product', string='Price Unit', readonly=True
                        ,store={
                            'exchange.order.line': (lambda self, cr, uid, ids, c={}: ids, ['product_id'], 10),
                        }), 
        'product_uom': fields.related('product_id', 'uom_id', type='many2one', relation='product.uom', string='Product UOM', readonly=True
                        ,store={
                            'exchange.order.line': (lambda self, cr, uid, ids, c={}: ids, ['product_id'], 10),
                        }),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal',digits_compute=dp.get_precision('Exchange Price')),
        'notes': fields.text('Notes'),
        'order_id': fields.many2one('exchange.order', 'Order Reference', select=True, required=True, ondelete='cascade'),
        'company_id': fields.related('order_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
        'date_order': fields.related('order_id', 'date_order', string='Order Date', readonly=True, type="date"),
        'location_id': fields.related('order_id', 'location_id', type='many2one', relation='stock.location', string='Location'),
        'categ_id': fields.many2one('product.category', 'Category', domain="[('type','=','normal')]"),

    }

    def create(self, cr, uid, vals, context={}):
        """
        inherit to add constrain of order line
        @param vals :Dictionary of values

        @return : super of exchange_order_line
        """
        state = self.pool.get('exchange.order').browse(cr, uid, vals['order_id']).state
        if state != 'draft':
            raise osv.except_osv(_('Error!'), _('You can only create order line in draft state.'))
        return super(exchange_order_line, self).create(cr, uid,  vals, context=context)


    _defaults = {
        'product_qty':1.0,
        'approved_qty':1.0,
        'delivered_qty':0.0,
        'state': 'draft',
        'categ_id': _get_category,
    }
    _table = 'exchange_order_line'
    _name = 'exchange.order.line'
    _description = 'Exchange Order Line'
    
    def unlink(self, cr, uid, ids, context=None):
        """
        Perfrom deleting exchange orders in state 'draft', 'cancel'
        and prohibit user from deleting records in other states

        @return super unlink function of exchange_order_line
        """
        exchange_orders_line = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in exchange_orders_line:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Error !'), _('You can not delete a prodcut'))
        return super(exchange_order_line, self).unlink(cr, uid, unlink_ids, context=context)

    def _check_negative(self, cr, uid, ids, context=None):
        """ 
        Constrain function to check the negative approved_qty should be greater than 0

        @return Boolean True or False
        """
        obj_ex = self.browse(cr, uid, ids[0], context=context)
        if obj_ex.approved_qty < 0 or obj_ex.product_qty < 0:
            return False
        return True
   
    def _check_approved_qty(self, cr, uid, ids, context=None):
        """ 
        Constrain function to check the approved_qty, it should be less than 
        product_qty in order line.

        @return Boolean True or False
        """
        obj_ex = self.browse(cr, uid, ids[0], context=context)
        if obj_ex.approved_qty > obj_ex.product_qty:
            return False
        return True

    def _check_products(self, cr, uid, ids, context=None):
        """ 
        Constrain function to check the product, should be in one order line.

        @return Boolean True or False
        """
        line = self.browse(cr, uid, ids[0], context=context)
        pord = self.search(cr, uid, [ ('product_id', '=', line.product_id.id), ('order_id', '=', line.order_id.id)])
        if len(pord) > 1:
            return False
        return True

    def _check_product_categ(self, cr, uid, ids, context=None):
        """ 
        Constrain function to check the product category in order line
        it should be the same of category in exchange order.

        @return Boolean True or False
        """
        line = self.browse(cr, uid, ids[0], context=context)
        if line.order_id.categ_id and line.product_id.categ_id.id != line.order_id.categ_id.id:
            return False
        return True

    _constraints = [
        (_check_negative, 
            'The quantity and approved quantity must be greater than zero. ',
            ['approved_qty']),
        (_check_approved_qty, 
            'The Approved Qty must be less than Product Qty. ',
            ['approved_qty']),
        (_check_products,
          'product must be unique ',
           ['product_id']),
        (_check_product_categ,
          'All products must be in the same Categ. ', 
          ['product_id'])]

    def copy_data(self, cr, uid, id, default=None, context=None):
        """
        Set default value to state,move_ids,delivered_qty in object

        @param default: dict type contains the values to be override during copy of object
        @return : super of exchange_order_line
        """
        if not default:
            default = {}
        default.update({'state':'draft', 'move_ids':[], 'delivered_qty':0.0})
        return super(exchange_order_line, self).copy_data(cr, uid, id, default, context)

    def onchange_product_qty(self, cr, uid, ids, product_qty):
        """
        Changing allow_req field value
        @param product_qty:product_qty

        @return :dictionary conatins the new values of:
                 approved_qty: product_qty
        """
        return {'value':{'approved_qty': product_qty, }}

    def product_id_change(self, cr, uid, ids, product, qty, uom, date_order=False,
            name=False, price_unit=False, notes=False):
        """
        Finds product_id of changed product and reset values of product_uom, 
        price_unit, name depend on product.

        @param product: Id of changed product.
        @param qty : qty of changed product
        @param uom : uom of changed product
        @param date_order : date_order of changed product
        @param name : name of changed product
        @param price_unit : price_unit of changed product
        @param notes : notes of changed product

        @return: Dictionary of values contain {'value': result}
        """
        if not product:
            return {'value': {'price_unit': price_unit or 0.0, 'name': name or '',
                'notes': notes or'', 'product_uom' : uom or False}, 'domain':{'product_uom':[]}}
        lang = self.pool.get('res.users').browse(cr, uid, uid).lang
        prod = self.pool.get('product.product').browse(cr, uid, product)
        context = {'lang':lang}
        prod_name = self.pool.get('product.product').name_get(cr, uid, [prod.id], context=context)[0][1]
        result = {
             'product_uom': prod.uom_id.id,
             'price_unit':prod.standard_price,
             'name':prod_name,
              }
        return {'value': result}

    def product_uom_change(self, cursor, user, ids, product, uom, qty=0, name='', date_order=False):
        """
        Finds UoM of changed product.
        @param product: Id of changed product.
        @param qty : qty of changed product
        @param uom : uom of changed product
        @param date_order : date_order of changed product
        @param name : name of changed product
        @param price_unit : price_unit of changed product
        @param notes : notes of changed product

        @return: Dictionary of values contain {'value': result}
        """
        res = self.product_id_change(cursor, user, ids, product,
                qty=qty, uom=uom, name=name, date_order=date_order)
        return res
        
    def onchange_category(self, cr, uid, ids, categ_id, rec_by_categ, context=None):
        if not rec_by_categ:
            return {'value':{'categ_id': categ_id}}
        domain = {'product_id':[('categ_id', '=', categ_id)]}
        return {'value':{'categ_id': categ_id},'domain': domain}
    
    def button_done(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to done.

        @return: boolean True
        """
        wf_service = netsvc.LocalService("workflow")
        res = self.write(cr, uid, ids, {'state': 'done'})
        for line in self.browse(cr, uid, ids, context=context):
            wf_service.trg_write(uid, 'exchange.order', line.order_id.id, cr)
        return res

    def button_cancel(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to cancel if move_line is not done.

        @return: boolean True or False
        """
        for line in self.browse(cr, uid, ids, context=context):
            for move_line in line.move_ids:
                if move_line.state != 'cancel':
                    raise osv.except_osv(
                            _('Could not cancel Exchange Order line!'),
                            _('You must first cancel stock moves attached to this exchange order line.'))
        return self.write(cr, uid, ids, {'state': 'cancel'})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
