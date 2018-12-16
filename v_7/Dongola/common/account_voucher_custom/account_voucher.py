# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import netsvc
import time

#----------------------------------------------------------
# Account Journal(Inherit)
#----------------------------------------------------------
class account_journal(osv.Model):

    _inherit = "account.journal"

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        """
        Inherit search method to return only cash journal when there is operation_type with supply_cash value
        
        @return: list of IDs
        """
        if context is None:
            context = {}
        ids = super(account_journal, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)
        if context and context.has_key('operation_type'):
            if context['operation_type']=='supply_cash':
                ids=self.search(cr, uid, [('type','=','cash')])
        return ids
    
    def _check_company(self, cr, uid, ids):
        """
        Constrain method to assure that the journal sequence company and 
        journal company are the same

        @return: boolean
        """
        for journal in self.browse(cr, uid, ids):
            if journal.sequence_id and journal.sequence_id.company_id != journal.company_id:
                return False  
            if journal.voucher_sequence_id and journal.voucher_sequence_id.company_id != journal.company_id:
                return False
        return True
    
    _columns = {
        'voucher_sequence_id': fields.many2one('ir.sequence', 'Voucher Sequence', domain="[('company_id','=',company_id)]", 
                                               help="The sequence used for voucher numbers in this journal."),
    }

    _constraints = [(_check_company, 'Journal company and voucher sequence company do not match.', ['company_id'])]

    def create(self, cr, uid, vals, context=None):
        """
        Inherit create method to create voucher sequence when create the journal
        
        @return: super create
        """
        if not 'voucher_sequence_id' in vals or not vals['voucher_sequence_id']:
            valss=vals.copy()
            valss.update({'name': vals['name']+'-'+ 'Voucher Sequence','code':'Voucher' +'/'+ vals['code'] })
            vals.update({'voucher_sequence_id': self.create_sequence(cr, SUPERUSER_ID, valss, context)})
        return super(account_journal, self).create(cr, uid, vals, context)

