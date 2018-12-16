# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from openerp.tools.translate import _
from account_custom.common_report_header import common_report_header as common_header
from openerp import tools
from account.report.common_report_header import common_report_header as custom_common_header

class general_ledger(report_sxw.rml_parse, common_header, custom_common_header):
    
    _name = 'report.account.general.ledger'

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        obj_move = self.pool.get('account.move.line')
        self.sortby = data['form'].get('sortby', 'sort_date')
        context = data['form'].get('used_context', {})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=context)
        self.ctx2 = data['form'].get('used_context', {}).copy()
        self.ctx2.update({'initial_bal':  bool(data['form']['initial_balance'])})
        self.ctx2.update({'periods': []})
        self.move = data['form']['move']
        self.init_balance = data['form']['initial_balance']
        if self.init_balance:
            self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=self.ctx2)
        self.display_account = data['form']['display_account']
        self.target_move = data['form'].get('target_move', 'all')
        ctx = self.context.copy()       
        ctx['fiscalyear_id'] = data['form']['fiscalyear_id']
        if data['form']['filter'] == 'filter_period':
            ctx['period_from'] = data['form']['period_from']
            ctx['period_to'] = data['form']['period_to']
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form']['date_from']
            ctx['date_to'] = data['form']['date_to']
        ctx['state'] = data['form']['target_move']
        self.context.update(ctx)
        if (data['model'] == 'ir.ui.menu'):
            new_ids = [data['form']['chart_account_id']]
            if data['form']['account_ids']:
               self.account_query =  " AND l.account_id in (%s) " %(",".join([str(x) for x in data['form']['account_ids']]))
               new_ids =data['form']['account_ids']
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        self.state_query = ""
        if self.target_move == 'posted':
            self.state_query = " AND m.state = 'posted' "
        if  data['form']['analytic_account_ids'] :
            self.analytic_ids =  self._get_children_and_consol(self.cr, self.uid, data['form']['analytic_account_ids'], 'account.analytic.account')
            self.query +=  " and analytic_account_id in (%s) "  % (",".join([str(x) for x in self.analytic_ids])) 
            self.account_query +=  " and analytic_account_id in (%s) "  % (",".join([str(x) for x in self.analytic_ids])) 
            self.init_query  +=  " and analytic_account_id in (%s) "  % (",".join([str(x) for x in self.analytic_ids])) 
        return super(general_ledger, self).set_context(objects, data, new_ids, report_type=report_type)

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(general_ledger, self).__init__(cr, uid, name, context=context)
        self.cr = cr
        self.uid = uid
        self.query = ""
        self.init_query =""
        self.account_query =  " "
        self.tot_currency = 0.0
        self.period_sql = ""
        self.sold_accounts = {}
        self.sortby = 'sort_date'
        self.acc_ids = []
        self.read_data = []
        self.account_ids= []
        self.analytic_ids = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'lines_consil': self.lines_consil,
            'sum_debit_account': self._sum_debit_account,
            'sum_credit_account': self._sum_credit_account,
            'sum_balance_account': self._sum_balance_account,
            'sum_currency_amount_account': self._sum_currency_amount_account,
            'get_children_accounts': self.get_children_accounts,
            'get_fiscalyear': self.get_fiscalyear_br,
            'get_journal': self._get_journal,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period_br,
            'get_end_period': self.get_end_period_br,
            'get_filter': self._get_filter,
            'get_filter_Trans': self._get_filter_Trans,
            'get_sortby_gl': self._get_sortby_gl,
            'get_start_date':self._get_date_from,
            'get_end_date':self._get_date_to,
            'get_target_move': self._get_target_move,
            'get_Translation': self._get_Translation,
            'get_display_account': self._get_display_account,
            'get_label_according_model': self._get_label_according_model,
            'get_multi_company': self._get_multi_company,
            'analytic_lines': self._analytic_lines,
            'get_objects': self.get_objects,
            'lines_g': self._lines_g,
            'total': self._total,
        })
        self.context = context

    def _sum_currency_amount_account(self, account):
        self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                FROM account_move_line l \
                WHERE l.account_id = %s AND %s' % (account.id, self.query))
        sum_currency = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                            FROM account_move_line l \
                            WHERE l.account_id = %s AND %s ' % (account.id, self.init_query))
            sum_currency += self.cr.fetchone()[0] or 0.0
        return sum_currency

