# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import netsvc
import datetime

class purchase_order(osv.Model):

    _inherit = 'purchase.order'

    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Order'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('waiting_budget', 'Waiting for budget Approve'),
        ('budget_approved', 'Budget Approved'),]
        
    _columns = {
       'state': fields.selection(STATE_SELECTION, 'Status', readonly=True, help="The status of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' status. Then the order has to be confirmed by the user, the status switch to 'Confirmed'. Then the supplier must confirm the order to change the status to 'Approved'. When the purchase order is paid and received, the status becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the status becomes in exception.", select=True),
    }


    def action_budget_create(self, cr, uid, ids, context=None):
        """
        This method creates budget confirmation for selected requisition by sending
        the total price and ordered department to budget confirmation.

        @param self: object pointer
        @param cr: database cursor
        @param confirmation_id: The confirmation id  which is created  
        @return: IDs of created confirmations
        """
        payment_term_obj = self.pool.get('account.payment.term')
        for porder in self.browse(cr, uid, ids, context=context):
            period = self.pool.get('account.period').find(cr,uid,porder.date_order, context = context)[0] 
            result = []
            confirmation_dict={
                    'reference': porder.name,
                    'period_id': period,
                    'partner_id':porder.partner_id.id,
                    'amount': porder.amount_total,
                    'note':'',
                    'date':porder.date_order,
                    'type':'purchase'}

            for line in porder.order_line:
                confirmation_ids=[]
                account_id = self._choose_account_from_po_line(cr, uid, line, context=context)
                notes = _("Purchase Approval: %s \nDescription: %s.\nDate: %s  \nProducts: %s ") % (porder.name , porder.notes , porder.date_order , line.name )

                result= payment_term_obj.compute(cr, 
                               uid, porder.payment_term_id.id, line.price_subtotal,porder.date_order or False, context=context)
                for  r in  result:
                    confirmation_dict.update(
                        {'date':r[0],
                        'amount':r[1],
                        'note':notes,
                        'name':'/',
                        'general_account_id': account_id,
                        'account_analytic_id': line.account_analytic_id.id or False,
                        })
                    confirmation_id = self.pool.get('account.budget.confirmation').create(cr, uid, confirmation_dict)
                    confirmation_ids.append(confirmation_id)
                line.write({'confirmation_ids':[(6, 0, confirmation_ids)] ,'state': 'waiting_budget'})
            self.write(cr, uid, ids, {'state': 'waiting_budget'})
        return True

    def confirmation_get(self, cr, uid, ids, *args):
        res = []
        for porder in self.browse(cr, uid, ids, context={}):
            for line in porder.order_line:
                res += [x.id for x in line.confirmation_ids]
        return res

    def test_state(self, cr, uid, ids, mode, *args):
        assert mode in ('approved', 'canceled'), _("invalid mode for test_state")
        approved = True
        canceled = False
        waiting = False
        porder_line = self.pool.get('purchase.order.line')
        for porder in self.browse(cr, uid, ids, context={}):
            for line in porder.order_line:
                if all([x.state in ('valid' ,'cancel') for x in line.confirmation_ids]):
                    if all([x.state == 'valid' for x in line.confirmation_ids]):
                        if line.state != 'budget_approved':
                            line.write({'state': 'budget_approved'})
                    if all([x.state == 'cancel' for x in line.confirmation_ids]):
                        if line.state != 'cancel':
                            line.write({'state': 'cancel'})
                else:
                    approved = False    
                if all([x.state == 'unvalid' for x in line.confirmation_ids]):
                    if line.state != 'no_approve':
                        line.write({'state': 'no_approve'})
            canceled= self.test_cancel(cr, uid, [porder.id], context={})
        if mode == 'approved':
            if  canceled:
                return False
            return approved
        elif mode == 'canceled':
            return canceled

    def test_cancel(self, cr, uid, ids, context=None):
        for porder in self.browse(cr, uid, ids, context=context):
            if all([x.state == 'cancel' for x in porder.order_line]):
                return True
        return False

