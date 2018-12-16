# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class account_check_print_wizard(osv.osv_memory):

    _inherit = "account.check.print.wizard"

    def _get_state(self, cr, uid, context=None):
        """ 
        @return: char default value of wizard state.
        """
        ids = self._get_voucher_ids(cr, uid, context=context)
        voucher = self.pool.get('account.voucher').browse(cr, uid, ids, context=context)
        move = self.pool.get('account.move').browse(cr, uid, context.get('active_id',False) , context=context)
        return voucher and ((context['active_model'] == 'account.move' and voucher.move_id.state != 'posted' and not voucher.chk_seq and 'nothing') or 
                            (context['active_model'] == 'account.voucher' and voucher.state != 'receive' and 'unpost') or (voucher.chk_seq and 'printed' or 'draft')) or \
                (context['active_model'] == 'account.move' and move.state != 'posted' and 'unpost' or 'draft')

    def _get_msg(self, cr, uid, context=None): 
        """
        @return: char default value of wizard displaying message.
        """
        voucher_pool = self.pool.get('account.voucher')
        ids = self._get_voucher_ids(cr, uid, context=context)
        chk_no = ids and voucher_pool.browse(cr, uid, ids, context=context).chk_seq or False
        if context['active_model'] == 'account.move' and self.pool.get('account.move').browse(cr, uid, context.get('active_id',False) , context=context).state != 'posted':
            return _("Your payment's move is not posted!")
        elif context['active_model'] == 'account.voucher' and voucher_pool.browse(cr, uid, ids, context=context).state != 'receive':
            return _("Your payment's is not paid!")
        elif chk_no:
            return _("This Payment has already been paid with check:%s")%(chk_no)
        else:
            return _("Please verify this check number matches the starting preprinted number of the check in the printer! If not, enter new check number below.")

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

                sequence_pool.write(cr, uid, [journal_id.check_sequence.id], {'number_next':data.new_no}, context=context)
                next_seq = sequence_pool.get_id(cr, uid, journal_id.check_sequence.id, context=context)
                voucher_pool.write(cr, uid,[voucher.id],{'amount_in_word': amount_to_text_ar(voucher.amount, 'ar'),'chk_seq': next_seq, 'chk_status':True, 'date_due': (voucher.date_due or voucher.date)},  context=context)
                if data.state == 'update':
                    check_log_pool.write(cr,uid,chk_log_ids, {'check_no': next_seq}, context=context)
                else: 
                    check_log_pool.create(cr, uid,{'name': voucher.id, 'status': 'active', 'check_no': next_seq, 'journal_id':journal_id.id},  context=context)
                if data.state == 'reprint_new':
                    check_log_pool.write(cr,uid,chk_log_ids, {'status': data.status}, context=context)
                #if context['active_model'] == 'account.move':
                move_pool.write(cr, uid,[voucher.move_id.id], {'ref' : next_seq or ' '}, context=context)
                lines = move_line_pool.search(cr, uid,[('move_id','=',voucher.move_id.id)], context=context)
                move_line_pool.write(cr, uid,lines, {'ref' : next_seq or ' '}, context=context)
        if data.state != 'update':
            return self.print_report(cr, uid, ids, context=context)
        return {'type':'ir.actions.act_window_close'}  

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
        if voucher.move_id:
            move_pool.write(cr, uid,[voucher.move_id.id], {'ref' : next_seq or ''}, context=context)
            lines = move_line_pool.search(cr, uid,[('move_id','=',voucher.move_id.id)], context=context)
            move_line_pool.write(cr, uid,lines, {'ref' : next_seq or ' '}, context=context)
        return {'type':'ir.actions.act_window_close'}
    
    def print_report(self, cr, uid, ids, context=None):
        """
        @return: dictionary printing report action
        """
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.print.check', 'datas': {'ids':ids}}

    _defaults = {
           'state': _get_state,
           'msg': _get_msg,
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