# stope it and replace with orignal account blew   def get_children_accounts(self, account):
#        res = []
#        ids_acc = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
#        for child_account in self.pool.get('account.account').browse(self.cr, self.uid, [ids_acc][0], context=self.context):            
#            sql = """
#                SELECT count(id)
#                FROM account_move_line AS l
#                WHERE %s AND l.account_id = %%s
#            """ % (self.query)
#            self.cr.execute(sql, (child_account.id,))
#            num_entry = self.cr.fetchone()[0] or 0           
#            sold_account = self._sum_balance_account(child_account)
#            self.sold_accounts[child_account.id] = sold_account
#            if self.display_account == 'bal_movement':
#                if child_account.type != 'view' and num_entry != 0:
#                    res.append(child_account)
#            elif self.display_account == 'bal_solde':
#                if child_account.type != 'view' and num_entry != 0:
#                    if (sold_account != 0.0):
#                        res.append(child_account)
#            else:
#                res.append(child_account)      
#        if not res:           
#            return [account]
#        return res

    def get_children_accounts(self, account):
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        res = []
        currency_obj = self.pool.get('res.currency')
        ids_acc = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
        currency = account.currency_id and account.currency_id or account.company_id.currency_id
        for child_account in self.pool.get('account.account').browse(self.cr, self.uid, ids_acc, context=self.context):
            sql = """
                SELECT count(id)
                FROM account_move_line AS l
                WHERE %s AND l.account_id = %%s
            """ % (self.query)
            self.cr.execute(sql, (child_account.id,))
            num_entry = self.cr.fetchone()[0] or 0
            sold_account = self._sum_balance_account(child_account)
            self.sold_accounts[child_account.id] = sold_account
            if self.display_account == 'movement':
                if child_account.type != 'view' and num_entry != 0:
                    res.append(child_account)
            elif self.display_account == 'not_zero':
                if child_account.type != 'view' and num_entry != 0:
                    if not currency_obj.is_zero(self.cr, self.uid, currency, sold_account):
                        res.append(child_account)
            else:
                res.append(child_account)
        if not res:
            return [account]
        return res
    def lines(self, account):
        res = {}
        """ Return all the account_move_line of account with their account code counterparts """
        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted', '']
        # First compute all counterpart strings for every move_id where this account appear.
        # Currently, the counterpart info is used only in landscape mode
        self.cr.execute("   SELECT m1.move_id, \
                            array_to_string(ARRAY(SELECT DISTINCT a.code \
                                          FROM account_move_line m2 \
                                          LEFT JOIN account_account a ON (m2.account_id=a.id) \
                                          WHERE m2.move_id = m1.move_id \
                                          AND m2.account_id<>%s), ', ') AS counterpart \
                FROM (SELECT move_id \
                        FROM account_move_line l \
                        LEFT JOIN account_move m ON (m.id = l.move_id) \
                        WHERE " + self.query + " " + self.state_query + "  AND l.account_id = %s GROUP BY move_id) m1 ", (account.id, account.id))
        counterpart_res = self.cr.dictfetchall()
        counterpart_accounts = {}
        for i in counterpart_res:
            counterpart_accounts[i['move_id']] = i['counterpart']
        del counterpart_res

        # Then select all account_move_line of this account
        if self.sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'
        elif self.sortby == 'dc':
            sql_sort = 'l.credit, l.move_id'
        else:
            sql_sort = 'l.date, l.move_id'

        self.cr.execute("SELECT l.id AS lid, l.date AS ldate, j.code AS lcode, l.currency_id,l.amount_currency,l.ref AS lref, \
                            l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, l.period_id AS lperiod_id, \
                            l.partner_id AS lpartner_id, m.name AS move_name, m.id AS mmove_id,per.code as period_code, c.symbol AS currency_code, \
                            i.id AS invoice_id, i.type AS invoice_type, i.number AS invoice_number, p.name AS partner_name \
                        FROM account_move_line l \
                            JOIN account_move m on (l.move_id=m.id) \
                            LEFT JOIN res_currency c on (l.currency_id=c.id) \
                            LEFT JOIN res_partner p on (l.partner_id=p.id) \
                            LEFT JOIN account_invoice i on (m.id =i.move_id) \
                            LEFT JOIN account_period per on (per.id=l.period_id) \
                            JOIN account_journal j on (l.journal_id=j.id) \
                        WHERE " + self.query + " " + self.state_query + " AND l.account_id = %s ORDER by " + sql_sort, (account.id,))

        res_lines = self.cr.dictfetchall()
        res_init = []
        ############if res_lines and self.init_balance:
        if self.init_balance:
            # FIXME: replace the label of lname with a string translatable
            self.cr.execute("   SELECT 0 AS lid, '' AS ldate, '' AS lcode, COALESCE(SUM(l.amount_currency),0.0) AS amount_currency, \
                                '' AS lref, 'الرصيد الإفتتاحي' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, \
                                    '' AS lperiod_id, '' AS lpartner_id, '' AS move_name, '' AS mmove_id, '' AS period_code, '' AS currency_code, \
                                    NULL AS currency_id, '' AS invoice_id, '' AS invoice_type, '' AS invoice_number, '' AS partner_name \
                                FROM account_move_line l \
                                    LEFT JOIN account_move m on (l.move_id=m.id) \
                                    LEFT JOIN res_currency c on (l.currency_id=c.id) \
                                    LEFT JOIN res_partner p on (l.partner_id=p.id) \
                                    LEFT JOIN account_invoice i on (m.id =i.move_id) \
                                    JOIN account_journal j on (l.journal_id=j.id) \
                                WHERE ".decode('utf-8') + self.init_query + " " + self.state_query + " AND l.account_id = %s", (account.id,))
            res_init = self.cr.dictfetchall()
            cred = res_init[0]['credit']
            deb = res_init[0]['debit']
            res = res_init + res_lines
        else:
            res = res_lines
        account_sum = 0.0
        for l in res:
            l['move'] = l['move_name'] != '/' and l['move_name'] or ('*' + str(l['mmove_id']))
            l['partner'] = l['partner_name'] or ''
            account_sum += l['debit'] - l['credit']
            l['progress'] = account_sum
            l['line_corresp'] = l['mmove_id'] == '' and ' ' or counterpart_accounts[l['mmove_id']]  # .replace(', ',',')
            # Modification of amount Currency
            if l['credit'] > 0:
                if l['amount_currency'] != None:
                    l['amount_currency'] = abs(l['amount_currency']) * -1
            if l['amount_currency'] != None:
                self.tot_currency = self.tot_currency + l['amount_currency']
        return res  #----------------- Lines() END

