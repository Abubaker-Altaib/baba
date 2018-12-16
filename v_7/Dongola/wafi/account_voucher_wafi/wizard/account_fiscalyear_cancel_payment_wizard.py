# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
from account_voucher_wafi.account_account import cancel_vouchers as cancel_vouchers

class account_fiscalyear_cancel_payment_wizard(osv.osv_memory):

    _name = "account.fiscalyear.cancel.payment.wizard"

    _description = 'Cancel Payment'

    _columns = {
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True),
        'account_id': fields.related('journal_id', 'default_credit_account_id', type='many2one', relation='account.account', string='Deposit Account', readonly=True),
        'company_id': fields.related('journal_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True),
        'note': fields.text('Notes'),
        'period_id': fields.many2one('account.period', 'Extension Period', required=True),
    }

    def _get_fiscalyear(self, cr, uid, context=None):
        """
        @return: in id of fiscal year which want to cancel it's payments
        """
        return context.get('active_model', False) == 'account.fiscalyear' and context.get('active_id', False)

    def _get_period_id(self, cr, uid, context=None):
        """
        @return: int id of special open period in fiscal year which want to cancel it's payments
        """
        if context.get('active_model', False) == 'account.fiscalyear':
            period = self.pool.get('account.period').search(cr, uid,
                    [('fiscalyear_id', '=', context.get('active_id', False)),
                     ('state', '=', 'draft'), ('special', '=', True)], context=context)
            return period and period[0]

    _defaults = {
        'note': lambda self, cr, uid, context:_('Canceled Not Received Payment for:'),
        'fiscalyear_id': _get_fiscalyear,
        'period_id': _get_period_id
    }

    def open_voucher(self, cr, uid, ids, context=None):
        """
        Method that cancel unreceived & unreconsiled payment vouchers 
        when closing fiscal year and create amanat move
        
        @return: dictionary action that display all canceled vouchers
        """
        if context is None:
            context = {}
        form = self.read(cr, uid, ids, [])[0]

        journal_id = form['journal_id'][0]
        fiscalyear_id = form['fiscalyear_id'][0]
        period_id = form['period_id'][0]
        company_id = form['company_id'] and form['company_id'][0]
        account_id = form['account_id'] and form['account_id'][0]

        data_pool = self.pool.get('ir.model.data')
        voucher_pool = self.pool.get('account.voucher')
        journal_pool = self.pool.get('account.journal')
        res_company_pool = self.pool.get('res.company')
        self.pool.get('account.period').write(cr, uid, period_id,{'state': 'draft'}, context=context)
        if not company_id:
            company_id = res_company_pool.search(cr, uid, [], context=context)
        if company_id and not isinstance(company_id, list):
            company_id = [company_id]
        voucher_ids = []
        for company in company_id:
            journal_ids = journal_pool.search(cr, uid, [('type', 'in', ['bank', 'cash']), ('company_id', '=', company)], context=context)
            unreceive_voucher_ids = voucher_pool.search(cr, uid, [('company_id', '=', company), ('pay_journal_id', '=', journal_ids),
                                                        ('state', 'in', ['receive']), ('period_id.fiscalyear_id', '=', fiscalyear_id)], context=context)
            unreconsiled_voucher_ids = voucher_pool.search(cr, uid, [('company_id', '=', company), ('pay_journal_id', '=', journal_ids),
                                                        ('move_ids.statement_id', '=', False), ('period_id.fiscalyear_id', '=', fiscalyear_id),
                                                        ('state', 'in', ['posted', 'done'])], context=context)
            val = {'journal_id':journal_id,
                       'company_id':company_id,
                       'account_id':account_id,
                       'unreceive_voucher_ids':unreceive_voucher_ids,
                       'unreconsiled_voucher_ids':unreconsiled_voucher_ids,
                       'narration':_('Closing fiscal year!'),
                       'log_msg':_("The Payment '%s' has been cancelled because of closing fiscal year!"),
                       'move_narration':_("Deposit move from cancelled voucher '%s' because of closing fiscal year!"),
                       'period_id':period_id,
            }
            voucher_ids += cancel_vouchers(self, cr, uid, val, context=context)
        action = {}
        if voucher_pool.search(cr, uid, [('period_id.fiscalyear_id', '=', fiscalyear_id),('state', 'not in', ['done', 'cancel', 'reversed'])], context=context):
            raise orm.except_orm(_('Warning !'), _('Supplementary period couldn\'t close while there is pending entries, kindly complete their process first!'))
        self.pool.get('account.period').write(cr, uid, period_id, {'state':'done'}, context=context)
        self.pool.get('account.fiscalyear').write(cr, uid, fiscalyear_id, {'state':'close_ext_period'}, context=context)
        action_model, action_id = data_pool.get_object_reference(cr, uid, 'account_voucher', "action_purchase_receipt")
        self.pool.get('account.period').write(cr, uid, period_id,{'state': 'done'}, context=context)
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', [" + ','.join(map(str, voucher_ids)) + "])]"
        return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
