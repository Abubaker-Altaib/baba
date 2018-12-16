# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import netsvc
import time

#----------------------------------------------------------
# Account Voucher (Inherit)
#----------------------------------------------------------
class account_voucher(osv.Model):

    _inherit = 'account.voucher'

    def _get_voucher(self, cr, uid, ids, context=None):
        """
        @return: list of all voucher waiting to schedule
        """
        return self.pool.get('account.voucher').search(cr, uid, [('state', '=', 'schedule')], context=context)

    _columns = {
        'voucher_id': fields.many2one('account.voucher', 'Deposit Voucher',
                             domain=[('state', '=', 'cancel')], readonly=True, states={'draft':[('readonly', False)]}),
        'state':fields.selection([('draft', 'Draft'), ('close', 'Waiting for Department Manager Behest'),
                                  ('confirm', 'Waiting for Payment Confirm'), ('review', 'Waiting for Internal Auditor Review'),
                                  ('pay', 'Waiting for Payment Pay'),
                                  ('receive', 'Waiting for Payment Deliver'), ('posted', 'Waiting for Financial Controller post'),
                                  ('done', 'Done'), ('cancel', 'Cancel'), ('reversed', 'Reversed'),
                                  ('no_approve', 'Budget doesn\'t Approve')], 'Status', readonly=True, size=32, track_visibility='onchange'),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=False, states={'receive':[('readonly', True)], 'posted':[('readonly', True)], 'done':[('readonly', True)], 'cancel':[('readonly', True)], 'reversed':[('readonly', True)]}),
        'date':fields.date('Date', select=True, readonly=False, states={'receive':[('readonly', True)], 'posted':[('readonly', True)], 'done':[('readonly', True)], 'cancel':[('readonly', True)], 'reversed':[('readonly', True)]}, help="Effective date for accounting entries"),
    }


    def unlink(self, cr, uid, ids, context=None):
        """
        Inherit unlink method to prevent deleting not draft records
        
        @return: super unlink
        """
        if self.search(cr, uid, [('id', 'in', ids), ('state', '!=', 'draft')], context=context):
            raise osv.except_osv(_('Invalid Action!'), _('Cannot delete voucher(s) which are not in draft state.'))
        return super(account_voucher, self).unlink(cr, uid, ids, context=context)

    def action_cancel_voucher(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'cancel'
        @return: boolean True
        """
        context['reverse_move'] = True
        for voucher in self.browse(cr,uid,ids,context=context):
            if voucher.move_id:
                voucher.move_id.revert_move([voucher.journal_id.id],[voucher.period_id.id], voucher.date,context=context)
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def action_draft_voucher(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'draft', 
        delete old workflow instance and create new one 
        
        @return: boolean True
        """
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'account.voucher', id, cr)
            wf_service.trg_create(uid, 'account.voucher', id, cr)
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def review_voucher(self, cr, uid, ids, context=None):
        """
        Wokflow method prevent exceeding accounts ceiling, 
        also prevent feeding treasury when there is standing treasury feeding operation 
        
        @return: change state to 'review'
        """
        for v in self.browse(cr, uid, ids, context=context):
            if v.operation_type:
                if v.operation_type == 'supply_cash' and v.journal_balance < v.account_id.ceiling:
                    raise orm.except_orm(_('Entry Error!'), _('ceiling !'))
                for vl in v.line_ids:
                    if v.operation_type == 'treasury' and self.search(cr, uid, [('id', '!=', v.id),
                                            ('state', 'not in', ['posted', 'done', 'cancel', 'draft']),
                                            ('operation_type', '=', 'treasury'),
                                            ('line_ids.account_id', 'in', [vl.account_id.id])], context=context):
                        raise orm.except_orm(_('Entry Error!'), _('There are standing entries for treasury ‬!'))
                    if vl.account_id.ceiling > 0 and vl.account_balance + vl.amount > vl.account_id.ceiling:
                        raise orm.except_orm(_('Entry Error!'), _('ceiling!'))
        return self.write(cr, uid, ids, {'state': 'review'}, context=context)

    def open_voucher(self, cr, uid, ids, context=None):
        """
        Workflow method that recalculate amounts & change state to 'complete
        
        @return: boolean True
        """
        self.compute_tax(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state': 'complete'}, context=context)

    def receive_voucher(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'receive' and create journal entries.
        
        @return: boolean True
        """
        print "POOOOOOOOOOOOOOOOOOOOOOsteds"
        
        """for v in self.browse(cr, uid, ids, context=context):
            if v.account_id.type == 'liquidity' and v.account_id.balance < 0:
                raise orm.except_orm(_('Error!'), _('You Can\'t exceed existing balance!'))"""
        return self.write(cr, uid, ids, {'state': 'posted'}, context=context)

    def complete_close(self, cr, uid, ids, context=None):
        """
        Workflow function that check:
            * Account ceiling doesn't exceed
            * Voucher has lines
            * In case of special expense the voucher amount should equal the selected canceled one
        
        @return: change state to 'close'
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.operation_type:
                for v_line in voucher.line_dr_ids:
                    if v_line.amount != 0:
                        if v_line.account_id.ceiling != 0 :
                            if v_line.account_balance + v_line.amount > v_line.account_id.ceiling:
                                raise orm.except_orm(_('Entry Error!'), _('you can not exceed the account "Ceiling" amount !'))
            if not voucher.line_ids:
                raise orm.except_orm(_('Error!'), _('You cannot complete a expenses payment  without any bill information.'))
            if voucher.voucher_id and voucher.voucher_id.amount != voucher.amount:
                raise orm.except_orm(_('Error!'), _('Expense Amount must be equal to Deposit Amount'))
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)

    def pay_voucher(self, cr, uid, ids, context=None):
        """
        Workflow function that  make budget confirmation affect cash budget
        
        @return: change state to 'pay'
        
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.voucher_id :
                self.write(cr, uid, [voucher.voucher_id.id], {'active': False}, context=context)
            confirmation_ids = [line.budget_confirm_id.id for line in voucher.line_dr_ids if line.budget_confirm_id and line.state != 'cancel']
            print ">>>>>>>>>>>>>>>>>>>>,",confirmation_ids
            if confirmation_ids:
                self.pool.get('account.budget.confirmation').write(cr, uid, confirmation_ids, {'cash': True}, context=context)
        """
        return self.write(cr, uid, ids, {'state': 'pay'}, context=context)

    def action_cancel_line(self, cr, uid, ids, context=None):
        """
        Object Button function which canceling budget confirmation
        and change voucher line state to "cancel" and recalculate voucher amount
        
        @return: boolean True
        """
        wf_service = netsvc.LocalService("workflow")
        line_ids = []
        voucher = self.browse(cr, uid, ids, context=context)[0]
        for line in voucher.line_ids:
            if line.state == 'no_approve':
                wf_service.trg_validate(uid, 'account.budget.confirmation', line.budget_confirm_id.id, 'cancel', cr)
            elif line.state != 'cancel':
                line_ids.append((0, 0, {'amount':line.amount}))
        vals = self.onchange_price(cr, uid, ids, line_ids, voucher.tax_id, partner_id=voucher.partner_id.id, context=context)
        self.write(cr, uid, ids, vals.get('value', {}), context=context)
        return True

    '''def create(self, cr, uid, vals, context=None):
        """
        Inherit create method to prevent creating new revenue voucher when there is standing one waiting for auditor audit 
        
        @return: Create new record
        """
        date = vals.get('date', time.strftime('%Y-%m-%d'))
        if vals.get('type') == 'sale' and self.search(cr, uid, [('state', '=', 'review'), ('type', '=', 'sale'),('date', '<', date)], context=context):
            raise orm.except_orm(_('Error!'), _('Can not create new revenue record because some old records not reviewed yet!'))
        return super(account_voucher, self).create(cr, uid, vals, context=context)'''


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