#--------------------------------------Sum_Debit--------------------
    def _sum_debit_account(self, account):
        if account.type == 'view':
            sum_debit = account.debit
        else:
            move_state = ['draft', 'posted', 'completed']
            if self.target_move == 'posted':
                move_state = ['posted', '']
            self.cr.execute('SELECT sum(debit) \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id = %s) ' + self.state_query + ' \
                    AND ' + self.query + ' '
                    , (account.id,))
            sum_debit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            childs = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
            self.cr.execute('SELECT sum(debit) \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id IN %s) ' + self.state_query + '\
                    AND ' + self.init_query + ' '
                    , (tuple(childs),))
            # Add initial balance to the result
            sum_debit += self.cr.fetchone()[0] or 0.0
        return sum_debit

#--------------------------------------Sum_Credit--------------------
    def _sum_credit_account(self, account):
        if account.type == 'view':
            sum_credit = account.credit
        else:
            move_state = ['draft', 'posted', 'completed']
            if self.target_move == 'posted':
                move_state = ['posted', '']
            self.cr.execute('SELECT sum(credit) \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id = %s) ' + self.state_query + ' \
                    AND ' + self.query + ' '
                    , (account.id,))
            sum_credit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            childs = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
            self.cr.execute('SELECT sum(credit) \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id IN %s) ' + self.state_query + ' \
                    AND ' + self.init_query + ' '
                    , (tuple(childs),))
            # Add initial balance to the result
            sum_credit += self.cr.fetchone()[0] or 0.0
        return sum_credit

