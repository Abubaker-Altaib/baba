# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import fields, osv

class account_common_report(osv.osv_memory):

    _inherit = "account.common.report"

    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        res = {}
        if filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False , 'date_to': False}
        if filter == 'filter_date':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': time.strftime('%Y-01-01'), 'date_to': time.strftime('%Y-%m-%d')}
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods = [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False}
        return res

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from', 'date_to', 'fiscalyear_id', 'journal_ids', 'period_from', 'period_to', 'filter', 'chart_account_id', 'target_move'])[0]
        if data['form']['period_from']:
            data['form'].update({
                'period_from':data['form']['period_from'][0], 
            })  
        if data['form']['period_to']:
            data['form'].update({
                'period_to':data['form']['period_to'][0], 
            })
        data['form'].update({
            'chart_account_id':data['form']['chart_account_id'] and data['form']['chart_account_id'][0], 
            'fiscalyear_id':data['form']['fiscalyear_id'] and data['form']['fiscalyear_id'][0], 
            })
      
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []  #####################
        data['form']['used_context'] = used_context
        return self._print_report(cr, uid, ids, data, context=context)

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False, context=None):
        res = {}
        if not fiscalyear:
            res['value'] = {'initial_balance': False}
        return res
     
    def _get_account(self, cr, uid, context=None):
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', company)], context=context, limit=1)
        return accounts and accounts[0] or False

    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now), ('company_id', '=', company)], context=context, limit=1)
        return fiscalyears and fiscalyears[0] or False

    def _get_all_journal(self, cr, uid, context=None):
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        return self.pool.get('account.journal').search(cr, uid , [('company_id', '=', company),('type','not in',['situation','profit_loss'])], context=context)

    _columns = {
        'journal_ids': fields.many2many('account.journal', string='Journals', required=True, domain=[('type','not in',['situation','profit_loss'])]), 
    }

    _defaults = {
            'fiscalyear_id':False , #_get_fiscalyear, 
            'journal_ids': _get_all_journal, 
            'chart_account_id': _get_account, 
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
