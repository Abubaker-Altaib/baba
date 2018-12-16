# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _
from account_voucher_wafi.account_account import cancel_vouchers as cancel_vouchers

class account_cancel_check(osv.osv_memory):
    
    _inherit = 'account.cancel.check'

    _columns = {
        'journal_ids': fields.many2many('account.journal', 'cancel_check_journal_rel', 'cancel_check_id', 'journal_id', 'Bank Accounts', 
                                        domain = [('type','in',['bank','cash'])]),
        'journal_id': fields.many2one('account.journal','Deposit Journal', domain = [('type', '=','purchase'),('special','=',True)], required=True),
        'account_id': fields.related('journal_id', 'default_credit_account_id', type='many2one', relation='account.account', string='Deposit Account', readonly=True),
        'company_id': fields.related('journal_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.cancel.check', context=c),
    } 

    def get_moves(self, cr, uid, ids, context=None):
        """
        Method that display all cancelled payment
        
        @return: dictionary action details
        """
        if context is None:
            context = {}
        form = self.read(cr, uid, ids, [])[0]
        
        journal_ids = form['journal_ids']
        journal_id = form['journal_id'] and form['journal_id'][0]
        company_id = form['company_id'] and form['company_id'][0]
        data_pool = self.pool.get('ir.model.data')
        voucher_ids = self.get_move(cr, uid, ids,journal_ids,journal_id,company_id, context=context)
        action = {}
        action_model,action_id = data_pool.get_object_reference(cr, uid, 'account_voucher', "action_purchase_receipt")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', ["+','.join(map(str,voucher_ids))+"])]"
        return action

    def get_move(self, cr, uid, ids=False,journal_ids=False,journal_id=False,company_id=False,account_id=False, context=None):
        """
        Method that cancel unreceived & unreconsiled payment vouchers 
        which exceed it's grace period and create amanat move
        
        @param journal_ids: list of payment journal ids which want to cancel their vouchers 
        @param journal_id: int amanat journal id
        @param company_id: int company id
        @param account_id: int amanat account
        @return: list of canceled voucher ids
        """
        if context is None:
            context = {}
        voucher_pool = self.pool.get('account.voucher')
        journal_pool = self.pool.get('account.journal')
        res_company_pool=self.pool.get('res.company')
        if not company_id:
            company_id=res_company_pool.search(cr, uid, [], context=context)
        if company_id and not isinstance(company_id,list): 
            company_id = [company_id]
        voucher_ids = []
        for company in company_id:
            if not journal_ids:
                journal_ids=journal_pool.search(cr, uid, [('type','in',['bank','cash']),('company_id','=',company)], context=context)
            for journal in journal_pool.browse(cr, uid, journal_ids):
                date= (datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d') + relativedelta(months=-journal.grace_period)).strftime('%Y-%m-%d')
                unreceive_voucher_ids = voucher_pool.search(cr, uid, [('company_id','=',company),('pay_journal_id','=',journal.id),
                                                            ('date','<=',date),('state','in',['receive']),('type','in',['purchase','payment'])], context=context)
                unreconsiled_voucher_ids = voucher_pool.search(cr, uid, [('company_id','=',company),('pay_journal_id','=',journal.id),
                                                            ('date','<=',date),('move_ids.statement_id','=',False), ('state','in',['posted','done']),
                                                            ('type','in',['purchase','payment'])], context=context)
                if not journal_id:
                    journal_id=journal_pool.search(cr, uid, [('company_id','=',company),('type', '=','purchase'),('special','=',True)], context=context)
                if not account_id:
                    account_id=journal_pool.browse(cr, uid, journal_id).default_credit_account_id.id
                val = {'journal_id':journal_id, 
                       'company_id':company_id,
                       'account_id':account_id,
                       'unreceive_voucher_ids':unreceive_voucher_ids,
                       'unreconsiled_voucher_ids':unreconsiled_voucher_ids,
                       'narration':_('Exceeded waiting period'),
                       'log_msg':_("The Payment '%s' exceeded waiting period and has been cancelled"),
                       'move_narration':_("Deposit move from cancelled voucher '%s' because of exceeding grace period!"),
                }
                voucher_ids += cancel_vouchers(self, cr, uid, val,context=context)
        return voucher_ids


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
