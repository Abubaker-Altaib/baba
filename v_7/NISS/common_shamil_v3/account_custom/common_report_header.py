# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import pooler
from openerp.osv import osv, orm
from openerp.tools.translate import _
from account.report import common_report_header

class common_report_header(object):

    def _get_display_account(self, data):
        if data.get('form', False) and data['form'].get('display_account', False):
            if data['form']['display_account'] == 'bal_all':
                return _('All Accounts')
	    elif data['form']['display_account'] == 'bal_movement':
                return _('Parents Accounts')
            return _('By Categories')
        return ''

    def _get_label_according_model(self, data):
        if data['model'] == 'account.account':
            return _('Company')
	elif data['model'] == 'ir.ui.menu':
            return _('Chart of Account')
        return ''

    def _get_multi_company(self, data, account_id):
        wiz_company = self.pool.get('account.account').browse(self.cr,self.uid, data['form']['chart_account_id']).company_id
        acc_company = self.pool.get('account.account').browse(self.cr,self.uid, account_id).company_id
        if not wiz_company.id == acc_company.id:
            return   ' - ' + self.pool.get('account.account').browse(self.cr,self.uid,account_id).company_id.name 
        return   False


    ####################From getter helper #####################################
    def get_start_period_br(self, data):
        if data.get('form', False) and data['form'].get('period_from', False):
            return pooler.get_pool(self.cr.dbname).get('account.period').browse(self.cr,self.uid,data['form']['period_from']).name
        return ''
    def get_end_period_br(self, data):
        if data.get('form', False) and data['form'].get('period_to', False):
            return pooler.get_pool(self.cr.dbname).get('account.period').browse(self.cr,self.uid,data['form']['period_to']).name
        return ''
    
    def get_fiscalyear_br(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).name
        return ''

    def _get_chart_account_id_br(self, data):
        return self._get_info(data, 'chart_account_id', 'account.account')

    def _get_accounts_br(self, data):
        return self._get_info(data, 'account_ids', 'account.account')

    def _get_analytic_accounts_br(self, data):
        return self._get_info(data, 'analytic_account_ids', 'account.analytic.account')

    def _get_chart_analytic_account_id_br(self, data):
        return self._get_info(data, 'chart_analytic_account_id', 'account.analytic.account')

    def _get_info(self, data, field, model):
        info = data.get('form', {}).get(field)
        if info:
            return self.pool.get(model).browse(self.cr, self.uid, info)
        return False

    def _get_display_account(self, data):
        val = self._get_form_param('display_account', data)
        if val == 'bal_all':
            return _('All accounts')
        elif val == 'bal_mix':          
            return _('With transactions or non zero balance')
        elif val == 'all':           
            return _('All')  
        elif val == 'movement':            
            return _('with movement')               
        else:          
            return _('Not Zero')

    def _get_display_partner_account(self, data):
        val = self._get_form_param('result_selection', data)
        if val == 'customer':
            return _('Receivable Accounts')
        elif val == 'supplier':
            return _('Payable Accounts')
        elif val == 'customer_supplier':
            return _('Receivable and Payable Accounts')
        else:
            return val

    def _get_display_target_move(self, data):
        val = self._get_form_param('target_move', data)
        if val == 'posted':
            return _('All Posted Entries')
        elif val == 'all':
            return _('All Entries')
        else:
            return val

    def _get_display_account_raw(self, data):
        return self._get_form_param('display_account', data)

    def _get_filter(self, data):
        if data.get('form', False) and data['form'].get('filter', False):
            if data['form']['filter'] == 'filter_date':
                return 'Date'
            elif data['form']['filter'] == 'filter_period':
                return 'Periods'
        return 'No Filter'


    def _get_filter_Trans(self, data):
        if self._has_filter(data):
            if data['form']['filter'] == 'filter_date':
                return _('Date')
            elif data['form']['filter'] == 'filter_period':
                return _('Periods')
        return _('No Filters')

    def _get_sortby_gl(self, data):
        if self.sortby == 'sort_date':
            return _('Date')
        elif self.sortby == 'sort_journal_partner':
            
            return _('Journal & Partner')
        return _('Date')    
    
    def _get_target_move(self, data):
        if data.get('form', False) and data['form'].get('target_move', False):
            if data['form']['target_move'] == 'all':
                return _('All Entries')
            return _('All Posted Entries')
        return ''
    
    def _get_move(self, data):
	return self._get_form_param('moves', data)

    def _get_just_balance(self, data):
	return self._get_form_param('acc_balances', data)

    def _get_initial_balance(self, data):
        return self._get_form_param('initial_balance', data)

    def _get_amount_currency(self, data):
        return self._get_form_param('amount_currency', data)

    def _get_date_from(self, data):
        if data.get('form', False) and data['form'].get('date_from', False):
            return data['form']['date_from']
        return ''
    
    def _get_date_to(self, data):
        if data.get('form', False) and data['form'].get('date_to', False):
            return data['form']['date_to']
        return ''

    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default)

    def _get_form_param_translate(self, param, data, default=False):
        return _(self._get_form_param(param, data, default=default))

    ####################Account and account line filter helper #################

    def sort_accounts_with_structure(self, account_ids, context=None):
        """Sort accounts by code respecting their structure"""

        def recursive_sort_by_code(level, max_level, accounts, parent_id=False):
            sorted_accounts = []
            level_accounts = [account for account
                              in accounts
                              if account['level'] == level
                              and (not parent_id or
                                   account['parent_id'] and account['parent_id'][0] == parent_id)]
            if not level_accounts:
                return []

            level_accounts = sorted(level_accounts, key=lambda a: a['code'])
            for level_account in level_accounts:
                sorted_accounts.append(level_account['id'])
                if level < max_level:
                    sorted_accounts.extend(recursive_sort_by_code(level + 1, max_level, accounts, parent_id=level_account['id']))
            return sorted_accounts

        if not account_ids:
            return []
        accounts = self.pool.get('account.account').read(self.cr, self.uid,
                                                         account_ids,
                                                         ['id', 'parent_id', 'level', 'code'],
                                                         context=context)
        levels = [x['level'] for x in accounts]
        start_level = min(levels)
        max_level = max(levels)
        sorted_accounts = recursive_sort_by_code(start_level, max_level, accounts)
        res_acc = [acc for acc in account_ids if acc not in sorted_accounts]
        return sorted_accounts

    def get_all_accounts(self, account_ids, filter_view=False, filter_type=None, context=None):
        """Get all account passed in params with their childrens"""
        context = context or {}
        accounts = []
        if not isinstance(account_ids, list):
            account_ids = [account_ids]
        acc_obj = self.pool.get('account.account')
        for account_id in account_ids:
            accounts.append(account_id)
            accounts += acc_obj._get_children_and_consol(self.cr, self.uid, account_id, context=context)
        res_ids = list(set(accounts))
        res_ids = self.sort_accounts_with_structure(res_ids, context=context)

        if filter_view or filter_type:
            format_list = [tuple(res_ids)]
            sql = "SELECT id FROM account_account WHERE id IN %s "
            if filter_view:
                sql += " AND type != 'view'"
            if filter_type:
                sql += " AND type in %s"
                format_list.append(tuple(filter_type))

            self.cr.execute(sql, tuple(format_list))
            fetch_only_ids = self.cr.fetchall()
            if not fetch_only_ids:
                return []
            only_ids = [only_id[0] for only_id in fetch_only_ids]
            # keep sorting but filter ids
            res_ids = [res_id for res_id in res_ids if res_id in only_ids]
        return res_ids

    ####################Periods and fiscal years  helper #######################

    def _get_opening_periods(self):
        """Return the list of all journal that can be use to create opening entries
        We actually filter on this instead of opening period as older version of OpenERP
        did not have this notion"""
        return self.pool.get('account.period').search(self.cr,
                                                       self.uid,
                                                       [('special', '=', True)])


    def get_included_opening_period(self, period, check_move = True):
        """Return the opening included in normal period we use the assemption
        that there is only one opening period per fiscal year"""
        mv_line_obj = self.pool.get('account.move.line')
        period_obj =  self.pool.get('account.period')
        res = period_obj.search(self.cr,
                                self.uid,
                                [('special', '=', True),
                                 ('date_start', '>=', period.date_start),
                                 ('date_stop', '<=', period.date_stop)],
                                limit=1)
        if check_move and res:
            validation_res = mv_line_obj.search(self.cr,
                                                self.uid,
                                                [('period_id', '=', res[0])],
                                                limit=1)
            if not validation_res:
                return False
        return res

    def _get_period_range_form_periods(self, start_period, stop_period, mode):
        # TODO test date type
        period_obj = self.pool.get('account.period')
        search_period = [('date_start', '>=', start_period.date_start),
                         ('date_stop', '<=', stop_period.date_stop)]
                         
        if mode == 'exclude_opening':
            search_period += [('special', '=', False)]
        res = period_obj.search(self.cr, self.uid, search_period)
        return res

    def _get_period_range_form_start_period(self, start_period, include_opening=False,
                                            fiscalyear=False, stop_at_previous_opening=False):
        """We retrieve all periods before start period"""
        opening_period_id = False
        period_obj = self.pool.get('account.period')
        fisc_year_obj = self.pool.get('account.fiscalyear')
        mv_line_obj = self.pool.get('account.move.line')
        # We look for previous opening period
        if stop_at_previous_opening:
            opening_search = [('special', '=', True),
                             ('date_stop', '<', start_period.date_start)]
            if fiscalyear :
                opening_search.append(('fiscalyear_id', '=', fiscalyear.id))

            opening_periods = period_obj.search(self.cr, self.uid, opening_search,
                                                order='date_stop desc')
            for opening_period in opening_periods:
                validation_res = mv_line_obj.search(self.cr,
                                                    self.uid,
                                                    [('period_id', '=', opening_period)],
                                                    limit=1)
                if validation_res:
                    opening_period_id = opening_period
                    break
        past_limit = []
        if opening_period_id:
            #we also look for overlapping periods
            opening_period_br = period_obj.browse(self.cr, self.uid, opening_period_id)
            past_limit = [('date_start', '>=', opening_period_br.date_stop)]

        periods_search = [('date_stop', '<=', start_period.date_stop)]
        periods_search += past_limit

        if not include_opening:
            periods_search += [('special', '=', False)]

        if fiscalyear :
            periods_search.append(('fiscalyear_id', '=', fiscalyear.id))
        periods = period_obj.search(self.cr, self.uid, periods_search)
        if include_opening and opening_period_id:
            periods.append(opening_period_id)
        periods = list(set(periods))
        if start_period.id in periods:
            periods.remove(start_period.id)
        return periods


    def get_first_fiscalyear_period(self, fiscalyear):
        return self._get_st_fiscalyear_period(fiscalyear)


    def get_last_fiscalyear_period(self, fiscalyear):
        return self._get_st_fiscalyear_period(fiscalyear, order='DESC')


    def _get_st_fiscalyear_period(self, fiscalyear, order='ASC'):
        period_obj = self.pool.get('account.period')
        p_id = period_obj.search(self.cr, self.uid, [('special','=', False),
                                  ('fiscalyear_id', '=', fiscalyear.id)],
                                 limit=1, order='date_start %s' % (order,))
        if not p_id:
            raise orm.except_orm(_('No normal period found'),'')
        return period_obj.browse(self.cr, self.uid, p_id[0])

    ####################Initial Balance helper #################################

    def _compute_init_balance(self, account, period_ids, mode='computed'):
        if not isinstance(period_ids, list):
            period_ids = [period_ids]

        try:
            self.cr.execute("SELECT sum(debit)-sum(credit) as balance,"
                                " sum(amount_currency) as curr_balance"
                                " FROM account_move_line"
                                " where period_id in %s"
                                " And account_id = %s", (tuple(period_ids), account.id))
            res = self.cr.fetchone()

        except Exception, exc:
            self.cr.rollback()
            raise exc
        return {'init_balance': res[0] or 0.0, 'init_balance_currency': res[1] or 0.0, 'state': mode}


    def _compute_inital_balances(self, account_ids, start_period, fiscalyear, main_filter):
        """We compute initial balance.
        If form is filtered by date all initial balance are equal to 0
        This function will sum pear and apple in currency amount if account as no secondary currency"""
        opening_periods = self._get_opening_periods()
        # if opening period is included in start period we do not need to compute init balance
        # we just read it from opening entries
        read_period_id = self.get_included_opening_period(start_period)
        res = {}
        if main_filter in ('filter_period', 'filter_no'):

            # PNL and Balance accounts are not computed the same way look for attached doc
            # We include opening period in pnl account in order to see if opening entries
            # were created by error on this account
            pnl_periods_ids = self._get_period_range_form_start_period(start_period, fiscalyear=fiscalyear,
                                                                       include_opening=True)

            bs_period_ids = self._get_period_range_form_start_period(start_period, include_opening=True,
                                                                     stop_at_previous_opening=True)
            nil_res = {'init_balance': 0.0, 'init_balance_currency': 0.0, 'state': 'computed'}
            for acc in self.pool.get('account.account').browse(self.cr, self.uid, account_ids):
                if acc.user_type.close_method == 'none':
                    if pnl_periods_ids:
                        res[acc.id] = self._compute_init_balance(acc, pnl_periods_ids)
                    else:
                        res[acc.id] = nil_res
                else :
                    if read_period_id:
                        res[acc.id] = self._compute_init_balance(acc, read_period_id, mode='read')
                    elif bs_period_ids:
                        res[acc.id] = self._compute_init_balance(acc, bs_period_ids)
                    else:
                        res[acc.id] = nil_res
        else:
            for acc_id in account_ids:
                res[acc_id] = {'init_balance': 0.0, 'init_balance_currency': 0.0, 'state': 'disable'}
        return res

    ####################Account move retrieval helper ##########################
    def _get_move_ids_from_periods(self, account_id, period_start, period_stop, mode, valid_only=False):
        move_line_obj = self.pool.get('account.move.line')
        # we filter opening period here
        periods = self._get_period_range_form_periods(period_start, period_stop, mode)
        if not periods:
            return []
        search = [('period_id', 'in', periods), ('account_id', '=', account_id)]
        if valid_only:
            search += [('state', '=', 'valid')]
        return move_line_obj.search(self.cr, self.uid, search)

    def _get_move_ids_from_dates(self, account_id, date_start, date_stop, mode, valid_only=False):
        # TODO imporve perfomance by setting opening period as a property
        move_line_obj = self.pool.get('account.move.line')
        search_period = [('date', '>=', date_start), 
                         ('date', '<=', date_stop),
                         ('account_id', '=', account_id)]
                         
        if mode == 'exclude_opening':
            opening = self._get_opening_periods()
            if opening:
                search_period += ['period_id', 'not in', opening]
                
        if valid_only:
            search_period += [('state', '=', 'valid')]
        return move_line_obj.search(self.cr, self.uid, search_period)

    def get_move_lines_ids(self, account_id, main_filter, start, stop, mode='include_opening', valid_only=False):
        """Get account move lines base on form data"""
        res = {}
        if mode not in ('include_opening', 'exclude_opening'):
            raise orm.except_orm(_('Invalid query mode'), _('Must be in include_opening, exclude_opening'))

        if main_filter in ('filter_period', 'filter_no'):
            return self._get_move_ids_from_periods(account_id, start, stop, mode, valid_only=valid_only)
            
        elif main_filter == 'filter_date':
            return self._get_move_ids_from_dates(account_id, start, stop, mode, valid_only=valid_only)
            
        else:
            raise orm.except_orm(_('No valid filter'), _('Please set a valid time filter'))

    def _get_move_line_datas(self, move_line_ids, order='l.date ASC, per.special DESC, per.date_start ASC, m.name ASC'):
        if not move_line_ids:
            return []
        if not isinstance(move_line_ids, list):
            move_line_ids = [move_line_ids]
        monster ="""
SELECT l.id AS lid,
            l.date AS ldate,
            j.code AS jcode ,
            l.currency_id,
            l.account_id,
            l.amount_currency,
            l.ref AS lref,
            l.name AS lname,
            COALESCE(l.debit, 0.0) - COALESCE(l.credit, 0.0) AS balance,
            l.period_id AS lperiod_id,
            per.code as period_code,
            per.special AS peropen,
            l.partner_id AS lpartner_id,
            p.name AS partner_name,
            m.name AS move_name,
             COALESCE(partialrec.name, fullrec.name, '') AS rec_name,
            m.id AS move_id,
            c.name AS currency_code,
            i.id AS invoice_id,
            i.type AS invoice_type,
            i.number AS invoice_number
FROM account_move_line l
    JOIN account_move m on (l.move_id=m.id)
    LEFT JOIN res_currency c on (l.currency_id=c.id)
    LEFT JOIN account_move_reconcile partialrec on (l.reconcile_partial_id = partialrec.id)
    LEFT JOIN account_move_reconcile fullrec on (l.reconcile_id = fullrec.id)
    LEFT JOIN res_partner p on (l.partner_id=p.id)
    LEFT JOIN account_invoice i on (m.id =i.move_id)
    LEFT JOIN account_period per on (per.id=l.period_id)
    JOIN account_journal j on (l.journal_id=j.id)
    WHERE l.id in %s"""
        monster += (" ORDER BY %s" % (order,))
        try:
            self.cr.execute(monster, (tuple(move_line_ids),))
            res= self.cr.dictfetchall()
        except Exception, exc:
            self.cr.rollback()
            raise
        if res:
            return res
        else:
            return []

    def _get_moves_counterparts(self, move_ids, account_id, limit=3):
        if not move_ids:
            return {}
        if not isinstance(move_ids, list):
            move_ids = [move_ids]
        to_retunr = {}
        sql = """
SELECT account_move.id,
       array_to_string(
          ARRAY(SELECT DISTINCT a.code
                FROM account_move_line m2
                  LEFT JOIN account_account a ON (m2.account_id=a.id)
                WHERE m2.move_id =account_move_line.move_id
                  AND m2.account_id<>%s limit %s) , ', ')

FROM account_move
        JOIN account_move_line on (account_move_line.move_id = account_move.id)
        JOIN account_account on (account_move_line.account_id = account_account.id)
WHERE move_id in %s"""

        try:
            self.cr.execute(sql, (account_id, limit, tuple(move_ids)))
            res= self.cr.fetchall()
        except Exception, exc:
            self.cr.rollback()
            raise exc
        if res:
            return dict(res)
        else:
            return {}
        
    # Add NEW
    
    def _get_Translation(self, data):
        return _(data)
    
    def _get_journal(self, data):
        codes = []
        if data.get('form', False) and data['form'].get('journal_ids', False):
            self.cr.execute('select code from account_journal where id IN %s',(tuple(data['form']['journal_ids']),))
            codes = [x for x, in self.cr.fetchall()][0]
        return codes
    
    def _get_company(self, data):
        return self._get_chart_account_id_br(data).company_id.name

    def _get_currency(self, data):
        return self._get_chart_account_id_br(data).company_id.company_id.currency_id.symbol


    def _sum_debit_period(self, period_id, journal_id=None):
        journals = journal_id or self.journal_ids
        if not journals:
            return 0.0
        self.cr.execute('SELECT SUM(debit) FROM account_move_line l '
                        'WHERE period_id=%s AND journal_id IN %s '+ self.query_get_clause +'',
                        (period_id, tuple(journals)))

        return self.cr.fetchone()[0] or 0.0

    def _sum_credit_period(self, period_id, journal_id=None):
        journals = journal_id or self.journal_ids
        if not journals:
            return 0.0
        self.cr.execute('SELECT SUM(credit) FROM account_move_line l '
                        'WHERE period_id=%s AND journal_id IN %s ' + self.query_get_clause +' ',
                        (period_id, tuple(journals)))
        return self.cr.fetchone()[0] or 0.0


    def _sum_debit(self, period_id=False, journal_id=False):
        if journal_id and isinstance(journal_id, int):
            journal_id = [journal_id]
        if period_id and isinstance(period_id, int):
            period_id = [period_id]
        if not journal_id:
            journal_id = self.journal_ids
        if not period_id:
            period_id = self.period_ids
        if not (period_id and journal_id):
            return 0.0
        self.cr.execute('SELECT SUM(debit) FROM account_move_line l '
                        'WHERE period_id IN %s AND journal_id IN %s ' + self.query_get_clause + ' ',
                        (tuple(period_id), tuple(journal_id)))
        return self.cr.fetchone()[0] or 0.0

    def _sum_credit(self, period_id=False, journal_id=False):
        if journal_id and isinstance(journal_id, int):
            journal_id = [journal_id]
        if period_id and isinstance(period_id, int):
            period_id = [period_id]
        if not journal_id:
            journal_id = self.journal_ids
        if not period_id:
            period_id = self.period_ids
        if not (period_id and journal_id):
            return 0.0
        self.cr.execute('SELECT SUM(credit) FROM account_move_line l '
                        'WHERE period_id IN %s AND journal_id IN %s '+ self.query_get_clause+'',
                        (tuple(period_id), tuple(journal_id)))
        return self.cr.fetchone()[0] or 0.0

    def _get_children_and_consol(self, cr, uid, ids, module, context={}):
        #this function search for all the children and all consolidated children (recursively) of the given account ids
        ids2 = self.pool.get(module).search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.pool.get(module).browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, module, context)    
        return ids2 + ids3
    
#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:  
