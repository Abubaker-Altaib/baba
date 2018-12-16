# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_fiscalyear_close(osv.osv_memory):
    """
    Closes Account Fiscalyear and Generate Closing entries for the selected Fiscalyear Profit & loss accounts
    """
    _name = "account.fiscalyear.pl.close"

    _description = "Fiscalyear Profit & loss Closing"

    _columns = {
       'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year to close', required=True, 
                                        help="Select a Fiscal year to close"),
       'account_id': fields.many2one('account.account', 'Profit & Loss Account', required=True),
       'journal_id': fields.many2one('account.journal', 'Closing Entries Journal', required=True, domain=[('type','=','situation')], 
                                     help='The best practice here is to use a journal dedicated to contain the closing entries of all fiscal years. Note that you should define it with type \'situation\'.'),
       'period_id': fields.many2one('account.period', 'Closing Entries Period', required=True, domain=[('special','=',True)]),
       'report_name': fields.char('Name of new entries',size=64, required=True, help="Give name of the new entries"),
       'company_id': fields.many2one('res.company', 'Company', type='many2one'),
    }

    def _get_fiscalyear(self, cr, uid, context=None):
        """ 
        Get fiscalyear_id
        
        @return: id of fiscal year
        """
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False

    _defaults = {
        'report_name': lambda self, cr, uid, context:_('Closing Profit and Loss'),
        'fiscalyear_id': _get_fiscalyear,
    }

    def onchange_fiscalyear_id(self, cr, uid, ids, fiscalyear_id=False, company_id=False, context=None):
        """
        Inherit method to update report_name values (Closing Profit and Loss) 

        @param fiscalyear_id: fiscalyear_id
        @param company_id: company_id
        @return: dictionary of values
        """
        FY = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=context)
        return {'value': {'company_id': FY and FY.company_id.id or False, 'account_id': False, 
                          'journal_id': False, 'period_id': False, 'report_name': _('Closing Profit and Loss')}}

    def data_save(self, cr, uid, ids, context=None):
        """
        This function close Profit & loss account of the selected fiscalyear by create entries in the closing period

        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscalyear close state’s IDs
        @return: dictionary of new form value
        """
        period_pool = self.pool.get('account.period')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        journal_pool = self.pool.get('account.journal')
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        account_pool = self.pool.get('account.account')
        currency_pool = self.pool.get('res.currency')
        data =  self.read(cr, uid, ids, context=context)[0]
        if context is None:
            context = {}
        fiscalyear = fiscalyear_pool.browse(cr, uid, data['fiscalyear_id'][0], context=context)
        journal = journal_pool.browse(cr, uid, data['journal_id'][0], context=context)
        period = period_pool.browse(cr, uid, data['period_id'][0], context=context)
        company_id = journal.company_id.id
        context.update({'company_id': company_id})
        #delete existing move and move lines if any
        move_ids = move_pool.search(cr, uid, [('journal_id', '=', journal.id), 
                                              ('period_id', '=', period.id)], context=context)
        if move_ids:
            move_pool.unlink(cr, uid, move_ids, context=context)
        query_line = move_line_pool._query_get(cr, uid,
                obj='account_move_line', context={'fiscalyear': fiscalyear.id})
        #create the closing move
        vals = {
            'name': '/',
            'ref': '',
            'period_id': period.id,
            'journal_id': journal.id,
            'date':period.date_stop,
        }
        move_id = move_pool.create(cr, uid, vals, context=context)
        account_ids = account_pool.search(cr, uid, [('user_type.close_method','=','pl'),
                                                    ('type','!=','view')], context=context)
        query_1st_part = """
                INSERT INTO account_move_line (
                     debit, credit, name, date, move_id, journal_id, period_id,
                     account_id, currency_id, amount_currency, company_id, state) VALUES 
        """
        query_2nd_part = ""
        query_2nd_part_args = []
        total_balance = 0.0
        for account in account_pool.browse(cr, uid, account_ids, context=context):
            account_balance =  self.pool.get('account.account').read(cr, uid, account.id, ['balance'], 
                                            context={'fiscalyear': fiscalyear.id, 'company_id': company_id})['balance']
            balance_in_currency = 0.0
            if account.currency_id:
                cr.execute('SELECT sum(amount_currency) as balance_in_currency FROM account_move_line ' \
                           'WHERE account_id = %s  AND ' + query_line + ' AND currency_id = %s', 
                           (account.id, account.currency_id.id)) 
                balance_in_currency = cr.dictfetchone()['balance_in_currency']
            company_currency_id = journal.company_id.currency_id
            if not currency_pool.is_zero(cr, uid, company_currency_id, abs(account_balance)):
                if query_2nd_part:
                    query_2nd_part += ','
                query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                query_2nd_part_args += (account_balance < 0 and -account_balance or 0.0,
                       account_balance > 0 and account_balance or 0.0,
                       data['report_name'],
                       period.date_start,
                       move_id,
                       journal.id,
                       period.id,
                       account.id,
                       account.currency_id and account.currency_id.id or None,
                       balance_in_currency,
                       account.company_id.id,
                       'draft')
                total_balance += account_balance
        if query_2nd_part:
            query_2nd_part += ",(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            query_2nd_part_args += (total_balance > 0 and total_balance or 0.0,
                       total_balance < 0 and -total_balance or 0.0,
                       data['report_name'],
                       period.date_start,
                       move_id,
                       journal.id,
                       period.id,
                       data['account_id'][0],
                       None,
                       None,
                       account.company_id.id,
                       'draft')
            cr.execute(query_1st_part + query_2nd_part, tuple(query_2nd_part_args))   
        return {
            'name':_("Journal Entry"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': '[]',
            'res_id': move_id,
            'context': context,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