class purchase_order_line(osv.Model):

    _inherit = 'purchase.order.line'

    _columns = {
        'confirmation_ids': fields.many2many('account.budget.confirmation', 'purchase_order_line_confirmation_rel', 'order_line_id', 'confirmation_id', 'Budget Confirmation ', readonly=True),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled'),
                           ('waiting_budget', 'Waiting for budget Approve'),('budget_approved', 'Budget Approved'), 
                           ('no_approve','Budget Not Appoved'),], 'Status', required=True, readonly=True,
                                  help=' * The \'Draft\' status is set automatically when purchase order in draft status. \
                                       \n* The \'Confirmed\' status is set automatically as confirm when purchase order in confirm status. \
                                       \n* The \'Done\' status is set automatically when purchase order is set as done. \
                                       \n* The \'Cancelled\' status is set automatically when user cancel purchase order.'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({'confirmation_ids':[]})
        return super(purchase_order_line, self).copy_data(cr, uid, id, default, context)

class account_payment_permanent_line(osv.Model):

    _inherit = 'account.payment.permanent.line'

    _columns = {
        'confirmation_ids': fields.one2many('account.budget.confirmation', 'budget_line_id', 'Confirmations'),
    }

class account_payment_permanent(osv.Model):

    _inherit = 'account.payment.permanent'

    def generate_orders(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'done'.
        @return: boolean True
        """
        voucher_pool = self.pool.get('account.voucher')
        payment_term_obj = self.pool.get('account.payment.term')
        account_budget_confirmation_obj = self.pool.get('account.budget.confirmation')
        period_obj = self.pool.get('account.period')
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
    #################################to remind
            total_fixed = total_percent = 0
            for line in order.payment_term.line_ids:
                if line.value == 'fixed':
                    total_fixed += line.value_amount
                if line.value == 'procent':
                    total_percent += line.value_amount
            total_fixed = (total_fixed * 100) / (order.amount or 1.0)
            if (total_fixed + total_percent) > 100:
                raise orm.except_orm(_('Error!'), _("Can not create the payments !\n\
                The related payment term is probably miss configured as it gives a computed amount greater than the total permanent payment amount. \
                The latest line of your payment term must be of type 'balance' to avoid rounding issues."))
            # create one move line for the total and possibly adjust the other lines amount
            totlines1 = []
            for o in order.line_ids:
                totlines1 += payment_term_obj.compute(cr, uid, order.payment_term.id, o.amount, order.date or False, context=context)
     
            d = {}
            for k, v in totlines1:
                d.setdefault(k, [k]).append(v)
                totlines = map(tuple, d.values())

            for t in totlines :
                #to substract date from the interval number 
                order_date = t[0]
                entered_date = datetime.datetime.strptime(order_date, '%Y-%m-%d')
                entered_date = entered_date.date()
                account_id = (order.partner_id.property_account_payable and order.partner_id.property_account_payable.id) or \
                                    (order.journal_id.default_credit_account_id and order.journal_id.default_credit_account_id.id)
                period_id = period_obj.find(cr, uid, t[0], context=context)[0]

                list_confirm = [conf.id for conf in o.confirmation_ids]
                confirmations = account_budget_confirmation_obj.search(cr, uid, [('id','in', list_confirm),('period_id','=', period_id)], context=context) #('date','=',t[0]),

                for confirm in confirmations:
                    confirm_id = confirm

                voucher_lines = [(0, 0, {'name':ol.name, 'account_id':ol.account_id.id, 'type':'dr',
                                         'amount':t[count + 1], 'account_analytic_id':ol.account_analytic_id.id, 'budget_confirm_id': confirm_id   })
                                 for count, ol in enumerate(order.line_ids)]
                res = voucher_pool.onchange_price(cr, uid, 0, voucher_lines, [], partner_id=order.partner_id.id, context=context).get("value", {})
                voucher_dict = {
                   'partner_id' : order.partner_id.id,
                   'account_id': account_id,
                   'company_id' : order.company_id.id,
                   'journal_id' : order.journal_id.id,
                   'period_id': order.period_id.id,
                   'type':'purchase',
                   'date' : t[0],
                   'reference': order.name,
                   'payment_permanent_voucher_id': order.id,
                   'line_ids':voucher_lines,
                   'amount':res.get("amount", 0.0)
                }
                voucher_pool.create(cr, uid, voucher_dict, context=context)
            return self.write(cr, uid, ids, {'state':'done'}, context=context)


