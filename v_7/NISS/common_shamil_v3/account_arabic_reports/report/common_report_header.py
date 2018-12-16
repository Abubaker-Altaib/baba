# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import pooler
from openerp.tools.translate import _
from openerp.osv import orm

class common_report_header(object):

    def _get_st_fiscalyear_period(self, fiscalyear, order='ASC'):
        period_obj = self.pool.get('account.period')
        p_id = period_obj.search(self.cr,
                                 self.uid,
                                 [('special','=', False),
                                  ('fiscalyear_id', '=', fiscalyear.id)],
                                 limit=1,
                                 order='date_start %s' % (order,))
        if not p_id:
            raise orm.except_orm(_('No normal period found'),'')
        return period_obj.browse(self.cr, self.uid, p_id[0]).name

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

    def _get_start_date(self, data):
        if data.get('form', False) and data['form'].get('date_from', False):
            return data['form']['date_from']
        return ''

    def _get_target_move(self, data):
        if data.get('form', False) and data['form'].get('target_move', False):
            if data['form']['target_move'] == 'all':
                return _('All Entries')
            return _('All Posted Entries')
        return ''

    def _get_end_date(self, data):
        if data.get('form', False) and data['form'].get('date_to', False):
            return data['form']['date_to']
        return ''

    def get_start_period(self, data):
        if data.get('form', False) and data['form'].get('period_from', False):
            return pooler.get_pool(self.cr.dbname).get('account.period').browse(self.cr,self.uid,data['form']['period_from']).name
	else:
	    FY = pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id'])
	    return  self._get_st_fiscalyear_period(FY)
        return ''

    def get_end_period(self, data):
        if data.get('form', False) and data['form'].get('period_to', False):
            return pooler.get_pool(self.cr.dbname).get('account.period').browse(self.cr, self.uid, data['form']['period_to']).name
	else:
	    FY = pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id'])
	    return self._get_st_fiscalyear_period(FY, order='DESC')
        return ''

    def _get_account(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return pooler.get_pool(self.cr.dbname).get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).name
        return ''

    def _get_sortby(self, data):
        raise (_('Error'), _('Not implemented'))

    def _get_filter(self, data):
        if data.get('form', False) and data['form'].get('filter', False):
            if data['form']['filter'] == 'filter_date':
                return 'Date'
            elif data['form']['filter'] == 'filter_period':
                return 'Periods'
        return 'No Filter'

    def _get_filter_Trans(self, data):
	if data.get('form', False) and data['form'].get('filter', False):
            if data['form']['filter'] == 'filter_date':
                return _('Date')
            elif data['form']['filter'] == 'filter_period':
                return _('Periods')
        return _('No Filter')

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

    def _get_fiscalyear(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).name
        return ''    

    def _get_company(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return pooler.get_pool(self.cr.dbname).get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).company_id.name
        return ''

    def _get_journal(self, data):
        codes = []
        if data.get('form', False) and data['form'].get('journal_ids', False):
            self.cr.execute('select code from account_journal where id IN %s',(tuple(data['form']['journal_ids']),))
            codes = [x for x, in self.cr.fetchall()]
        return codes

    def _get_currency(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return pooler.get_pool(self.cr.dbname).get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).company_id.currency_id.symbol
        return ''

    def _get_Translation(self, data):
        return _(data)


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
        wiz_company = self.pool.get('account.account').browse(self.cr,self.uid, data['form']['chart_account_id'][0]).company_id
        acc_company = self.pool.get('account.account').browse(self.cr,self.uid, account_id).company_id
        if not wiz_company.id == acc_company.id:
            return   ' - ' + self.pool.get('account.account').browse(self.cr,self.uid,account_id).company_id.name 
        return   False

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:  
