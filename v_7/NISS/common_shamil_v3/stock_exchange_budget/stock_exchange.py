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

STATE_SELECTION = [
        ('draft', 'Request for Exchange'),
        ('confirmed', 'Waiting Department Approval'),
        ('category_manager', 'Waiting for category manager'),
        ('approved_qty', 'Waiting Budget Check'),
        ('budget_yes', 'Budget Approved'),
        ('budget_no', 'Budget Cancelled'),
        ('approved', 'Approved'),
        ('picking', 'Picking'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

# ----------------------------------------------------
# Exchange Order 
# ----------------------------------------------------
class exchange_order(osv.Model):
    
    _inherit= "exchange.order"
   
    _columns = {
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
        'acc_bud_confirm_id': fields.many2one('account.budget.confirmation', 'Budget Confirmation', readonly=True),
        'account_analytic_id': fields.related('acc_bud_confirm_id', 'analytic_account_id', type='many2one', relation='account.analytic.account', string='Analytic Account', store=True, readonly=True),
        'account_id': fields.related('acc_bud_confirm_id', 'general_account_id', type='many2one', relation='account.account', string='Account', store=True, readonly=True),        
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        Coping exchange order record and reset values
        @param default: dict type contains the values to be override during copy of object
        @return: super copy function of exchange_order
        """
        if default is None:
            default = {}
        default = default.copy()
        default['acc_bud_confirm_id'] = False
        res = super(exchange_order, self).copy(cr, uid, id, default, context)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        """ 
        Workflow function Changes order state to cancel.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for order in self.browse(cr, uid, ids, context=context):
            if order.acc_bud_confirm_id:
                wf_service.trg_validate(uid, 'account.budget.confirmation', order.acc_bud_confirm_id.id, 'cancel', cr)
        res = super(exchange_order, self).action_cancel(cr, uid, ids, context)
        return True

    def action_cancel_order(self, cr, uid, ids, context=None):
        """ 
        Workflow function Changes order state to cancel related by budget confirmation id.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for order in self.browse(cr, uid, ids, context=context):
            if order.acc_bud_confirm_id:
                wf_service.trg_validate(uid, 'account.budget.confirmation', order.acc_bud_confirm_id.id, 'cancel', cr)
        res = super(exchange_order, self).action_cancel_order(cr, uid, ids, context)
        return True


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
        self.changes_state(cr, uid, ids,{'state': 'approved_qty'},context={})
        return confirmation 
 
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
                if exch_obj.test_finished(cr, uid, [line.id]) == True:
                    if line.state != 'done':
                        write_done_ids.append(line.id)
                else:
                    finished = False
                if exch_obj.test_cancel(cr, uid, [line.id]) == True:
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

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
        Prepare the dict of values to create the new picking for a
        exchange order. This method may be overridden to implement custom
        picking generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order.line record to invoice
        @return: dict of values to create() the picking
        """
        res = super(exchange_order, self)._prepare_order_picking(cr, uid, order, context)
        new_dict={
              'analytic_account_id':order.account_analytic_id and order.account_analytic_id.id,
              'account_id':order.account_id and order.account_id.id, }
        res.update(new_dict)
        return res

# ----------------------------------------------------
# Order Line
# ----------------------------------------------------
class exchange_order_line(osv.Model):

    _inherit = 'exchange.order.line'

    _columns = {
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
               }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
