# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import netsvc
import time
import datetime
from openerp import workflow
from openerp import netsvc

class account_invoice(osv.Model):
    """
    Standing orders model for payments scheduled in installments
    """
    _inherit='account.invoice'

    
    def action_number(self, cr, uid, ids, context=None):
        """
        modify the update query and delete the check with 
        ref value cause it will not be empty,
        and add sequence to the move
        """
        if context is None:
            context = {}
        #TODO: not correct fix but required a frech values before reading it.
        self.write(cr, uid, ids, {})

        for obj_inv in self.browse(cr, uid, ids, context=context):
            invtype = obj_inv.type
            number = obj_inv.number
            move_id = obj_inv.move_id and obj_inv.move_id.id or False
            reference = obj_inv.reference or ''

            self.write(cr, uid, ids, {'internal_number': number})

            if invtype in ('in_invoice', 'in_refund'):
                if not reference:
                    ref = self._convert_ref(cr, uid, number)
                else:
                    ref = reference
            else:
                ref = self._convert_ref(cr, uid, number)
            
            sequence = obj_inv.move_id.period_id.sequence_id.id
            seq_no = self.pool.get('ir.sequence').get_id(cr, uid, sequence, context=context)

            cr.execute('UPDATE account_move SET ref=%s,internal_sequence_number=%s ' \
                    'WHERE id=%s',
                    (ref, seq_no, move_id))
            cr.execute('UPDATE account_move_line SET ref=%s ' \
                    'WHERE move_id=%s',
                    (ref, move_id))
            cr.execute('UPDATE account_analytic_line SET ref=%s ' \
                    'FROM account_move_line ' \
                    'WHERE account_move_line.move_id = %s ' \
                        'AND account_analytic_line.move_id = account_move_line.id',
                        (ref, move_id))
        return True

    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()
            
    def _get_invoice_from_line(self, cr, uid, ids, context=None):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    def _get_invoice_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines"""

        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.move_creation=='invoice':
                return super(account_invoice,self).action_move_create(cr, uid, ids, context=context)

          
    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        """
        Functional field method that calculate the residual amount that doesn't pay yet
        and change the order state to 'paid' when full payment is made
        
        @return: dictionary of {record id: residual amount}
        """
        #from openerp import workflow
        wf_service = netsvc.LocalService("workflow")
        result = {}
        amount=0.0
        for order in self.browse(cr, uid, ids, context=context):
            if order.move_creation=='invoice':
                return super(account_invoice,self)._amount_residual(cr, uid, ids, name, args, context=context)
            for line in order.invoice_line:
                amount+=line.price_subtotal
            result[order.id] = amount -sum([vouher.amount for vouher in order.voucher_ids if vouher.state in ['pay','receive','posted','done']])
            if result[order.id] == 0.0 :
                
                #self.write(cr, uid, order.id, {'state':'paid'}, context=context)
                wf_service.trg_validate(uid, 'account.invoice', order.id, 'to_paid', cr)
                #workflow.trg_validate(uid, 'account.invoice', order.id, 'to_paid', cr)
        return result

    def _get_voucher(self, cr, uid, ids, context=None):
        """
        Method that maps record ids of a trigger model to ids of the corresponding records 
        in the source model (whose field values need to be recomputed).
        
        @param: list of voucher ids
        @return:  list of payment permanent ids
        """
        voucher = self.pool.get('account.voucher')
        return [l.invoice_id.id for l in voucher.browse(cr, uid, ids, context=context)]

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        
        journal_obj = self.pool.get('account.journal')
        res = super(account_invoice,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        ttype = context.get('journal_type', False)
        for field in res['fields']:
            if field == 'journal_id':
                journal_select = journal_obj._name_search(cr, uid, '', [('type', '=', ttype),('special','=',False)], context=context, limit=None, name_get_uid=1)
                res['fields'][field]['selection'] = journal_select
        return res

    _columns = {
        'order_nature': fields.selection([('revocable', 'Revocable'), ('irrevocable', 'Irrevocable'), ],
                                         'Order Nature'),
        'account_id': fields.many2one('account.account', 'Account', required=False, help="The partner account used for this invoice."),
        'revocable_conditions': fields.selection([('work', 'Completion of work'), ('delivery', 'Inventories delivery'),
                                                  ('time', 'Interpolation time'), ], 'Revocable Conditions'),
        'move_creation':fields.selection([('invoice', 'With Invoice'), ('voucher', 'With Voucher')], 'Move Creation',required=True),
        'condition_descriptions': fields.char('Condition Descriptions', size=256),
        'voucher_ids': fields.one2many('account.voucher', 'invoice_id', 'Vouchers', ondelete='cascade',readonly=True,),
        'journal_id': fields.many2one('account.journal', 'Journal', domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale_refund'], 'in_refund': ['purchase_refund'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id),('special','=',False)]"),
        'residual': fields.function(_amount_residual, digits_compute=dp.get_precision('Account'),string='Balance',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','move_id'], 50),
                'account.invoice.tax': (_get_invoice_tax, None, 50),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 50),
                'account.move.line': (_get_invoice_from_line, None, 50),
                'account.move.reconcile': (_get_invoice_from_reconcile, None, 50),
            },
            help="Remaining amount due."),
        'state' : fields.selection([('draft', 'Draft'), ('proforma','Pro-forma'),
                                    ('proforma2','Pro-forma'), ('complete', 'Completed'),
                                    ('confirm','Confirmed'), ('review', 'Reviewed'),
                                    ('open','Open'),('paid','Paid'),
                                    ('cancel', 'Cancelled'),('done', 'Done')],
                                    'Status', readonly=True),
    }

    _defaults = {
        'date_invoice': time.strftime('%Y-%m-%d'),
        'move_creation':'invoice'
    }

    def onchange_date(self, cr, uid, ids, date, company_id, context=None):
        """
        This Method change the period of order according to selected date 
        
        @param date: latest value from user input for field date
        @return: Returns a dict which contains new values, and context
        """
        if context is None: context = {}
        ctx = context.copy()
        ctx.update({'account_period_prefer_normal': True, 'company_id': company_id})
        pids = self.pool.get('account.period').find(cr, uid, date, context=ctx)
        if pids:
            return {'value': {'period_id':pids[0]}}

    def copy(self, cr, uid, ids, default=None, context=None):
        """
        Inherit copy method to reset voucher_ids & reference fields value in the new record
        
        @return: super copy
        """
        default = default or {}
        default.update({'voucher_ids' : []})
        return super(account_invoice, self).copy(cr, uid, ids, default=default, context=context)

    def to_complete(self, cr, uid, ids, context=None):
        """
        Workflow method that make sure records have lines before complete it
  
        @return: change records state to 'complete'
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.type=='in_invoice' and not order.invoice_line:
                raise orm.except_orm(_('Invalid Action!'), _('Please create some Payment Permanent lines.'))
        return self.write(cr, uid, ids, {'state':'complete'}, context=context)

    def to_confirm(self, cr, uid, ids, context=None):
        """
        Workflow method that make sure records have lines before confirm it
  
        @return: change records state to 'confirm'
        """
        for order in self.browse(cr, uid, ids, context=context):
            if not order.invoice_line:
                raise orm.except_orm(_('Invalid Action!'), _('Please create some Invoice lines.'))
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)
        
    def action_cancel(self, cr, uid, ids, context=None):
        """
        Workflow method that delete the workflow instance & create new one 
        
        @return: change records state to 'cancel'
        """
        voucher_obj = self.pool.get('account.voucher')
        for order in self.browse(cr, uid, ids, context=context):
            if order.move_creation=='invoice':
                return super(account_invoice,self).action_cancel(cr, uid, ids,context=context)
            if not order.comment:
                raise orm.except_orm(_('Invalid Action!'), _('Please write cancel reasons in Internal Notes.'))
            voucher_ids=[vouher.id for vouher in order.voucher_ids if vouher.state not in ['pay','receive','posted','done']]
            if voucher_ids:
                voucher_obj.cancel_voucher(cr, uid, voucher_ids, context)
                voucher_obj.write(cr, uid, voucher_ids, {'narration':order.comment}, context=context)
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)

    
    
    def run_scheduler(self, cr, uid, context=None):
        ids=[]
        ids = self.search(cr, uid, [('state', '=', 'open')], context=context)
        context['due_payment']=True
        
        return self.generate_orders(cr, uid, ids, context=context)

    def generate_orders(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'done'.
        
        @return: boolean True
        """
        voucher_pool = self.pool.get('account.voucher')
        payment_term_obj = self.pool.get('account.payment.term')
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            total_fixed = total_percent = 0
            
            for line in order.payment_term.line_ids:
                if line.value == 'fixed':
                    total_fixed += line.value_amount
                if line.value == 'procent':
                    total_percent += line.value_amount

            total_fixed = (total_fixed * 100) / (order.amount_total or 1.0)
            if (total_fixed + total_percent) > 100:
                raise orm.except_orm(_('Error!'), _("Can not create the payments !\n\
                The related payment term is probably miss configured as it gives a computed amount greater than the total permanent payment amount. \
                The latest line of your payment term must be of type 'balance' to avoid rounding issues."))
            totlines1 = []
            if context.get('due_payment')==True or context.get('due_payment')==None:
                current_date=datetime.date.today()+datetime.timedelta(days=order.company_id.interval_number)
                date_invo=datetime.datetime.strptime(order.date_invoice, '%Y-%m-%d').date()
                if date_invo <= current_date:
                    for o in order.invoice_line:
                        record = payment_term_obj.compute(cr, uid, order.payment_term.id, o.price_subtotal,
                        order.date_invoice or False, context=context)
                        list = []
                        for i in record:
                            list.append((i[0],(i[1],o.id)))
                        totlines1 += list
                        d = {}
                    for k, v in totlines1:
                        d.setdefault(k, [k]).append(v)
                        totlines = map(tuple, d.values())
                    for t in totlines :
                        order_date = t[0]
                        entered_date = datetime.datetime.strptime(order_date, '%Y-%m-%d')
                        entered_date = entered_date.date()
                        account_id = (order.partner_id.property_account_payable and order.partner_id.property_account_payable.id) or \
                                                (order.journal_id.default_credit_account_id and order.journal_id.default_credit_account_id.id)

                        voucher_lines = []
                        invoice_line = self.pool.get('account.invoice.line')
                        for fragment in t[1:]:
                            invoice = invoice_line.browse(cr,uid,fragment[1])
                            voucher_line = {
                                        "account_id":invoice.account_id and invoice.account_id.id or False,
                                        "account_analytic_id":invoice.account_analytic_id and invoice.account_analytic_id.id or False,
                                        "amount":fragment[0],
                                        "name":invoice.name,
                                        'type':'dr',
                                        'budget_confirm_id':invoice.budget_confirm_id,
                                        }
                            voucher_lines.append((0,0,voucher_line))
                        
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
                               'invoice_id': order.id,
                               'line_ids':voucher_lines,
                               'amount':res.get("amount", 0.0),
                        }
                        
                        voucher_pool.create(cr, uid, voucher_dict, context=context)
            return self.write(cr, uid, ids, {'state':'done'}, context=context)


    def _check_date(self, cr, uid, ids, context=None):
        """
        Constraint method that make sure the date is within the selected period when journal is allowing this check
        
        @return: boolean
        """
        for l in self.browse(cr, uid, ids, context=context):
            if l.journal_id.allow_date and l.state not in ['draft','cancel' ]:
                if not time.strptime(l.date_invoice[:10],'%Y-%m-%d') >= time.strptime(l.period_id.date_start, '%Y-%m-%d') or not time.strptime(l.date_invoice[:10], '%Y-%m-%d') <= time.strptime(l.period_id.date_stop, '%Y-%m-%d'):
                    return False
        return True

    _constraints = [
        (_check_date, 'The date of your operation is not in the defined period! You should change the date or remove this constraint from the journal.', ['date']),
    ]
    def line_get_convert(self, cr, uid, line, part, date, context=None):
        """
        Add budget_confirm_id field to result dictionary

        @param part: partner_id
        @param date: date of invoice
        @return: dictionary of values to be updated
        """
        res = super(account_invoice, self).line_get_convert(cr, uid, line, part, date, context)
        res.update({
               'budget_confirm_id': line.get('budget_confirm_id', False),
        })
        return res

class account_invoice_line(osv.osv):

    _inherit='account.invoice.line'

    _columns = {
        'budget_confirm_id':  fields.many2one('account.budget.confirmation', 'Confirmation'),
    }

    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context)
        res.update({
               'budget_confirm_id': line.budget_confirm_id.id
        })
        return res
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
