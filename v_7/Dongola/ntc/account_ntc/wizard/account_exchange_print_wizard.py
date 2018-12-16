# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar
from datetime import datetime

class account_exchange_print_wizard(osv.osv_memory):
    """
    Wizard to print payment exchange
    """
    _name = "account.exchange.print.wizard"

    def _exchange_journal_seq(self, journal_id, context=None):
        """
        Check if Journal check_seq defined or not.
        
        @return: boolean True if defined or raise an exception.
        """
        if not journal_id.check_sequence:
            raise osv.except_osv(_('Warning'),_('Please add "Check or Exchange Sequence" for journal %s')%(journal_id.name))
        return True
        
    def _get_nxt_exchange_no(self, cr, uid, context=None):
        """
        @return: int next exchange number according to Journal's exchange_seq
        """
        sequence_pool = self.pool.get('ir.sequence')
        move = context['active_model'] == 'account.move' and self.pool.get('account.move').browse(cr, uid, context.get('active_id',[]), context=context)
        journal_id= move.journal_id
        if self._exchange_journal_seq(journal_id, context=context):
            return move and sequence_pool.read(cr, uid, journal_id.check_sequence.id, ['number_next_actual'],  context=context)['number_next_actual']

    def _get_state(self, cr, uid, context=None):
        """ 
        @return: char default value of wizard state.
        """
        move = self.pool.get('account.move').browse(cr, uid, context.get('active_id',False) , context=context)
        return move and (context['active_model'] == 'account.move' and move.state != 'closed' and 'update' or 'draft')

    def _get_msg(self, cr, uid, context=None): 
        """
        @return: char default value of wizard displaying message.
        """
        voucher_pool = self.pool.get('account.voucher')
        if context['active_model'] == 'account.move' and self.pool.get('account.move').browse(cr, uid, context.get('active_id',False) , context=context).state != 'closed':
            return _("Your payment's move is not Closed!")
        else:
            return _("Please verify this exchange number matches the starting preprinted number of the exchange existing! If not, enter new exchange number below.")

    _columns =  {
        'new_no': fields.integer('Update Exchange Number'),
        'nxt_exch_no': fields.char('Next Exchange Number', size=64),
        'new_exch_no': fields.integer('Update Exchange Number'),
        #'status': fields.selection([('voided', 'Voided'), ('lost', 'Lost'), ('unk', 'Unknown')], 'Status'), 
        'msg': fields.text('Message', translate=True),
        'state': fields.selection([('draft', 'Draft'), ('add', 'Add'), ('update', 'Update'), ('reprint_new', 'Reprint')], 'States'),
    }

    _defaults = {
           'new_no': _get_nxt_exchange_no,
           'state': _get_state,
           'msg': _get_msg,
    }

    def exchange_payment(self, cr, uid, ids, context=None):
        """
        This method for creating new exchange Payment or update the exchange No.
        
        @return: dictionary, an action to close wizard
        """
        data = self.browse(cr, uid, ids, context=context)[0]
        check_log_pool = self.pool.get('check.log')
        sequence_pool = self.pool.get('ir.sequence')
        move_pool = self.pool.get('account.move') 
        move_line_pool = self.pool.get('account.move.line')

        voucher_obj = self.pool.get('account.voucher')
        old_voucher_ids = voucher_obj.search(cr, uid, [('move_id', '=', context['active_id'])], context=context)
        old_chk_log_ids = check_log_pool.search(cr,uid,[('name','in',old_voucher_ids),('status','=','active')], context=context)
        '''if chk_log_ids:
            check_log_pool.write(cr, uid, chk_log_ids, {'status':'delete','deleted':True},context=context)'''
        if old_chk_log_ids:
            raise osv.except_osv(_('Warning'), _('This move have already exchanged'))
        voucher_id = self.check_move_data(cr, uid, ids, context=context)
        if not voucher_id:
            raise osv.except_osv(_('Warning'), _('The account in credit lines must be of type liquidity'))
        if data.new_no and voucher_id:
            move = move_pool.browse(cr, uid, context['active_id'], context=context)
            journal_id=move and  move.journal_id
            if self._exchange_journal_seq(journal_id, context=context):
                chk_log_ids = check_log_pool.search(cr,uid,[('status','=','active')], context=context)
                sequence_pool.write(cr, uid, [journal_id.check_sequence.id], {'number_next_actual':data.new_no}, context=context)
                next_seq = sequence_pool.get_id(cr, uid, journal_id.check_sequence.id, context=context)
                lines = move_line_pool.search(cr, uid,[('move_id','=',context['active_id'])], context=context)
                line = move_line_pool.browse(cr, uid, lines, context=context)[0]
                check_log_pool.create(cr, uid,{'name': voucher_id, 'status': 'active', 'check_no': next_seq, 'journal_id':journal_id.id,'company_id':move.company_id.id},  context=context)
                #check_log_pool.create(cr, uid,{'partner_id':line.partner_id.id,'date_due':move.date,'status': 'active', 'check_no': next_seq, 'journal_id':journal_id.id,'company_id':move.company_id.id},  context=context)
                move_pool.write(cr, uid,[context['active_id']], {'ref' : next_seq or ' '}, context=context)
                move_line_pool.write(cr, uid,lines, {'ref' : next_seq or ' '}, context=context)
        return {'type':'ir.actions.act_window_close'}
    
    def check_move_data(self, cr, uid, ids, context=None):
        """ 
        This Method check some constraints before printing check from Journal Entry.
        1. Move state must be closed.
        @return: int ID of created voucher.
        """    
        move = self.pool.get('account.move').browse(cr, uid, context.get('active_id',[]), context=context)
        if move.state != 'closed':
            raise osv.except_osv(_('Warning'), _('Payment is not closed. Please Validate Payment First!'))
        return self.new_check(cr, uid, ids, context=context)

    def new_check(self, cr, uid, ids, context=None):
        """ 
        This Method create new voucher when printing check from journal entry.
        
        @return: int ID of created voucher
        """
        voucher_pool = self.pool.get('account.voucher')
        move = self.pool.get('account.move').browse(cr, uid, context.get('active_id',[]), context=context)
        cr.execute("SELECT COALESCE(sum(credit),0) amount,ml.partner_id,COALESCE(date_maturity,%s) date_maturity,ml.id id " \
                   "FROM account_move_line ml INNER JOIN account_move m ON m.id = ml.move_id " \
                   "INNER JOIN account_account acc ON acc.id = ml.account_id INNER JOIN account_account_type acc_type ON acc_type.id = acc.user_type " \
                   "WHERE m.id = %s AND ml.credit > 0 AND acc.type = 'liquidity' GROUP BY ml.partner_id,date_maturity,ml.id",(move.date,str(move.id),))
        suppliers = cr.dictfetchall()
        voucher_id = False
        for supplier in suppliers:
            voucher = {
                'account_id':move.journal_id.default_credit_account_id.id,
                'company_id':move.company_id.id,
                'period_id':move.period_id.id,
                'date':move.date,
                'amount':supplier['amount'],
                'journal_id':move.journal_id.id,
                'pay_journal_id':move.journal_id.id,
                'move_id':int(move.id),
                'ref': move.name,
                'partner_id':supplier['partner_id'],
                'amount_in_word':amount_to_text_ar(supplier['amount'], 'ar'),
                'type':'payment',
                'allow_check':1,
                'chk_status':True,
                'date_due':supplier['date_maturity']
            }
            voucher_id = voucher_pool.create(cr, uid, voucher, context=context)
            voucher_pool.write(cr, uid, voucher_id, {'state': 'posted'}, context=context)
            self.write(cr, uid, ids, {'payment_id':voucher_id}, context=context)
        return voucher_id

    def exchange_move_data(self, cr, uid, ids, context=None):
        """ 
        This Method exchange some constraints before printing exchange from Journal Entry.
        1. Move state must be posted.
        2. Move Journal must allow exchange writing.
        3. Cheque must pay from cash account.
        4. Move Lines must have partner_id (Beneficiary).
        5. Cheque must pay to only one partner.
        @return: int ID of created voucher.
        """    
        move_line_pool = self.pool.get('account.move.line')
        move = self.pool.get('account.move').browse(cr, uid, context.get('active_id',[]), context=context)
        move_line = move_line_pool.search(cr, uid, [('move_id','=',context.get('active_id',[]))], context=context)
        partners = move_line_pool.read(cr, uid, move_line, ['partner_id'], context=context)
        if len(set([part['partner_id'] for part in partners])) > 1:
            raise osv.except_osv(_('Warning'), _('Can not create new exchange for multiple partner!!'))
        return True

    def do_delete(self, cr, uid, ids, context=None):
        """ 
        This method for deleting exchange. 
        It delete the exchange_seq value in payment & make the exchange status in exchange log "delete"
        
        @return: dictionary, an action to close wizard
        """
        data = self.browse(cr, uid, ids, context=context)[0]
        voucher_pool = self.pool.get('account.voucher')
        move_pool = self.pool.get('account.move') 
        move_line_pool = self.pool.get('account.move.line')
        check_log_pool = self.pool.get('check.log')
        voucher = voucher_pool.browse(cr, uid, data.payment_id.id, context=context)
        next_seq =voucher.number
        chk_log_ids = check_log_pool.search(cr,uid,[('name','=',voucher.id),('status','=','active')], context=context)
        voucher_pool.write(cr, uid,[voucher.id],{'exchange_seq':'','date_due':(voucher.date_due or voucher.date)}, context=context)
        if chk_log_ids:
            check_log_pool.write(cr, uid, chk_log_ids, {'status':'delete','deleted':True},context=context)
        move_pool.write(cr, uid,[voucher.move_id.id], {'ref' : next_seq or ''}, context=context)
        lines = move_line_pool.search(cr, uid,[('move_id','=',voucher.move_id.id)], context=context)
        move_line_pool.write(cr, uid,lines, {'ref' : next_seq or ' '}, context=context)
        return {'type':'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
