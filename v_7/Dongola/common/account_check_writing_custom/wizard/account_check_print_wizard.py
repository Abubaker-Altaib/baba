# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class account_check_print_wizard(osv.osv_memory):
    """
    Wizard to print payment check
    """
    _name = "account.check.print.wizard"

    def _check_journal_seq(self, journal_id, context=None):
        """
        Check if Journal check_seq defined or not.
        
        @return: boolean True if defined or raise an exception.
        """
        if not journal_id.check_sequence:
            raise osv.except_osv(_('Warning'),_('Please add "Check Sequence" for journal %s')%(journal_id.name))
        return True
        
    def _get_nxt_chk_name(self, cr, uid, context=None):
        """
        @return: char full next check number according to Journal's check_seq
        """
        sequence_pool = self.pool.get('ir.sequence')
        voucher = context['active_model'] == 'account.move' and self.pool.get('account.move').browse(cr, uid, context.get('active_id',[]), context=context) \
                  or self.pool.get('account.voucher').browse(cr, uid, context.get('active_id',[]), context=context)
        journal_id = voucher and (context['active_model'] == 'account.voucher' and voucher.pay_now!='pay_later' and voucher.pay_journal_id or voucher.journal_id)
        if self._check_journal_seq(journal_id, context=context): 
            seq = journal_id and sequence_pool.read(cr, uid, journal_id.check_sequence.id, ['number_next_actual', 'prefix', 'suffix', 'padding'],  context=context)
            d = sequence_pool._interpolation_dict()
            return seq and (seq['number_next_actual'] and (sequence_pool._interpolate(seq['prefix'],d) + '%%0%sd' % seq['padding'] % seq['number_next_actual'] + sequence_pool._interpolate(seq['suffix'],d)) \
                       or (sequence_pool._interpolate(seq['prefix'],d) + sequence_pool._interpolate(seq['suffix'],d)))

    def _get_nxt_chk_no(self, cr, uid, context=None):
        """
        @return: int next check number according to Journal's check_seq
        """
        sequence_pool = self.pool.get('ir.sequence')
        voucher = context['active_model'] == 'account.move' and self.pool.get('account.move').browse(cr, uid, context.get('active_id',[]), context=context) \
                  or self.pool.get('account.voucher').browse(cr, uid, context.get('active_id',[]), context=context)
        journal_id=voucher and (context['active_model'] == 'account.voucher' and voucher.pay_now!='pay_later' and voucher.pay_journal_id or voucher.journal_id)
        if self._check_journal_seq(journal_id, context=context):
            return voucher and sequence_pool.read(cr, uid, journal_id.check_sequence.id, ['number_next_actual'],  context=context)['number_next_actual']

    def _get_state(self, cr, uid, context=None):
        """ 
        @return: char default value of wizard state
        """
        voucher_pool = self.pool.get('account.voucher')
        ids = self._get_voucher_ids(cr, uid, context=context)
        voucher = voucher_pool.browse(cr, uid, ids, context=context)
        return voucher and ((voucher.move_id.state != 'posted' and not voucher.chk_seq and 'nothing') or 
                            (voucher.move_id.state != 'posted' and 'unpost') or (voucher.chk_seq and 'printed' or 'draft')) or 'draft'

    def _get_msg(self, cr, uid, context=None): 
        """
        @return: char default value of wizard displaying message
        """
        voucher_pool = self.pool.get('account.voucher')
        ids = self._get_voucher_ids(cr, uid, context=context)
        chk_no = ids and voucher_pool.browse(cr, uid, ids, context=context).chk_seq or False
        move = context['active_model'] == 'account.move' and \
            self.pool.get('account.move').browse(cr, uid, context.get('active_id',False) , context=context) or \
            voucher_pool.browse(cr, uid, ids, context=context).move_id
        return (move.state != 'posted' and _("Your payment's move is not posted!")) or (chk_no and _("This Payment has already been paid with check:%s")%(chk_no) or \
            _("Please verify this check number matches the starting preprinted number of the check in the printer! If not, enter new check number below."))
    
    def _get_voucher_ids(self,  cr, uid, context=None):
        """
        @return: int payment voucher id 
        """
        active_id = context.get('active_id',False) and context['active_model'] == 'account.voucher' and [context.get('active_id',False)] or \
               self.pool.get('account.voucher').search(cr, uid, [('move_id','=', context.get('active_id',False))], context=context)
        return  active_id and active_id[0] or []

    _columns =  {
        'name': fields.char("Next Check Number" , size=64, help='Next check number'),  
        'payment_id': fields.many2one('account.voucher', 'Payment'),
        'new_no': fields.integer('Update Check Number', help='Enter new check number here if you wish to update'),
        'nxt_chk_no': fields.char('Next Check Number', size=64, help='Next check number'),
        'new_chk_no': fields.integer('Update Check Number', help='Enter new check number here if you wish to update'),
        'status': fields.selection([('voided', 'Voided'), ('lost', 'Lost'), ('unk', 'Unknown')], 'Status'), 
        'msg': fields.text('Message', translate=True),
        'state': fields.selection([('draft', 'Draft'), ('printed', 'Printed'), ('reprint', 'Reprint'), ('reprint_new', 'Reprint'), 
                                   ('update', 'Update'),('unpost','Unposted Move'),('nothing','Do Nothing')], 'States'),
    }

    _defaults = {
           'new_no': _get_nxt_chk_no,
           'name': _get_nxt_chk_name,
           'state': _get_state,
           'payment_id': _get_voucher_ids,
           'msg': _get_msg,
    }

    def reprint_new(self,  cr, uid, ids, context=None):
        """
        Changing wizard state to "update" and modify displaying message.
        
        @return: boolean True
        """
        this = self.browse(cr, uid, ids)[0]
        voucher_id = self.read(cr, uid, ids, ['payment_id'], context=context)[0]['payment_id'][0]
        chk_no = self.pool.get('account.voucher').read(cr, uid, voucher_id, ['chk_seq'], context=context)['chk_seq']
        self.write(cr, uid, ids, {'state': 'reprint_new', 'msg': _("What happened to the existing check no %s")%(chk_no)}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.check.print.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
             }

    def reprint_new_next(self,  cr, uid, ids, context=None):
        """
        Changing wizard state to "reprint"
        
        @return: boolean True
        """
        this = self.browse(cr, uid, ids)[0]
        self.write(cr, uid, ids, {'state': 'reprint'}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.check.print.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
             }
        return  True

    def update_check_no(self,  cr, uid, ids, context=None):
        """
        Changing wizard state to "update" and modify displaying message.
        
        @return: boolean True
        """
        this = self.browse(cr, uid, ids)[0]
        self.write(cr, uid, ids, {'state': 'update', 'msg': _("Please verify this check number matches the starting preprinted number of the check in the printer! If not, enter new check number below.")}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.check.print.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
             }

    def check_payment(self, cr, uid, ids, context=None):
        """
        This method for creating new Check Payment or update the Check No.
        
        @return: dictionary, an action to close wizard
        """
        data = self.browse(cr, uid, ids, context=context)[0]
        check_log_pool = self.pool.get('check.log')
        sequence_pool = self.pool.get('ir.sequence')
        move_pool = self.pool.get('account.move') 
        voucher_pool = self.pool.get('account.voucher')
        move_line_pool = self.pool.get('account.move.line')
        voucher_id = (data.payment_id and data.payment_id.id) or (context['active_model'] == 'account.move' and self.check_move_data(cr, uid, ids, context=context))
        if data.new_no:
            voucher = voucher_pool.browse(cr, uid, voucher_id, context=context)
            journal_id=voucher and (voucher.pay_journal_id or voucher.journal_id)
            if self._check_journal_seq(journal_id, context=context):
                chk_log_ids = check_log_pool.search(cr,uid,[('name','=',voucher.id),('status','=','active')], context=context)
                if data.state == 'reprint':
                    check_log_pool.write(cr,uid,chk_log_ids, {'status': data.status}, context=context)
                sequence_pool.write(cr, uid, [journal_id.check_sequence.id], {'number_next_actual':data.new_no}, context=context)
                next_seq = sequence_pool.get_id(cr, uid, journal_id.check_sequence.id, context=context)
                voucher_pool.write(cr, uid,[voucher.id],{'amount_in_word': amount_to_text_ar(voucher.amount, 'ar'),'chk_seq': next_seq, 'chk_status':True, 'date_due': (voucher.date_due or voucher.date)},  context=context)
                if data.state == 'update':
                    check_log_pool.write(cr,uid,chk_log_ids, {'check_no': next_seq}, context=context)
                else: 
                    check_log_pool.create(cr, uid,{'name': voucher.id, 'status': 'active', 'check_no': next_seq, 'journal_id':journal_id.id},  context=context)
                move_pool.write(cr, uid,[voucher.move_id.id], {'ref' : next_seq or ' '}, context=context)
                lines = move_line_pool.search(cr, uid,[('move_id','=',voucher.move_id.id)], context=context)
                move_line_pool.write(cr, uid,lines, {'ref' : next_seq or ' '}, context=context)
        if data.state != 'update':
            return self.print_report(cr, uid, ids, context=context)
        return {'type':'ir.actions.act_window_close'}

    def check_move_data(self, cr, uid, ids, context=None):
        """ 
        This Method check some constraints before printing check from Journal Entry.
        1. Move state must be closed.
        2. Move Journal must allow check writing.
        3. Cheque must pay from cash account.
        4. Move Lines must have partner_id (Beneficiary).
        5. Cheque must pay to only one partner.
        @return: int ID of created voucher.
        """    
        move_line_pool = self.pool.get('account.move.line')
        move = self.pool.get('account.move').browse(cr, uid, context.get('active_id',[]), context=context)
        if move.state != 'closed':
            raise osv.except_osv(_('Warning'), _('Payment is not closed. Please Validate Payment First!'))
        if not move.journal_id.allow_check_writing:
            raise osv.except_osv(_('Warning'), _("Current journal doesn't allow check writing"))
        account_ids = self.pool.get('account.account').search(cr, uid, [('type','=','liquidity')], context=context)
        move_line = move_line_pool.search(cr, uid, [('move_id','=',context.get('active_id',[]))], context=context)
        credit_lines = move_line_pool.search(cr, uid, [('move_id','=',context.get('active_id',[])),('credit','>',0),('account_id','not in',account_ids)], context=context)
        if credit_lines == move_line:
            raise osv.except_osv(_('Warning'), _('Can not pay with check without cash account!!'))
        debit_lines = move_line_pool.search(cr, uid, [('move_id','=',context.get('active_id',[])),('debit','>',0),('partner_id','=',False)], context=context)
        if debit_lines:
            raise osv.except_osv(_('Warning'), _('Can not create new check without partner!!'))
        partners = move_line_pool.read(cr, uid, move_line, ['partner_id'], context=context)#[0]['partner_id']
        if len(set([part['partner_id'] for part in partners])) > 1:
            raise osv.except_osv(_('Warning'), _('Can not create new check for multiple partner!!'))
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
                   "INNER JOIN account_account acc ON acc.id = ml.account_id INNER JOIN account_account_type acc_type ON acc_type.id = user_type " \
                   "WHERE m.id = %s AND ml.credit > 0 AND type = 'liquidity' GROUP BY ml.partner_id,date_maturity,ml.id",(move.date,str(move.id),))
        suppliers = cr.dictfetchall()
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

    def do_delete(self, cr, uid, ids, context=None):
        """ 
        This method for deleting printed check. 
        It delete the chk_seq value in payment & make the check status in check log "delete"
        
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
        voucher_pool.write(cr, uid,[voucher.id],{'chk_seq':'','chk_status':True,'date_due':(voucher.date_due or voucher.date)}, context=context)
        if chk_log_ids:
            check_log_pool.write(cr, uid, chk_log_ids, {'status':'delete','deleted':True},context=context)
        move_pool.write(cr, uid,[voucher.move_id.id], {'ref' : next_seq or ''}, context=context)
        lines = move_line_pool.search(cr, uid,[('move_id','=',voucher.move_id.id)], context=context)
        move_line_pool.write(cr, uid,lines, {'ref' : next_seq or ' '}, context=context)
        return {'type':'ir.actions.act_window_close'}

    def print_report(self, cr, uid, ids, context=None):
        """
        @return: dictionary call report service to print it
        """
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.print.check', 'datas': {'ids':ids}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
