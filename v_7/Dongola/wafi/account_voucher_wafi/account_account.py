# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.tools.translate import _
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.addons.account.account import account_account as acc

set_credit_debit = acc._set_credit_debit
#===============================================================================
# Voucher Canceling 
#===============================================================================
def cancel_vouchers(self, cr, uid, vals, context=None):
    """ 
    This method for cancel voucher and check exceeded waiting period.
    
    @return: list of cancelled  vouchers
    """
    voucher_pool = self.pool.get('account.voucher')
    move_pool = self.pool.get('account.move')
    period_pool = self.pool.get('account.period')
    journal_pool = self.pool.get('account.journal')
    log_pool = self.pool.get('check.log')
    sequence_pool = self.pool.get('ir.sequence')
    journal_id = vals.get('journal_id')
    company_id = vals.get('company_id')
    account_id = vals.get('account_id')
    date = vals.get('date') or \
        (vals.get('period_id') and period_pool.browse(cr, uid, vals.get('period_id'), context=context).date_stop) or \
        time.strftime('%Y-%m-%d')
    period_id = vals.get('period_id') or period_pool.find(cr,uid,date,
                context={'account_period_prefer_normal':True, 'company_id':company_id})[0]
    unreceive_voucher_ids = vals.get('unreceive_voucher_ids',[])
    unreconsiled_voucher_ids = vals.get('unreconsiled_voucher_ids',[])
    log_msg = vals.get('log_msg')
    msg = vals.get('narration')
    move_narration = vals.get('move_narration')
    all_voucher_ids = unreceive_voucher_ids+unreconsiled_voucher_ids
    if context is None:
        context = {}
    log_ids = log_pool.search(cr, uid, [('name','in',all_voucher_ids), ('status','=','active')], context=context)
    log_pool.write(cr, uid, log_ids, {'status': 'cancel'}, context=context) 
    if not journal_id:
        journal_id=journal_pool.search(cr, uid, [('company_id','=',company_id),('type', '=','purchase'),('special','=',True)], context=context)
    journal = journal_pool.browse(cr, uid, journal_id, context=context)
    period = period_pool.browse(cr, uid, period_id, context=context)
    voucher_pool.action_move_line_create(cr, uid, unreceive_voucher_ids, {'journal':journal, 'period':period, 
                                                                          'date':date, 'account':account_id}, context=context)
    voucher_pool.write(cr, uid, all_voucher_ids, {'state': 'cancel','narration': msg}, context=context) 
    for r in log_pool.read(cr, uid, log_ids,['check_no']):
        message = log_msg %(r['check_no'],)
        log_pool.log(cr, uid, r['id'], message)
    for r in voucher_pool.browse(cr, uid, all_voucher_ids,context=context):
        message = log_msg %(r.number,)
        voucher_pool.log(cr, uid, r.id, message)
        if r.id in unreconsiled_voucher_ids:
            move_id = move_pool.create(cr, uid, {
                                'name': sequence_pool.get_id(cr, uid, journal.sequence_id.id),
                                'journal_id': journal_id,
                                'narration':  move_narration%(r.number),
                                'date': date,
                                'ref': r.number,
                                'period_id': period_id,
                                'company_id': r.company_id.id,
                                'canceled_chk': True,
                                'line_id':[(0,0,{'name': _('Voucher %s Cancelling')%(r.number),
                                                'debit': r.amount > 0 and  r.amount or 0,
                                                'credit': r.amount < 0 and abs( r.amount) or 0,
                                                'account_id': r.account_id and r.account_id.id or r.pay_journal_id.default_debit_account_id.id,
                                                'journal_id': journal_id,
                                                'period_id': period_id,
                                                'partner_id': r.partner_id.id,
                                                'date': date or time.strftime('%Y-%m-%d'),
                                                'ref': r.number,}),
                                            (0,0,{'name': _('Voucher %s Canceling')%(r.number),
                                                'debit': r.amount < 0 and abs( r.amount) or 0,
                                                'credit': r.amount > 0 and r.amount or 0,
                                                'account_id': account_id,
                                                'journal_id': journal_id,
                                                'period_id': period_id,
                                                'partner_id': r.partner_id.id,
                                                'date': date or time.strftime('%Y-%m-%d'),
                                                'ref': r.number,})],
                            }, context=context)
            move_pool.post(cr, uid, [move_id], context=context)
    
    moves = [v.move_id.id for v in voucher_pool.browse(cr, uid, all_voucher_ids, context=context)]
    move_pool.write(cr, uid, moves, {'canceled_chk': True}, context=context)
    return all_voucher_ids

#----------------------------------------------------------
# Account Account (Inherit)
#----------------------------------------------------------
# class account_account(osv.Model):
# 
#     _inherit = "account.account"
# 
#     #FIXME: voucher type must be checked
#     #FIXME: debit & credit amount must be affected also
#     def __compute(self, cr, uid, ids, field_names, arg=None, context=None,
#                   query='', query_params=()):
#         """
#         Inherit __compute method to subtract payed voucher and waiting to receive amount from account balance
#         
#         @return: list of dictionary {account id: fields values}
#         """
#         res = super(account_account, self).__compute(cr, uid, ids, field_names, arg=arg, context=context, query=query, query_params=query_params)
#         for r in self.pool.get('account.voucher').read_group(cr, uid, [('state', '=', 'receive'), ('account_id', 'in', ids)], ['account_id', 'amount'], ['account_id'], context=context):
#             res.get(r['account_id'][0]).update({'balance':res[r['account_id'][0]]['balance'] - r['amount']})
#         return res
# 
#     _columns = {
#         'balance': fields.function(__compute, digits_compute=dp.get_precision('Account'), string='Balance', multi='balance'),
#         'credit': fields.function(__compute, fnct_inv=set_credit_debit, digits_compute=dp.get_precision('Account'), string='Credit', multi='balance'),
#         'debit': fields.function(__compute, fnct_inv=set_credit_debit, digits_compute=dp.get_precision('Account'), string='Debit', multi='balance'),
#     }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
