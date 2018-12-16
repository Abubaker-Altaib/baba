# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_curency_close(osv.osv_memory):
    """
    Wizard that calculate foreign currencies exchange
    """
    _name = "account.curency.close"
    
    _description = "Curency Closing"
        
    _columns = {
       'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year to Close', required=True, 
                                        help="Select a Fiscal year to close"),
       'account_id': fields.many2one('account.account', 'Exchange Differences Account', required=True),
       'journal_id': fields.many2one('account.journal', 'Closing Entries Journal', required=True, domain="[('type','=','situation')]", 
                                     help='The best practice here is to use a journal dedicated to contain the closing entries of all fiscal years. Note that you should define it with type \'situation\'.'),
       'period_id': fields.many2one('account.period', 'Closing Entries Period', required=True, domain="[('special','=',True)]",),
       'report_name': fields.char('Name of new entries',size=64, required=True, help="Give name of the new entries"),
       'company_id': fields.many2one('res.company', 'Company', type='many2one'),
    }

    _defaults = {
        'report_name': lambda self, cr, uid, context:_('Closing Currency'),
    }

    def onchange_fiscalyear_id(self, cr, uid, ids, fiscalyear_id=False, company_id=False, context=None):
        """
        Inherit method to update report_name values (Closing Currency) 

        @param fiscalyear_id: fiscalyear_id
        @param company_id: company_id
        @return: dictionary of values
        """
        FY = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=context)
        return {'value': {'company_id': FY and FY.company_id.id or False, 'account_id': False, 
                          'journal_id': False, 'period_id': False, 'report_name': _('Closing Currency')}}

    def data_save(self, cr, uid, ids, context=None):
        """
        This function close Profit & loss account of the selected fiscalyear by create entries in the closing period

        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscalyear close state’s IDs
        @return: dictionary of values
        """
        move_pool = self.pool.get('account.move')
        period_pool = self.pool.get('account.period')
        currency_pool = self.pool.get('res.currency')
        data =  self.read(cr, uid, ids, context=context)[0]
        account_id = data['account_id'][0]
        journal_id = data['journal_id'][0]
        period_id = data['period_id'][0]
        period = period_pool.browse(cr, uid, period_id, context=context)
        date = period.date_stop
        period_ids = period_pool.search(cr, uid, [('fiscalyear_id','=',data['fiscalyear_id'][0])], context=context)
        account_ids = self.pool.get('account.account').search(cr, uid, [('currency_id','!=',False)],context=context)
        vals = {
            'name': '/',
            'ref': '',
            'period_id': period_id,
            'journal_id': journal_id,
            'date': date,
        }
        move_id = move_pool.create(cr, uid, vals, context=context)
        query_1st_part = """
                INSERT INTO account_move_line ( debit, credit, name, date, 
                move_id, journal_id, period_id, account_id, currency_id, company_id, state) VALUES 
        """
        query_2nd_part = ""
        query_2nd_part_args = []
        cr.execute("SELECT account_id,currency_id,SUM(amount_currency) amount_currency,SUM(debit-credit) balance \
                    FROM account_move_line INNER JOIN account_move m ON m.id=move_id \
                    WHERE m.period_id IN %s AND currency_id IS NOT NULL AND account_id IN %s AND m.state='posted'\
                    GROUP BY account_id,currency_id",(tuple(period_ids),tuple(account_ids))) 
        context_multi_currency = context.copy()
        if date: 
            context_multi_currency.update({'date': date})
        total_currency_balance = 0
        result = cr.dictfetchall()
        for res in result:
            currency_balance = currency_pool.compute(cr, uid, res['currency_id'], period.company_id.currency_id.id, res['amount_currency'], context=context_multi_currency)
            if query_2nd_part:
                query_2nd_part += ','
            query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            query_2nd_part_args += (currency_balance-res['balance'] > 0 and currency_balance-res['balance'] or 0.0,
                   currency_balance-res['balance'] < 0 and abs(currency_balance-res['balance']) or 0.0,
                   data['report_name'],
                   date,
                   move_id,
                   journal_id,
                   period_id,
                   res['account_id'],
                   res['currency_id'],
                   data['company_id'][0],
                   'draft')
            total_currency_balance += currency_balance-res['balance']
        if query_2nd_part:
            query_2nd_part += ",(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            query_2nd_part_args += (total_currency_balance < 0 and -total_currency_balance or 0.0,
                       total_currency_balance > 0 and total_currency_balance or 0.0,
                       data['report_name'],
                       date,
                       move_id,
                       journal_id,
                       period_id,
                       account_id,
                       res['currency_id'],
                       data['company_id'][0],
                       'draft')
        if result:
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