#--------------------------------------Sum_Balance--------------------
    def _sum_balance_account(self, account):
        if account.type == 'view':
            sum_balance = account.balance
        else:
            move_state = ['draft', 'posted', 'completed']
            if self.target_move == 'posted':
                move_state = ['posted', '']
            self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id = %s) ' + self.state_query + ' \
                    AND ' + self.query + ' '
                    , (account.id,))
            sum_balance = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            childs = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
            self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id IN %s) ' + self.state_query + ' \
                    AND ' + self.init_query + ' '
                    , (tuple(childs),))
            # Add initial balance to the result
            sum_balance += self.cr.fetchone()[0] or 0.0
        return sum_balance

    def _get_account(self, data):
        if data['model'] == 'account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, [data['form']['id']]).company_id.name
        return super(general_ledger , self)._get_account(data)

    def _analytic_lines(self, account_id, analytic_id):
        account_analytic_obj = self.pool.get('account.analytic.account')
        ids = account_analytic_obj.search(self.cr, self.uid, [('parent_id', 'child_of', [analytic_id]),('id', '=',analytic_id)])
        ids.append(0)
        self.cr.execute("SELECT m.name as move,l.date as date, aa.name AS name, aa.code AS code, \
                            l.debit AS debit, l.credit AS credit \
                        FROM account_move_line AS l \
                        LEFT JOIN account_move m on (l.move_id=m.id) \
                        LEFT JOIN  account_account AS aa on(l.account_id=aa.id) \
                        WHERE " + self.query + self.state_query + self.account_query + " and l.account_id=%s and  analytic_account_id in %s " %(account_id,tuple(ids)))

        res = self.cr.dictfetchall()
        return res

    def get_children(self, ids):
        self.cr.execute("SELECT aa.id AS id, aa.name AS name, aa.code AS code, MIN(c.name) AS company, \
                            COALESCE(sum(l.debit),0.0) AS debit, COALESCE(sum(l.credit),0.0) AS credit \
                        FROM account_move_line AS l \
                                LEFT JOIN account_move m on (l.move_id=m.id) \
                                INNER JOIN account_analytic_account AS aa \
                                ON l.analytic_account_id=aa.id INNER JOIN res_company c \
                                ON c.id = aa.company_id \
                        WHERE " + self.query + self.state_query  + self.account_query + " \
                        GROUP BY aa.id, aa.name, aa.code, aa.company_id \
                        ORDER BY aa.company_id,aa.code")
        read_data = self.cr.dictfetchall()
        for data in read_data:
            if (data['id'] not in self.acc_ids):
                inculde_empty = True
                if (not self.empty_acc) and data['debit'] - data['credit'] == 0.00:
                    inculde_empty = False
                if inculde_empty:
                    self.acc_ids.append(data['id'])
                    self.read_data.append(data)
        return True

    def get_objects(self, empty_acc):
        if self.read_data:
            return self.read_data
        self.empty_acc = empty_acc
        self.read_data = []
        self.get_children(self.ids)  
        self.total_res = []
        self.cr.execute("SELECT COALESCE(sum(l.debit),0.0) AS debit, COALESCE(sum(l.credit),0.0) AS credit \
                        FROM account_move_line AS l \
                        LEFT JOIN account_analytic_account AS aa  on (l.analytic_account_id=aa.id) \
                        LEFT JOIN account_move m on (l.move_id=m.id) \
                        WHERE  " + self.query + self.state_query  + self.account_query + "   ")
        self.total_res = self.cr.dictfetchall()
        return self.read_data

    def _lines_g(self, account_id):
        account_analytic_obj = self.pool.get('account.analytic.account')
        ids = account_analytic_obj.search(self.cr, self.uid, [('parent_id', 'child_of', [account_id])])
        self.cr.execute("SELECT l.account_id as account_id,analytic_account_id as id,aa.name AS name, aa.code AS code, \
                            COALESCE(sum(l.debit),0.0) AS debit, COALESCE(sum(l.credit),0.0) AS credit \
                        FROM account_move_line AS l \
                        LEFT JOIN account_move m on (l.move_id=m.id) \
                        LEFT JOIN  account_account AS aa on(l.account_id=aa.id) \
                        WHERE " + self.query + self.state_query + self.account_query +" and l.analytic_account_id=%s " \
                        "GROUP BY l.account_id, aa.name, aa.code,analytic_account_id " % (account_id,))
        res = self.cr.dictfetchall()
        return res

    def _total(self):
        return self.total_res

    def lines_consil(self, account):
        res = {}
        """ Return all the account_move_line of account with their account code counterparts """
        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted', '']
        # First compute all counterpart strings for every move_id where this account appear.
        # Currently, the counterpart info is used only in landscape mode
        self.cr.execute("   SELECT m1.move_id, \
                            array_to_string(ARRAY(SELECT DISTINCT a.code \
                                          FROM account_move_line m2 \
                                          LEFT JOIN account_account a ON (m2.account_id=a.id) \
                                          WHERE m2.move_id = m1.move_id \
                                          AND m2.account_id<>%s), ', ') AS counterpart \
                FROM (SELECT move_id \
                        FROM account_move_line l \
                        LEFT JOIN account_move m ON (m.id = l.move_id) \
                        WHERE " + self.query + " " + self.state_query + "  AND l.account_id = %s GROUP BY move_id) m1 ", (account.id, account.id))
        counterpart_res = self.cr.dictfetchall()
        counterpart_accounts = {}
        for i in counterpart_res:
            counterpart_accounts[i['move_id']] = i['counterpart']
        del counterpart_res

        # Then select all account_move_line of this account
        if self.sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'
        elif self.sortby == 'dc':
            sql_sort = 'l.credit, l.move_id'
        else:
            sql_sort = 'l.date, l.move_id'

        ############################################
        query = ("create or replace view account_general_ledger as (SELECT l.move_id,l.account_id,l.id AS lid, l.date AS ldate, j.code AS lcode, l.currency_id,l.amount_currency,l.ref AS lref, \
                            l.name AS lname, COALESCE(l.debit,0) AS pre_debit, COALESCE(l.credit,0) AS pre_credit, l.period_id AS lperiod_id, \
                            l.partner_id AS lpartner_id, m.name AS move_name, m.id AS mmove_id,per.code as period_code, c.symbol AS currency_code, \
                            i.id AS invoice_id, i.type AS invoice_type, i.number AS invoice_number, p.name AS partner_name \
                        FROM account_move_line l \
                            JOIN account_move m on (l.move_id=m.id) \
                            LEFT JOIN res_currency c on (l.currency_id=c.id) \
                            LEFT JOIN res_partner p on (l.partner_id=p.id) \
                            LEFT JOIN account_invoice i on (m.id =i.move_id) \
                            LEFT JOIN account_period per on (per.id=l.period_id) \
                            JOIN account_journal j on (l.journal_id=j.id) \
                        WHERE " + self.query + " " + self.state_query + " AND l.account_id = %s " + ")")

        tools.drop_view_if_exists(self.cr, 'account_general_ledger')
        self.cr.execute(query, (account.id,))
        if self.move:
          select = " concat( line_view.name , substring(aggr_textcat('\n ' ||  description ) from 2)) " 
        else:
          select = "line_view.name "
        self.cr.execute('''select  ''' + select + ''' as name, COALESCE(sum(line_view.debit),0)  as debit, COALESCE(sum(line_view.credit),0) as credit  
                            from account_general_ledger l 
                            left join 
                                (select  min(l1.lid) as lid, 
                                min(acc.name) as name, 
				substring(aggr_textcat('\n ' || p.name||'(' || l2.credit-l2.debit || ')'  ) from 2)  as description ,
                                min(l2.account_id) as v_account2,
                                COALESCE(sum(l2.debit),0) as credit, COALESCE(sum(l2.credit),0) as debit 
                                from account_general_ledger l1 
                                inner join account_move_line l2 on (l1.move_id=l2.move_id and l1.lid!=l2.id and l1.account_id!=l2.account_id ) 
                                left join account_account acc on (acc.id = l2.account_id)    
                                LEFT JOIN res_partner p on (l2.partner_id=p.id) 
                                group by  lid, l2.account_id  ) as line_view 
                        on(l.lid=line_view.lid)  
                         group by v_account2,line_view.name ORDER by v_account2, credit, debit desc''')
        res_lines = self.cr.dictfetchall()
        res_init = []
        ############if res_lines and self.init_balance:
        if self.init_balance:
            # FIXME: replace the label of lname with a string translatable
            self.cr.execute("   SELECT 0 AS lid, '' AS ldate, '' AS lcode, COALESCE(SUM(l.amount_currency),0.0) AS amount_currency, \
                                '' AS lref, 'الرصيد الإفتتاحي' AS name, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, \
                                    '' AS lperiod_id, '' AS lpartner_id, '' AS move_name, '' AS mmove_id, '' AS period_code, '' AS currency_code, \
                                    NULL AS currency_id, '' AS invoice_id, '' AS invoice_type, '' AS invoice_number, '' AS partner_name \
                                FROM account_move_line l \
                                    LEFT JOIN account_move m on (l.move_id=m.id) \
                                    LEFT JOIN res_currency c on (l.currency_id=c.id) \
                                    LEFT JOIN res_partner p on (l.partner_id=p.id) \
                                    LEFT JOIN account_invoice i on (m.id =i.move_id) \
                                    JOIN account_journal j on (l.journal_id=j.id) \
                                WHERE ".decode('utf-8') + self.init_query + " " + self.state_query + " AND l.account_id = %s", (account.id,))
            res_init = self.cr.dictfetchall()
            cred = res_init[0]['credit']
            deb = res_init[0]['debit']
            res = res_init + res_lines
        else:
            res = res_lines
        account_sum = 0.0
        for l in res:
            account_sum += l['debit'] - l['credit']
            l['progress'] = account_sum
        return res  #----------------- Lines() END





report_sxw.report_sxw('report.account.general.ledger.analytic', 'account.analytic.account', 'addons/account_arabic_reports/report/account_general_ledger_analytic.rml',
        parser=general_ledger, header="internal landscape")

report_sxw.report_sxw('report.account.general.ledger.arabic', 'account.account', 'addons/account_arabic_reports/report/account_general_ledger.rml', parser=general_ledger, header=False)

report_sxw.report_sxw('report.account.general.ledger_landscape.arabic', 'account.account', 'addons/account_arabic_reports/report/account_general_ledger_landscape.rml', parser=general_ledger, header=False)

report_sxw.report_sxw('report.account.general.ledger.consild', 'account.account', 'addons/account_arabic_reports/report/account_general_ledger_consild.rml', parser=general_ledger, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
