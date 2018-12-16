# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import netsvc

class res_company(osv.Model):
    """ inherit company model to add code field """
    _inherit = "res.company"

    _columns = {
        'auto_budget': fields.boolean('Automatic Budget Check'), 
    }
    _defaults = {
        'auto_budget': True,
    }

class account_voucher(osv.Model):

    _inherit = 'account.voucher'
    def _get_state(self, cr, uid, context=None):
       res = list(super(account_voucher, self)._columns['state'].selection)
       res.append(('no_approve','Budget Not Appoved'))
       return res
     
    _columns = {
       'state': fields.selection(selection=_get_state, string='Status', readonly=True, ),

    }

    def _check_analytic_account(self, cr, uid, ids, context=None):
        """
         Check state of voucher and user_type of account_id  
         Return Boolean
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.state != "draft" and voucher.type !='ratification':
                for voucher_line in voucher.line_ids:
                    if voucher.state != "draft" and voucher_line.account_id.user_type.analytic_required and not voucher_line.account_analytic_id and voucher_line.amount > 0.0:
                        return False
        return True

    def _total_amount_check(self, cr, uid, ids, context=None):
         for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.state not in ['draft','cancel','no_approve' ] and voucher.amount==0.0:
                return False
         return True

    _constraints = [
        (_check_analytic_account, _('Some accounts required to add analytic account for it!'), ['account_id','account_analytic_id','amount']),
        (_total_amount_check, "Operation is not completed, Total amount shouldn't be zero!", []), 
    ]

    def unlink(self, cr, uid, ids, context=None):
        """ After Deleting any account voucher must deletes all confirmations for it's lines """
        confirmation_ids = self.approved_line(cr, uid, ids, context=context)
        res = super(account_voucher, self).unlink(cr, uid, ids, context=context)
        if confirmation_ids:
            self.pool.get('account.budget.confirmation').unlink(cr, uid, confirmation_ids, context=context)
        return res
    
    def onchange_price(self, cr, uid, ids, line_ids, tax_id, partner_id=False, context=None):
        """
        Compute the amount from all voucher lines and return it in voucher amount.

        @param line_ids: list of voucher line ids
        @param tax_id: list of tax_ids for voucher
        @param partner_id: set partner_id =False as default
        @return: super of onchange_amount and it return total price of voucher line
        with tax_ids amount
        """
        line_pool = self.pool.get('account.voucher.line')
        line_ids = resolve_o2m_operations(cr, uid, line_pool, line_ids, ["amount","state"], context)
        approve_line_ids = [(0,0,l) for l in line_ids if l.get("state","complete") != "cancel"]
        return super(account_voucher,self).onchange_price(cr, uid, ids, approve_line_ids, tax_id, partner_id, context=context)
    
    def create_budget_confirmation(self, cr, uid, ids, context=None):
        """ 
        This Method for creating Budget Confirmation for each Voucher Line with analytic account

        @return: boolean True it any confirmation created, or return False
        """
        context = context or {}
        wf_service = netsvc.LocalService("workflow")
        confirmation_pool = self.pool.get('account.budget.confirmation')
        currency_pool = self.pool.get('res.currency')
        new_confirm_id = False
        flag = False
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.type  in ('purchase','sale'):  super(account_voucher,self).compute_tax(cr, uid, [voucher.id], context=context)
            if voucher.journal_id.type == 'purchase' or 'purchase' in context:
                
                for voucher_line in voucher.line_ids:
                    if voucher_line.account_id and voucher_line.account_id.user_type.analytic_wk:
                        company_currency = voucher.company_id.currency_id.id
                        current_currency = voucher.currency_id.id
                        context_multi_currency = context.copy()
                        context_multi_currency.update({'date': voucher.date})
                        total_amount = currency_pool.compute(cr, uid, current_currency, company_currency, voucher_line.total_amount, context=context_multi_currency)
                        amount = currency_pool.compute(cr, uid, current_currency, company_currency, voucher_line.amount, context=context_multi_currency)
                        val = {
                             'reference': voucher.number,
                             'partner_id': voucher.partner_id.id,
                             'period_id': voucher.period_id.id,
                             'general_account_id': voucher_line.account_id.id,
                             'date': voucher.date,
                             'analytic_account_id': voucher_line.account_analytic_id and voucher_line.account_analytic_id.id,
                             'amount': total_amount or amount,
                             'residual_amount': total_amount or amount,
                             'type':context.get('type','other'),
                             'note':voucher_line.name or '/',
                        }
                        new_confirm_id = False
                        if voucher_line.budget_confirm_id:
                            flag = True
                            confirmation_pool.write(cr, uid, [voucher_line.budget_confirm_id.id], val, context=context)
                            new_confirm_id = voucher_line.budget_confirm_id.id
                        elif not voucher_line.budget_confirm_id:
                            flag = True
                            confirm = confirmation_pool.create(cr, uid, val, context=context)
                            new_confirm_id = int(confirm)
                            self.pool.get('account.voucher.line').write(cr, uid, [voucher_line.id], {'budget_confirm_id':confirm}, context=context)
                        if new_confirm_id and not voucher.company_id.auto_budget:
                            confirmation_pool.action_cancel_draft(cr, uid, new_confirm_id, context=context)
                            wf_service.trg_validate(uid, 'account.budget.confirmation', new_confirm_id, 'complete', cr)
                            wf_service.trg_validate(uid, 'account.budget.confirmation', new_confirm_id, 'check', cr)
        return flag

    def approved_line(self, cr, uid, ids, context=None):
        """
        This method return all voucher lines that have a budget confirmation.

        @return: list of all budget_confirm_ids for voucher lines 
        """
        return [voucher_line.budget_confirm_id.id for voucher in self.browse(cr, uid, ids, context=context) for voucher_line in voucher.line_ids if voucher_line.budget_confirm_id]
    

    def cancel_voucher(self, cr, uid, ids, context=None):
        """
        Object Button function which canceling all  budget confirmation
        and change voucher state to "cancel"
        """
        wf_service = netsvc.LocalService("workflow")
        for confirmation_id in self.approved_line(cr, uid, ids, context=context):
            wf_service.trg_validate(uid, 'account.budget.confirmation', confirmation_id, 'cancel', cr)
        return super(account_voucher, self).cancel_voucher(cr, uid, ids, context=context)

    def confirmation_get(self, cr, uid, ids, context=None):
        """
        This method gets all budget confirmation ids of voucher.

        @return: list of budget confirmation id
        """
        res = []
        for voucher in self.browse(cr, uid, ids, context=context):
            for line in voucher.line_ids:
                if line.budget_confirm_id:
                    res.append(line.budget_confirm_id.id)
        return res

    def test_state(self, cr, uid, ids, mode, context=None):
        """
        Check voucher line and budget_confirmation state 
        and write state in voucher line (approved,not approved,cancelled)
        depend on budget confirmation for this line

        @param mode :tuple of flags
        @return: Boolean True or False
        """
        assert mode in ('finished', 'canceled'), _("invalid mode for test_state")
        finished = True
        canceled = False
        notcanceled = False
        write_approve_ids = []
        write_cancel_ids = []
        write_no_approve_ids = []
        ids = isinstance(ids, list) and ids[0] or ids
        voucher = self.browse(cr, uid, ids, context=context)
        #if voucher.type =='receipt': return True
        for line in voucher.line_ids:
            if (not line.budget_confirm_id) or (line.budget_confirm_id.state in ['valid','cancel']):
                if (not line.budget_confirm_id) or (line.budget_confirm_id.state == 'valid' and line.state != 'approve'):
                    write_approve_ids.append(line.id)
                elif line.budget_confirm_id.state == 'cancel' and line.state != 'cancel':
                    write_cancel_ids.append(line.id)
            else:
                finished = False
            if line.budget_confirm_id:
                if (line.budget_confirm_id.state == 'unvalid'):
                    if line.state != 'no_approve':
                        write_no_approve_ids.append(line.id)
                else:
                    notcanceled = True
            else:
                write_approve_ids.append(line.id)
        if write_approve_ids:
            self.pool.get('account.voucher.line').write(cr, uid, write_approve_ids, {'state': 'approve'}, context=context)
        if write_cancel_ids:
            self.pool.get('account.voucher.line').write(cr, uid, write_cancel_ids, {'state': 'cancel'},context=context)
        if write_no_approve_ids:
            self.pool.get('account.voucher.line').write(cr, uid, write_no_approve_ids, {'state': 'no_approve'}, context=context)
        res = self.onchange_price(cr, uid, [voucher.id], [(4,l.id) for l in voucher.line_ids], voucher.tax_id and [t.id for t in voucher.tax_id] or [], voucher.partner_id, context).get("value",{})
        #Can't call orm write because of the recursion
        cr.execute("UPDATE account_voucher  \
                    SET amount=%s, tax_amount=%s  WHERE id=%s ",
                    (res.get("amount"),res.get("tax_amount"), voucher.id))
        
        canceled=self.test_cancel(cr, uid, [voucher.id],write_cancel_ids, context=context)
        if mode == 'finished':
            return finished
        elif mode == 'canceled':
            return canceled
            if notcanceled:
                return False
            return canceled

    def test_cancel(self, cr, uid, ids,cancel_ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            for line in voucher.line_ids:
                if line.state != 'cancel' and line.id not in cancel_ids:
                    return False
        return True

class account_voucher_line(osv.Model):

    _inherit = 'account.voucher.line'

    def unlink(self, cr, uid, ids, context=None):
        """
        After Deleting Voucher Lines, it's confirmation must deleted
        @return: Deleting selected records
        """
        confirmation_ids = [voucher_line.budget_confirm_id.id for voucher_line in self.browse(cr, uid, ids, context=context) if voucher_line.budget_confirm_id]
        line = super(account_voucher_line, self).unlink(cr, uid, ids, context=context)
        if confirmation_ids:
            self.pool.get('account.budget.confirmation').unlink(cr, uid, confirmation_ids, context=context)
        return line

    _columns = {
        'name':fields.char('Description', size=256, required=True),
        'budget_confirm_id': fields.many2one('account.budget.confirmation', 'Confirmation', select=2, ondelete="restrict"),
        'state':fields.selection([('complete','Waiting for Approve'),('approve','Approved'),('no_approve','Budget Not Approved'),
                                  ('cancel','Canceled')], 'State', required=True, readonly=True),
        'total_amount': fields.float('Total Amount'),
    }

    _defaults = {
        'state': 'complete',
        'name': '/',
    }

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Inherit copy method for voucher line 
        @param default: dictionary of the values of record to be created,
        @return: super method of copy    
        """
        return super(account_voucher_line, self).copy(cr, uid, ids, default=default, context=context)

    def create(self, cr, uid, vals, context=None):
        """
        Inherited - create method to be sure that account and voucher company
        are the same.

        @return: list creating voucher lines
        """
        vals.update({'budget_confirm_id':False})
        if vals.get('account_id',False) and vals.get('voucher_id',False):
            account_company = self.pool.get('account.account').read(cr, uid, vals['account_id'], ['company_id'])['company_id'][0]
            voucher_company = self.pool.get('account.voucher').read(cr, uid, vals['voucher_id'], ['company_id'])['company_id'][0]
            if account_company != voucher_company:
                raise orm.except_orm(_('Entry Error!'), _('The account company is not like the voucher company!'))
        return super(account_voucher_line, self).create(cr, uid, vals, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