class account_voucher(osv.Model):

    _inherit = 'account.voucher'

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Inherit copy method to recalculate the account_balance for each voucher line.
        
        @return: ID of new record copied
        """
        default.update({'reference': False})
        copy_id = super(account_voucher, self).copy(cr, uid, ids, default=default, context=context)
        for line in  self.browse(cr, uid, copy_id).line_dr_ids:
            line.write({'account_balance':line.account_id.balance})
        return copy_id

    def _journal_balance(self, cr, uid, ids, field_name, arg=None, context=None):
        """
        Functional field method that return the balance of pay journal's account
        
        @return: dictionary {voucher id: balance value} 
        """
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context): 
            journal_pool = self.pool.get('account.journal')
            journal = journal_pool.browse(cr, uid, id, context=context)
            res[voucher.id] = voucher.pay_journal_id and (journal.ttype in ('purchase','payment') and voucher.pay_journal_id.default_credit_account_id.balance or voucher.pay_journal_id.default_debit_account_id.balance)
        return res

    _columns = {
        'state':fields.selection(
            [('draft','Draft'),
             ('cancel','Cancelled'),
             ('proforma','Pro-forma'),
             ('reversed','Reversed'),
             ('posted','Posted')
            ], 'Status', readonly=True, size=32, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                        \n* The \'Budget Not Appoved\' when at least one of budget confirmations related to this voucher didn\'t approve . \
                        \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Reversed\' when voucher\'s move reversed automatically reversed it\'s voucher. \
                        \n* The \'Cancelled\' status is used when user cancel voucher.'),
        'department_id':fields.many2one('hr.department', 'Department',readonly=True,states={'draft':[('readonly',False)]}),
        'account_id':fields.many2one('account.account', 'Account', required=False),
        'pay_journal_id':fields.many2one('account.journal', 'Payment Method'),
        'reference': fields.char('Ref #', size=64, readonly=True, help="Reference number."),
        'operation_type':fields.selection([('bank','Bank Feeding'), ('treasury','Treasury Feeding'),('supply_cash','Supply Cash'),('petty','Petty Cash Feeding')], 
                                          'Type',readonly=True,states={'draft':[('readonly',False)]}),
        'journal_balance': fields.function(_journal_balance, method=True, type='float', size=128, string='Balance',
                                readonly=True, store=True),
        'active': fields.boolean('Active'),
        'special': fields.boolean('Special Expense/Revenue'),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term', readonly=True, states={'draft':[('readonly', False)]},
                                        help="If you use payment terms, the due date will be computed automatically at the generation "\
                                            "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "\
                                            "The payment term may compute several due dates, for example 50% now, 50% in one month."),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid, ctx).company_id.id,
        #'tax_id': False,
        'active': 1,
        'special': 0,
    }
    
    def onchange_journal_id(self, cr, uid, ids, journal, pay_journal, line_ids, tax_id, partner_id, date, amount, ttype, company_id, pay_now, context={}):
        """
        Onchange method to set account_id and calls the super onchange method 
        based on the payment method
        
        @return: dictionary of values of fields to be updated 
        """
        journal_id = pay_now == 'pay_later' and journal or pay_journal
        partner_obj = partner_id and self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        journal_obj = journal_id and self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
        account_id = ttype in ('purchase','payment') and \
                        (pay_now == 'pay_now' and (journal_obj and journal_obj.default_credit_account_id.id) or \
                        (partner_obj and partner_obj.property_account_receivable and partner_obj.property_account_receivable.id)) \
                    or (pay_now == 'pay_now' and (journal_obj and journal_obj.default_debit_account_id.id) or \
                       (partner_obj and partner_obj.property_account_payable and partner_obj.property_account_payable.id)) or False
        balance = journal_obj and (ttype in ('purchase','payment') and journal_obj.default_credit_account_id.balance or journal_obj.default_debit_account_id.balance)
        res ={'value':{'journal_balance': balance,
                       'special':journal and self.pool.get('account.journal').browse(cr, uid, journal, context=context).special,
                       'account_id':account_id}}
        if journal_id:
            res['value'].update(self.onchange_journal(cr, uid, ids, journal_id, line_ids,tax_id, partner_id, date, amount, ttype, company_id, context=context)['value'])
        return res

    def onchange_date(self, cr, uid, ids, date, currency_id, payment_rate_currency_id, amount, company_id, context=None):
        """
        Onchange method to update context to get normal period
        
        @return: super onchange_date method 
        """
        if context is None:
            context ={}
        context.update({'account_period_prefer_normal': True})
        return super(account_voucher,self).onchange_date(cr, uid, ids, date, currency_id, payment_rate_currency_id, amount, company_id, context=context)

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        '''
        Method for getting Outstanding and Credits lines for specific partner
        
        @param id partner_id: Voucher Partner ID,
        @param id journal_id: Voucher Journal ID,
        @param float price: Voucher Amount,
        @param id currency_id: Voucher Currency ID,
        @param char ttype: Voucher Type (Sale, Purchase,Pay, receipt,...)
        @param date date: Voucher Date,
        @param list args: additional arguments,
        @return: dictionary update view values 
        '''
        if not isinstance(ids,list): 
            ids = [ids]
        if not journal_id: 
            return {}
        context = context or {}
        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        line_pool = self.pool.get('account.voucher.line')
        account_pool = self.pool.get('account.account')

        journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
        voucher_move_id = context.get('move', False)
        context_multi_currency = context.copy()
        if date: 
            context_multi_currency.update({'date': date})
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])], context=context) or False
        if line_ids and ttype in ('payment', 'receipt'):
            line_pool.unlink(cr, uid, line_ids)
        currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
        default = {
                'value': {'pre_line': False, 'currency_id':currency_id, 'payment_rate_currency_id': currency_id, 'payment_rate': 1,
                          'line_ids': [], 'line_cr_ids':[], 'line_dr_ids':[] }
            }
        if ttype == 'purchase': 
            default['value'].update({'tax_id':False})
        if not partner_id: 
            return default
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        if not partner_id and ids:
            return default
        #if pay_now =='pay_later' and ttype in ('purchase','sale'):
        account_id = (journal.type in ('sale', 'sale_refund') and (partner.property_account_receivable and partner.property_account_receivable.id)) or \
                 (journal.type in ('purchase', 'purchase_refund') and (partner.property_account_payable and partner.property_account_payable.id)) or \
                 journal.default_credit_account_id.id or journal.default_debit_account_id.id
        default['value']['account_id'] = account_id or False 
        #else :
        #    default['value']['account_id'] = False
        if journal.type not in ('cash', 'bank'):
            return default
        account_type = ttype == 'payment' and 'payable' or 'receivable'
        total_debit = ttype == 'payment' and price or 0.0
        total_credit = ttype != 'payment' and price or 0.0

        domain = [('state', '=', 'valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)]
        domain += (context.get('invoice_id', False) and [('invoice', '=', context['invoice_id'])]) or (voucher_move_id and [('move_id', '=', voucher_move_id)]) or []
        move_ids = context.get('move_line_ids', False) or move_line_pool.search(cr, uid, domain, context=context)
        move_ids.reverse()
        moves = move_line_pool.browse(cr, uid, move_ids, context=context)
        company_currency = journal.company_id.currency_id.id
        if company_currency != currency_id and ttype == 'payment':
            total_debit = currency_pool.compute(cr, uid, currency_id, company_currency, total_debit, context=context_multi_currency)
        elif company_currency != currency_id and ttype == 'receipt':
            total_credit = currency_pool.compute(cr, uid, currency_id, company_currency, total_credit, context=context_multi_currency)

        ##### Calculate Outstanding and Credits Totals #####
        for line in moves:
            if line.reconcile_partial_id:
                move = move_line_pool.browse(cr, uid, move_line_pool.search(cr, uid, [('reconcile_partial_id' , '=' , line.reconcile_partial_id.id), ('id', '!=', line.id)], context=context), context=context)
                line_partial_ids = [l.id for l in line.reconcile_partial_id.line_partial_ids]
                debit_credit = account_pool.read(cr, uid, line.account_id.id, ['debit','credit'], {'move_line_ids': line_partial_ids})
                ######### Receipt Vouchers
                if ttype == 'receipt':
                    if line.credit and debit_credit.get('debit',0) < line.credit:
                        total_credit += currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                    if line.debit and debit_credit.get('credit',0) < line.debit:
                        total_debit += currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                    continue
                ######### Payment Vouchers
                if ttype == 'payment':
                    if line.debit and debit_credit.get('credit',0) < line.debit:
                        total_debit += currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                    if line.credit and debit_credit.get('debit',0) < line.credit:
                        total_credit += currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                    continue
            total_credit += line.credit or 0.0
            total_debit += line.debit or 0.0
            
        ##### Outstanding and Credits Lines #####
        for line in moves:
            flag = True
            if line.reconcile_partial_id:
                move = move_line_pool.browse(cr, uid, move_line_pool.search(cr, uid, [('reconcile_partial_id' , '=' , line.reconcile_partial_id.id), ('id', '!=', line.id)], context=context), context=context)
                line_partial_ids = [l.id for l in line.reconcile_partial_id.line_partial_ids]
                debit_credit = account_pool.read(cr, uid, line.account_id.id, ['debit','credit'], {'move_line_ids': line_partial_ids})
                ######### Receipt Vouchers
                if line.credit and ttype == 'receipt' and debit_credit.get('debit',0) > line.credit:
                        continue
                original_amount = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                flag = False
                
                if line.debit and ttype == 'receipt' and debit_credit.get('credit',0) > line.debit:
                        continue
                original_amount = line.credit or line.debit or 0.0
                amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                flag = False
    
                ######### Payment Vouchers
                if line.debit and ttype == 'payment' and debit_credit.get('credit',0) > line.debit:
                        continue
                original_amount = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                flag = False
    
                if line.credit and ttype == 'payment' and debit_credit.get('debit',0) > line.credit:
                        continue
                original_amount = line.credit or line.debit or 0.0
                amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
                flag = False

            if flag:
                original_amount = line.credit or line.debit or 0.0
                amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)

            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, line.currency_id and abs(line.amount_currency) or original_amount, context=context_multi_currency),
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
            }
            amount = (line.credit and total_debit) or (line.debit and total_credit) or 0.0
            amount = min(amount_unreconciled, currency_pool.compute(cr, uid, company_currency, currency_id, abs(amount), context=context_multi_currency))
            
            total_debit -= line.credit and amount or 0.0
            total_credit -= line.debit and amount or 0.0
            rs['amount'] = amount
            
            if rs['amount'] > 0.0 and rs['amount'] == rs['amount_unreconciled']:
                rs['reconcile'] = True
                rs['partial_reconcile'] = False

            if rs['amount'] > 0.0 and rs['amount'] < rs['amount_unreconciled']:
                rs['partial_reconcile'] = True
                rs['reconcile'] = False
            default['value'].get('line_ids',[]).append(rs)
            
            if rs['type'] == 'cr':
                default['value'].get('line_cr_ids',[]).append(rs)
            else:
                default['value'].get('line_dr_ids',[]).append(rs)
            default['value']['pre_line'] = (ttype == 'payment' and len(default['value'].get('line_cr_ids',[])) > 0) or (ttype == 'receipt' and len(default['value'].get('line_dr_ids',[])) > 0)
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value'].get('line_dr_ids',[]), default['value'].get('line_cr_ids',[]), price,ttype)
        return default

    def action_payment_term_create(self, cr, uid, voucher, context=None):
        """
        Method creating Journal Entry for account voucher.
        
        @param voucher: object of voucher (browse)
        @return: boolean True
        """
        if context is None:
            context = {}
        move_id = True
        currency_pool = self.pool.get('res.currency')
        period_pool = self.pool.get('account.period')
        debit = 0.0
        credit = 0.0
        period_id = voucher.period_id
        current_currency = voucher.currency_id.id
        context_multi_currency = context.copy()
        context_multi_currency.update({'date': voucher.date})
        ctx = context.copy()
        ctx['fiscalyear_id'] = period_pool.browse(cr, uid, period_id.id).fiscalyear_id.id
        if voucher.payment_term:
            total_fixed = total_percent = 0
            for line in voucher.payment_term.line_ids:

                if line.value == 'fixed':
                    total_fixed += line.value_amount
                if line.value == 'procent':
                    total_percent += line.value_amount
            total_fixed = (total_fixed * 100) / (voucher.amount or 1.0)
            if (total_fixed + total_percent) > 100:
                raise osv.except_osv(_('Error !'), _("Cannot create the voucher !\nThe payment term defined gives a computed amount greater than the total voucher amount."))
        company_currency = voucher.company_id.currency_id.id
        move_lines = []
        totlines = False
        total_currency = 0
        if voucher.payment_term:
            totlines = self.pool.get('account.payment.term').compute(cr,
                    uid, voucher.payment_term.id, voucher.amount, voucher.date or False)
        if totlines:
            res_amount_currency = total_currency
            i = 0
            for t in totlines:
                if voucher.currency_id.id != company_currency:
                    amount_currency = currency_pool.compute(cr, uid,
                            company_currency, voucher.currency_id.id, t[1])
                else:
                    amount_currency = False
         
                res_amount_currency -= amount_currency or 0
                i += 1
                if i == len(totlines):
                    amount_currency += res_amount_currency
                if voucher.type == 'sale':
                    move_lines.append((0,0,{
                        'name': voucher.name or '/',
                        'debit': t[1],
                        'credit': credit,
                        'account_id': voucher.account_id.id,
                        'move_id': move_id,
                        'journal_id': voucher.journal_id.id,
                        'period_id': period_id.id,
                        'partner_id': voucher.partner_id.id,
                        'currency_id': company_currency != current_currency and  current_currency or False,
                        'amount_currency': company_currency != current_currency and sign * voucher.amount or 0.0, #FIXME: sign is not defined
                        'date': voucher.date,
                        'date_maturity': t[0],
                    }))
                elif voucher.type in ('pur_rat', 'purchase'):
                    move_lines.append((0,0,{
                        'name': voucher.name or '/',
                        'debit':debit ,
                        'credit': t[1],
                        'account_id': voucher.account_id.id,
                        'move_id': move_id,
                        'journal_id': voucher.journal_id.id,
                        'period_id': period_id.id,
                        'partner_id': voucher.partner_id.id,
                        'currency_id': company_currency != current_currency and  current_currency or False,
                        'amount_currency': company_currency != current_currency and sign * voucher.amount or 0.0, #FIXME: sign is not defined
                        'date': voucher.date,
                        'date_maturity': t[0],
                    }))
        return move_lines
    
    def action_draft_voucher(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'draft', 
        delete old workflow instance and create new one.

        @return: boolean True    
        """
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'account.voucher', id, cr)
            wf_service.trg_create(uid, 'account.voucher', id, cr)
        self.write(cr, uid, ids, {'state': 'draft'},context=context)
        return True

    def open_voucher(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'complete' and recalculate taxes.
        
        @return: boolean True
        """
        self.compute_tax(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'complete'}, context=context)
        return True

    def cancel_voucher(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'cancel', delete its move if any.
        
        @return: boolean True
        """
        super(account_voucher,self).cancel_voucher(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'cancel', 'move_id': False, 'active':0}, context=context)
        return True

    def cancel_voucher_state(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'cancel'.
        
        @return: boolean True
        """
        super(account_voucher,self).cancel_voucher(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True
    
    def compute_tax(self, cr, uid, ids, context=None):
        '''
        Calculate Voucher Amount before taxes, Tax Amount and Total Voucher Amount with Taxes,
        and update voucher record by new values.
        
        @return: boolean True
        '''
        context = context or {}
        tax_pool = self.pool.get('account.tax')
        for voucher in self.pool.get('account.voucher').browse(cr, uid, ids, context=context):
            voucher_amount = total_included = total = 0.0
            taxs = voucher.tax_id and (isinstance(voucher.tax_id,list)and voucher.tax_id or [voucher.tax_id]) or []
            for line in voucher.line_ids:
                voucher_amount += line.amount
                amount = line.untax_amount or line.amount
                computed_tax = tax_pool.compute_all(cr, uid, taxs, amount, 1)
                total_included += computed_tax.get('total_included', 0.0)
                total += computed_tax.get('total', 0.0)
                total_with_tax = [tax for tax in taxs if not tax.account_collected_id and tax.amount > 0.0]
                line_with_tax = tax_pool.compute_all(cr, uid, total_with_tax, amount, 1).get('total_included', 0.0)

                self.pool.get('account.voucher.line').write(cr, uid, [line.id], {'amount':computed_tax.get('total', 0.0),
                                                             'total_amount':line_with_tax,
                                                             'untax_amount':amount}, context=context)
            self.write(cr, uid, [voucher.id], {'amount': not taxs and voucher_amount or total_included,
                                               'tax_amount': total_included-total or 0.0})
        return True

    def onchange_payment(self, cr, uid, ids, pay_now, journal_id, partner_id, ttype='sale'):
        """
        Onchange in payment method to set pay journal False in case 
        of pay later.
        
        @param pay_now: char payment method
        @param journal_id: ID of voucher journal
        @param partner_id: ID of voucher partner 
        @param ttype: char, type of voucher
        @return: dictionary of values of fields to be updated 
        """
        res = super(account_voucher,self).onchange_payment(cr, uid, ids, pay_now, journal_id, partner_id, ttype=ttype)
        if pay_now == 'pay_later' and res:
            res['value'].update({'pay_journal_id':False})
        return res

    def action_move_line_create(self, cr, uid, ids, vals={}, context=None):
        """
        Method creating Journal Entry for account voucher.
        
        @param vals: dict of values (period, journal and date)
        @return: boolean True
        """
        if context is None:
            context = {}
        move_id = True
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        voucher_line_pool = self.pool.get('account.voucher.line')
        currency_pool = self.pool.get('res.currency')
        tax_pool = self.pool.get('account.tax')
        sequence_pool = self.pool.get('ir.sequence')
        period_pool = self.pool.get('account.period')
        ml_id=[]
        self.write(cr, uid, ids, {'state': 'posted'}, context=context)
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            period_id = vals.get('period') or voucher.period_id
            date = vals.get('date') or voucher.date
            journal_id = vals.get('journal') or voucher.pay_journal_id or voucher.journal_id
            account_id = vals.get('account') or (voucher.account_id and voucher.account_id.id) or \
                                (voucher.type in ('purchase', 'payment') and journal_id.default_credit_account_id.id) or \
                                (voucher.type in ('sale', 'receipt') and journal_id.default_debit_account_id.id)
            context_multi_currency = context.copy()
            context_multi_currency.update({'date': date})
            ctx = context.copy()
            ctx['fiscalyear_id'] = period_pool.browse(cr, uid, period_id.id).fiscalyear_id.id
            if journal_id.sequence_id:
                name = sequence_pool.get_id(cr, uid, journal_id.sequence_id.id)
            else:
                raise orm.except_orm(_('Error !'), _('Please define a sequence on the journal %s!')%(journal_id.name,))

            move_id = move_pool.create(cr, uid, {
                            'name': name,
                            'journal_id': journal_id.id,
                            'narration': voucher.narration,
                            'date': date,
                            'ref': voucher.number,
                            'period_id': period_id.id,
                        }, context=context)

            #create the first line manually
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id
            debit = 0.0
            credit = 0.0
            if voucher.type in ('purchase', 'payment'):
                credit = currency_pool.compute(cr, uid, current_currency, company_currency, voucher.amount, context=context_multi_currency)
            elif voucher.type in ('sale', 'receipt'):
                debit = currency_pool.compute(cr, uid, current_currency, company_currency, voucher.amount, context=context_multi_currency)
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            company_currency = voucher.company_id.currency_id.id
            move_lines = []
            line_total = debit - credit
            if voucher.type == 'sale':
                line_total = line_total - currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context_multi_currency)
            elif voucher.type == 'purchase':
                line_total = line_total + currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context_multi_currency)
            # Create Payment Terms move lines
            if voucher.payment_term:
                move_lines=self.action_payment_term_create(cr,uid,voucher,context=context) 
            # Create Move Line for each voucher line'''
            else :
                ml_id = move_line_pool.create(cr, uid,{
                    'name': voucher.name or '/',
                    'debit': debit,
                    'credit': credit,
                    'account_id': account_id ,
                    'move_id': move_id,
                    'journal_id': journal_id.id,
                    'period_id': period_id.id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency != current_currency and  current_currency or False,
                    'amount_currency': company_currency != current_currency and sign * voucher.amount or 0.0,
                    'date': date,
                    'date_maturity': voucher.date_due,
                    'ref': voucher.number,
                },context=context)

            rec_list_ids=[]
            for line in voucher.line_ids:
                if voucher.type == 'purchase' and 'state' in voucher_line_pool._columns and line.state != 'approve':
                    continue
                if not line.account_id:
                    raise orm.except_orm(_('Entry Error!'),_("Please make sure you enter an account for each voucher line!"))
                if not line.amount:
                    continue
                if line.amount == line.amount_unreconciled or (voucher.payment_option == 'with_writeoff' and line.amount < line.amount_unreconciled):
                    amount = line.move_line_id.amount_residual
                else :
                    amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.amount, context=context_multi_currency)
                move_line = {
                    'journal_id': journal_id.id,
                    'period_id': period_id.id,
                    'name': line.name and line.name or '/',
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': date,
                    'ref': voucher.number,
                    'budget_confirm_id': 'budget_confirm_id' in voucher_line_pool._columns and line.budget_confirm_id and line.budget_confirm_id.id,
                    'budget_line_id': 'budget_confirm_id' in voucher_line_pool._columns and line.budget_confirm_id.budget_line_id and line.budget_confirm_id.budget_line_id.id
                }
                if amount < 0:
                    amount = -amount
                    if line.type == 'dr':
                        line.type = 'cr'
                    else:
                        line.type = 'dr'

                if (line.type=='dr'):
                    line_total += amount
                    move_line['debit'] = amount
                    move_line['amount_currency'] = company_currency != current_currency and line.amount or 0.0
                else:
                    line_total -= amount
                    move_line['credit'] = amount
                    move_line['amount_currency'] = company_currency != current_currency and -line.amount or 0.0
                # Create Taxs Move Lines
                tax_line = move_line.copy()
                taxs = voucher.tax_id and (isinstance(voucher.tax_id,list)and voucher.tax_id or [voucher.tax_id]) or []
                
                for tax in tax_pool.compute_all(cr, uid, taxs, line.untax_amount, 1.00).get('taxes'):
                    tax_amount= currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, tax['amount'], context={'date': date or time.strftime('%Y-%m-%d')}, round=False)
                    tax_line.update({
                        'account_tax_id': False,
                        'account_id': tax['account_collected_id'] and tax['account_collected_id'] or move_line['account_id'],
                        'credit':  (voucher.type == 'purchase' and tax_amount<0 and -tax_amount) or (voucher.type == 'sale' and tax['amount']>0 and tax['amount']) or 0.0,
                        'debit': (voucher.type == 'purchase' and tax_amount>0 and tax_amount) or (voucher.type == 'sale' and tax['amount']<0 and -tax['amount']) or 0.0,
                        'amount_currency': company_currency != current_currency and tax['amount'] or 0.0,
                        'budget_confirm_id': 'budget_confirm_id' in voucher_line_pool._columns and 
                                            (not tax['account_collected_id'] or tax['account_collected_id'] == move_line['account_id']) and line.budget_confirm_id.id,
                        'budget_line_id': 'budget_confirm_id' in voucher_line_pool._columns and (not tax['account_collected_id'] or tax['account_collected_id'] == move_line['account_id']) and 
                                            line.budget_confirm_id.budget_line_id and line.budget_confirm_id.budget_line_id.id
                    })
                    move_line_pool.create(cr, uid, tax_line, context=context)
                voucher_line=move_line_pool.create(cr, uid, move_line, context=context)

                if line.move_line_id.id:
                    #voucher_line = move_line_pool.create(cr, uid, move_line)
                    rec_ids = [voucher_line, line.move_line_id.id]
                    rec_list_ids.append(rec_ids)

            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, context)

            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
            }, context=context)
            move_pool.write(cr, uid, [move_id],{'line_id': move_lines and move_lines,},context={'check':False})
            move_pool.post(cr, uid, [move_id], context=context)
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return ml_id

    def create(self, cr, uid, vals, context=None):
        """
        Inherit create method to set the sequence of the voucher based on payment method
        
        @param vals: dictionary of record values to be created
        @return: super create method
        """
        journal_id = vals.get('type') in ('sale','purchase','payment') and vals.get('journal_id') or vals.get('pay_journal_id' )
        if journal_id:
            journal_obj = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            if journal_obj.voucher_sequence_id:
                vals['number'] = self.pool.get('ir.sequence').get_id(cr, uid, journal_obj.voucher_sequence_id.id)
            else:
                raise orm.except_orm(_('Error!'), _('Journal %s has no sequence defined for voucher.') % journal_obj.name)
        return super(account_voucher,self).create(cr, uid, vals, context)

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        """
        Onchange method to resent the company ID based on user company
        
        @return: super onchage_amount method
        """
        company_id = company_id or self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        return super(account_voucher, self).onchange_amount( cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=context)

    def _check_date(self, cr, uid, ids, context=None):
        """
        Constraint method check that the voucher date is with in voucher period when journal allow this check
        
        @return: boolean
        """
        for l in self.browse(cr, uid, ids, context=context):
            if l.journal_id.allow_date and l.state not in ['draft','cancel' ]:
                if not time.strptime(l.date[:10],'%Y-%m-%d') >= time.strptime(l.period_id.date_start, '%Y-%m-%d') or not time.strptime(l.date[:10], '%Y-%m-%d') <= time.strptime(l.period_id.date_stop, '%Y-%m-%d'):
                    return False
        return True

    def _required_line_id(self, cr, uid, ids, context=None):
        """
        Constraint method make sure that any nun draft voucher has lines
        
        @return: boolean
        """
        if self.search(cr, uid,[('id', 'in', ids),('type','in',('sale','purchase')),('line_ids', '=', False),('state', '!=', 'draft')], context=context):
            return False
        return True

    def _amount_check(self, cr, uid, ids, context=None):
        """
        Constraint method make sure that all voucher lines have amount when voucher not draft
        
        @return: boolean
        """
        voucher_ids = self.search(cr, uid, [('type','in',('sale','purchase')),('state','!=','draft'),('id','in',ids)], context=context)
        if self.pool.get('account.voucher.line').search(cr, uid,[('amount','=',0),('voucher_id','in',voucher_ids)], context=context):
            return False
        return True

    def _total_amount_check(self, cr, uid, ids, context=None):
        """
        Constraint method make sure that voucher has amount when it is not draft or cancel
        
        @return: boolean
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.state not in ['draft','cancel' ] and voucher.amount==0.0:
                return False
        return True

    def _period_check(self, cr, uid, ids, context=None):
        """
        Constraint method to make sure the voucher's period is not closed before creating move
        
        @return: boolean
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if not  voucher.move_id and voucher.state not in ['draft','cancel' ] and voucher.period_id.state!='draft':
                return False
        return True

    def _journal_balance_check(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.state!='draft' and voucher.operation_type and voucher.amount>voucher.journal_balance:
                return False
        return True
    
    _constraints = [
        (_required_line_id, "Operation is not completed, Accounts & amounts details are missing!", ['line_ids']), 
        (_amount_check, "Operation is not completed, Account's amount shouldn't be zero!", []), 
        (_total_amount_check, "Operation is not completed, Total amount shouldn't be zero!", []), 
        (_period_check, "There is no period defined for this date or closed!", []), 
        (_check_date, 'The date of your operation is not in the defined period! You should change the date or remove this constraint from the journal.', ['date']),
        (_journal_balance_check,'Pay Journal Balance is less than Operation Amount',['operation_type','amount','journal_balance'])
    ]

class account_voucher_line(osv.Model):
    """
    Inherit voucher line to set values on change of reconcile, amount and account.
    """
    _inherit = 'account.voucher.line'

    def _account_balance(self, cr, uid, ids, field_name, arg=None, context=None):
        """
        Functional field method that return the balance of line's account
        
        @return: dictionary {voucher line id: balance value} 
        """
        res = {}
        for voucher_line in self.browse(cr, uid, ids, context=context):
            if voucher_line.account_id:
                res[voucher_line.id] = voucher_line.account_id.balance
        return res
   
    _columns = {
        'total_amount': fields.float('Total Amount'),
        'account_balance': fields.function(_account_balance, method=True, type='float', size=128, string='Balance',
                                readonly=True, store=True),
        'partial_reconcile': fields.boolean('Partial Reconcile'),
        'tax_ids': fields.many2many('account.tax', string='Taxes')
    }
    def _account_line_id(self, cr, uid, ids, context=None):
        """
        Constraint method that prevent using same account for voucher & voucher line when operation_type has value
        
        @return: boolean
        """
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.voucher_id.operation_type:
            if obj.account_id.id == obj.voucher_id.account_id.id:
                return False
        return True

    def _amount_line_id(self, cr, uid, ids, context=None):
        """
        Constraint method that prevent enter negative amount when voucher pay journal is special
        
        @return: boolean
        """
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.voucher_id.pay_journal_id.special == True:
            if obj.amount < 0:
                return False
        return True

    _constraints = [
        (_account_line_id, "You can not feed the source account ", ['account_id']), 
#         (_amount_line_id, "check the amount it must be positive ! ", ['amount']), 
    ]    

    def onchange_account(self, cr, uid, ids, account_id, context={}):
        """
        Onchange method to update the account balance when changing account_id.
         
        @return: dictionary of fields value to be updated 
        """
        val={}
        if account_id:
            account = self.pool.get('account.account').browse(cr, uid, account_id, context=context)
            val.update({'account_balance': account.balance})
            if account.user_type.analytic_required :
                dummy, analytic_account_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_custom', 'normal_analytic_account')
                val.update({'account_analytic_id':analytic_account_id and analytic_account_id[0]})
        return {'value':val}

    def onchange_reconcile(self, cr, uid, ids, reconcile, partial_reconcile, amount, amount_unreconciled, move_line_id, context={}):
        """
        Onchange method to update the amount based on reconcile option that was selected
 
        @param reconcile: boolean reconcile field in voucher line
        @param partial_reconcil: boolean reconcile field in voucher line
        @param amount: float amount of voucher line
        @param amount_unreconciled: float amount of unreconciled amount of voucher line
        @param move_line_id: list of voucher move lines
        @return: dictionary of amount value to be updated 
        """
        return {'value': { 'amount': reconcile and amount_unreconciled or partial_reconcile and amount or 0.0}}

    def onchange_amount(self, cr, uid, ids, amount, amount_unreconciled = False, context={}):
        """
        Onchange method on amount to update the reconcile option based on amount entered.
         
        @param amount: float amount of voucher line
        @param amount_unreconciled: float amount of unreconciled amount of voucher line
        @return: dictionary of fields value to be updated 
        """
        vals = {
                'reconcile': (amount == amount_unreconciled),
                'partial_reconcile': (amount < amount_unreconciled),
                'untax_amount': amount
                }
        return {'value': amount and vals or {}}
        


#CHECKME: When reverse move the voucher state should be reversed!! 
class account_move(osv.Model):
    """
    Inherit the move object to update voucher when it's move is reversed
    """
    _inherit = 'account.move'

    def revert_move(self, cr, uid, ids, journal, period, date, reconcile=True, context=None):
        """
        Inherit revert method to update the voucher state to reversed consequently.
         
        @param journal: ID of voucher journal
        @param period: ID of voucher period
        @param date: date of move 
        @param reconcile: boolean reconcile 
        @return: ID of new reversed move created
        """
        move_id = super(account_move, self).revert_move(cr, uid, ids, journal, period, date, reconcile=reconcile, context=context)
        voucher_pool = self.pool.get('account.voucher')
        voucher_ids = voucher_pool.search(cr, uid, [('move_id','in',ids)], context=context)
        voucher_pool.write(cr, uid, voucher_ids, {'state':'reversed'}, context=context)
        return move_id


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 943
