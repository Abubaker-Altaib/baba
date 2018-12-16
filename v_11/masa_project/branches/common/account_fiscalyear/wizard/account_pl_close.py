# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT



class account_fiscalyear_close(models.TransientModel):
    """
    Closes Account Fiscalyear and Generate Closing entries for the selected Fiscalyear Profit & loss accounts
    """
    _name = "account.fiscalyear.pl.close"
    _description = "Fiscalyear Profit & loss Closing"


    fiscalyear_id = fields.Many2one('account.fiscalyear', string='Fiscal Year to close', required=True, help="Select a Fiscal year to close")
    account_id = fields.Many2one('account.account', string='Profit & Loss Account', required=True)
    journal_id = fields.Many2one('account.journal', string='Closing Entries Journal', required=True)
    period_id = fields.Many2one('account.period', string='Closing Entries Period', required=True)
    report_name = fields.Char(string='Name of new entries',size=64, required=True, help="Give name of the new entries")
    company_id = fields.Many2one('res.company', 'Company')

    def data_save(self):
        """
        This function close Profit & loss account of the selected fiscalyear by create entries in the closing period

        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscalyear close state’s IDs
        @return: dictionary of new form value
        """


        period_pool = self.env['account.period']
        fiscalyear_pool = self.env['account.fiscalyear']
        journal_pool = self.env['account.journal']
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']

        account_pool = self.env['account.account']
        currency_pool = self.env['res.currency']
        data =  self.read()[0]

        fiscalyear = fiscalyear_pool.browse(data['fiscalyear_id'][0])
        journal = journal_pool.browse(data['journal_id'][0])
        period = period_pool.browse(data['period_id'][0])
        company_id = journal.company_id.id
        #context.update({'company_id': company_id})
        #delete existing move and move lines if any
        move_ids = move_pool.search([('journal_id', '=', journal.id), 
                                              ('period_id.fiscalyear_id', '=', fiscalyear.id)])
        if move_ids:
            move_ids.unlink()

        query_line = move_line_pool.with_context(fiscalyear=fiscalyear.id)._query_get()                                      
        #create the closing move
        vals = {
            'name': '/',
            'ref': '',
            'period_id': period.id,
            'journal_id': journal.id,
            'date':period.date_stop,
        }
        move_id = move_pool.create(vals)

        account_ids = account_pool.search([('user_type_id.close_year','=','profit_loss'),
                                                    ('user_type_id.type','!=','view')])
        account_balance_dic = {}
        query_1st_part = """
                INSERT INTO account_move_line (
                     debit, credit, name, date, date_maturity, move_id, journal_id, period_id,
                     account_id, currency_id, amount_currency, company_id) VALUES 
        """
        query_2nd_part = ""
        query_2nd_part_args = []
        total_balance = 0.0
        account_balance = 0.0

        for account in account_ids.ids:
            # Get account balances
            
            request = ("SELECT account_id AS id, (SUM(l.debit) - SUM(l.credit)) AS balance" +\
		           " FROM account_move_line l " +\
		           " LEFT JOIN account_account a ON (l.account_id=a.id)" +\
		           " LEFT JOIN account_move m ON (l.move_id=m.id)" +\
		           " WHERE l.account_id = %s AND l.date between %s and %s GROUP BY account_id")

            params = (account, fiscalyear.date_start, fiscalyear.date_stop,)
            self.env.cr.execute(request, params)
            account_dict = self.env.cr.dictfetchall() 
            account_obj = account_pool.browse(account)
            
            currency = account_obj.currency_id and account_obj.currency_id or account_obj.company_id.currency_id
            for row in account_dict:
                account_balance_dic = row
                account_balance = account_balance_dic.get('balance') or 0.0
                balance_in_currency = 0.0
                if account_obj.currency_id:
                    cr.execute('SELECT sum(amount_currency) as balance_in_currency FROM account_move_line ' \
                           'WHERE account_id = %s  AND ' + query_line + ' AND currency_id = %s', 
                           (account, account_obj.currency_id.id)) 
                    balance_in_currency = cr.dictfetchone()['balance_in_currency']
                company_currency_id = journal.company_id.currency_id.id

                if not currency.is_zero(company_currency_id) or not currency.is_zero(abs(account_balance)) :
                    if query_2nd_part:
                        query_2nd_part += ','
                    query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    query_2nd_part_args += (account_balance < 0 and -account_balance or 0.0,
                       account_balance > 0 and account_balance or 0.0,
                       data['report_name'],
                       period.date_start,
                       period.date_start,
                       move_id.id,
                       journal.id,
                       period.id,
                       account,
                       account_obj.currency_id and account_obj.currency_id.id or None,
                       balance_in_currency,
                       account_obj.company_id.id,
                       )
                    total_balance += account_balance
        if query_2nd_part:
            query_2nd_part += ",(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            query_2nd_part_args += (total_balance > 0 and total_balance or 0.0,
                       total_balance < 0 and -total_balance or 0.0,
                       data['report_name'],
                       period.date_start,
                       period.date_start,
                       move_id.id,
                       journal.id,
                       period.id,
                       data['account_id'][0],
                       None,
                       0.0,
                       account_obj.company_id.id,
                       )
            
            self.env.cr.execute(query_1st_part + query_2nd_part, tuple(query_2nd_part_args))
        total = 0.0 
        move_obj = move_pool.search([('id','=',move_id.id)]) 
        for line in move_obj.line_ids:
                total += line.debit
        move_obj_amount = total
        move_obj.write({'amount': move_obj_amount,})

        return {
            'name':_("Journal Entry"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': '[]',
            'res_id': move_id.id,

        }
