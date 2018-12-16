# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from common_report_header import common_report_header

class third_party_ledger(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(third_party_ledger, self).__init__(cr, uid, name, context=context)
        self.init_bal_sum = 0.0
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit_partner': self._sum_debit_partner,
            'sum_credit_partner': self._sum_credit_partner,
            'get_currency': self._get_currency,
            'comma_me': self.comma_me,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_account': self._get_account,
            'get_filter': self._get_filter,
            'get_filter_Trans': self._get_filter_Trans,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_fiscalyear': self._get_fiscalyear,
            'get_journal': self._get_journal,
            'get_partners':self._get_partners,
            'get_intial_balance':self._get_intial_balance,
            'display_initial_balance':self._display_initial_balance,
            'display_currency':self._display_currency,
            'get_target_move': self._get_target_move,
            'get_init_array':self._get_init_array,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        obj_partner = self.pool.get('res.partner')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
        ctx2 = data['form'].get('used_context', {}).copy()
        self.initial_balance = data['form'].get('initial_balance', True)
        self.cumulate_move = data['form'].get('cumulate_move', True)
        if self.initial_balance:
            ctx2.update({'initial_bal': True, 'periods':[]})
            self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        self.reconcil = data['form'].get('reconcil', True)
        self.result_selection = data['form'].get('result_selection', 'customer')
        self.amount_currency = data['form'].get('amount_currency', False)
        self.target_move = data['form'].get('target_move', 'all')
        self.partner_id = data['form'].get('partner_ids')
        self.account_ids = data['form'].get('account_ids', [])
        
        self.init_array = []
        PARTNER_REQUEST = ''

        self.state_query = ""
        if self.target_move == 'posted':
            self.state_query = " AND am.state = 'posted' "


        obj_account = self.pool.get('account.account')

        if (data['model'] == 'res.partner'):
            # # Si on imprime depuis les partenaires
            if ids:
                PARTNER_REQUEST = "AND line.partner_id IN %s", (tuple(ids),)
        if self.result_selection == 'supplier':
            self.ACCOUNT_TYPE = ['payable']
        elif self.result_selection == 'customer':
            self.ACCOUNT_TYPE = ['receivable']
        else:
            self.ACCOUNT_TYPE = ['payable', 'receivable']

        if not self.account_ids: 
            child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ctx2.get('chart_account_id', []), ctx2)
            self.account_ids = obj_account.search(self.cr, self.uid, [('id', 'in', child_ids), ('type', 'in', self.ACCOUNT_TYPE)])

        partner_to_use = []

        if self.partner_id:
            partner_to_use = self.partner_id
        else:
            # self.pool.get('res.partner').search(cr, uid, [()])
            self.cr.execute(
                "SELECT DISTINCT l.partner_id " \
                "FROM account_move_line AS l, account_account AS account, " \
                " account_move AS am " \
                "WHERE l.partner_id IS NOT NULL " \
                    "AND l.account_id = account.id " \
                    "AND am.id = l.move_id " + self.state_query + " "
                    "AND l.account_id IN %s " \
                    " " + PARTNER_REQUEST + " " \
                    "AND account.active ",
                (tuple(self.account_ids),))

            res = self.cr.dictfetchall()
            for res_line in res:
                partner_to_use.append(res_line['partner_id'])
        new_ids = partner_to_use

        self.partner_ids = new_ids
        objects = obj_partner.browse(self.cr, self.uid, new_ids)
        
        return super(third_party_ledger, self).set_context(objects, data, new_ids, report_type)

    def comma_me(self, amount):
        if type(amount) is float:
            amount = str('%.2f' % amount)
        else:
            amount = str(amount)
        if (amount == '0'):
             return ' '
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>'\g<2>", amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)

    def lines(self, partner):
        full_account = []
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND l.reconcile_id IS NULL"
        if self.cumulate_move:
            self.cr.execute(
                "SELECT min(l.id) as id, min(l.date) as date , min(j.code) as code, min(acc.code) as a_code, min(acc.name) as a_name, min(l.ref) as ref, min(am.name) as move_name, min(l.name) as name,CASE WHEN sum(debit) > sum(credit) THEN sum(debit) - sum(credit) ELSE 0 END AS debit , CASE WHEN sum(credit) > sum(debit) THEN sum(credit) - sum(debit) ELSE 0 END AS credit, min(l.amount_currency) as amount_currency,min(l.currency_id) as currency_id, min(c.symbol) AS currency_code " \
                "FROM account_move_line l " \
                "LEFT JOIN account_journal j " \
                    "ON (l.journal_id = j.id) " \
                "LEFT JOIN account_account acc " \
                    "ON (l.account_id = acc.id) " \
                "LEFT JOIN res_currency c ON (l.currency_id=c.id)" \
                "LEFT JOIN account_move am ON (am.id=l.move_id)" \
                "WHERE l.partner_id = %s " \
                    "AND l.account_id IN %s AND " + self.query + " " + self.state_query + " " \
                    " " + RECONCILE_TAG + " "\
                    " group by l.move_id ORDER BY date ",
                    (partner.id, tuple(self.account_ids)))
        else:
            self.cr.execute(
                "SELECT l.id, l.date, j.code, acc.code as a_code, acc.name as a_name, l.ref, am.name as move_name, l.name, l.debit, l.credit, l.amount_currency,l.currency_id, c.symbol AS currency_code " \
                "FROM account_move_line l " \
                "LEFT JOIN account_journal j " \
                    "ON (l.journal_id = j.id) " \
                "LEFT JOIN account_account acc " \
                    "ON (l.account_id = acc.id) " \
                "LEFT JOIN res_currency c ON (l.currency_id=c.id)" \
                "LEFT JOIN account_move am ON (am.id=l.move_id)" \
                "WHERE l.partner_id = %s " \
                    "AND l.account_id IN %s AND " + self.query + " " + self.state_query + " " \
                    " " + RECONCILE_TAG + " "\
                    "ORDER BY l.date",
                    (partner.id, tuple(self.account_ids)))

        res = self.cr.dictfetchall()
        sum = 0.0
        if self.initial_balance:
            sum = self.init_bal_sum
        for r in res:
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            full_account.append(r)
        return full_account

    def _get_init_array(self):
        return self.init_array

    def _get_intial_balance(self, partner):
        self.init_array = []
        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted']
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND l.reconcile_id IS NULL"
        self.cr.execute(
            "SELECT COALESCE(SUM(l.debit),0.0), COALESCE(SUM(l.credit),0.0), COALESCE(sum(debit-credit), 0.0) " \
            "FROM account_move_line AS l,  " \
            "account_move AS am "
            "WHERE l.partner_id = %s " \
            "AND am.id = l.move_id " + self.state_query + " "\
            "AND account_id IN %s" \
            " " + RECONCILE_TAG + " "\
            "AND " + self.init_query + "  ",
            (partner.id, tuple(self.account_ids)))
        res = self.cr.fetchall()
        self.init_bal_sum = res[0][2]
        self.init_array = res

    def _sum_debit_partner(self, partner):
        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted']

        result_tmp = 0.0
        result_init = 0.0
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND reconcile_id IS NULL"
        if self.initial_balance:
            self.cr.execute(
                    "SELECT sum(debit) " \
                    "FROM account_move_line AS l, " \
                    "account_move AS am "
                    "WHERE l.partner_id = %s" \
                        "AND am.id = l.move_id " + self.state_query + " "\
                        "AND account_id IN %s" \
                        " " + RECONCILE_TAG + " " \
                        "AND " + self.init_query + " ",
                    (partner.id, tuple(self.account_ids)))
            contemp = self.cr.fetchone()
            if contemp != None:
                result_init = contemp[0] or 0.0
            else:
                result_init = result_tmp + 0.0
        if self.cumulate_move:
            self.cr.execute(
                    "select sum(debit) as debit from (SELECT  CASE WHEN sum(debit) > sum(credit) THEN sum(debit) - sum(credit) ELSE 0 END AS debit " \
                "FROM account_move_line AS l, " \
                "account_move AS am "
                "WHERE l.partner_id = %s " \
                    "AND am.id = l.move_id " + self.state_query + " "\
                    "AND account_id IN %s" \
                    " " + RECONCILE_TAG + " " \
                    "AND " + self.query + "  group by l.move_id) as result",
                (partner.id, tuple(self.account_ids),))
        else:
            self.cr.execute(
                "SELECT sum(debit) " \
                "FROM account_move_line AS l, " \
                "account_move AS am "
                "WHERE l.partner_id = %s " \
                    "AND am.id = l.move_id " + self.state_query + " "\
                    "AND account_id IN %s" \
                    " " + RECONCILE_TAG + " " \
                    "AND " + self.query + " ",
                (partner.id, tuple(self.account_ids),))

        contemp = self.cr.fetchone()
        if contemp != None:
            result_tmp = contemp[0] or 0.0
        else:
            result_tmp = result_tmp + 0.0

        return result_tmp + result_init

    def _sum_credit_partner(self, partner):
        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted']

        result_tmp = 0.0
        result_init = 0.0
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND reconcile_id IS NULL"
        if self.initial_balance:
            self.cr.execute(
                    "SELECT sum(credit) " \
                    "FROM account_move_line AS l, " \
                    "account_move AS am  "
                    "WHERE l.partner_id = %s" \
                        "AND am.id = l.move_id " + self.state_query + " "\
                        "AND account_id IN %s" \
                        " " + RECONCILE_TAG + " " \
                        "AND " + self.init_query + " ",
                    (partner.id, tuple(self.account_ids)))
            contemp = self.cr.fetchone()
            if contemp != None:
                result_init = contemp[0] or 0.0
            else:
                result_init = result_tmp + 0.0
        if self.cumulate_move:
            self.cr.execute(
                    "select sum(credit) as credit from (SELECT  CASE WHEN sum(credit) > sum(debit) THEN sum(credit) - sum(debit) ELSE 0 END AS credit " \
                "FROM account_move_line AS l, " \
                "account_move AS am "
                "WHERE l.partner_id=%s " \
                    "AND am.id = l.move_id " + self.state_query + " "\
                    "AND account_id IN %s" \
                    " " + RECONCILE_TAG + " " \
                    "AND " + self.query + "  group by l.move_id) as result",
                (partner.id, tuple(self.account_ids),))
        else:
            self.cr.execute(
                "SELECT sum(credit) " \
                "FROM account_move_line AS l, " \
                "account_move AS am "
                "WHERE l.partner_id=%s " \
                    "AND am.id = l.move_id " + self.state_query + " "\
                    "AND account_id IN %s" \
                    " " + RECONCILE_TAG + " " \
                    "AND " + self.query + " ",
                (partner.id, tuple(self.account_ids),))   
        contemp = self.cr.fetchone()
        if contemp != None:
            result_tmp = contemp[0] or 0.0
        else:
            result_tmp = result_tmp + 0.0
        return result_tmp + result_init

    def _get_partners(self):
        if self.result_selection == 'customer':
            return _('Receivable Accounts')
        elif self.result_selection == 'supplier':
            return _('Payable Accounts')
        elif self.result_selection == 'customer_supplier':
            return _('Receivable and Payable Accounts')
        return ''

    def _sum_currency_amount_account(self, account, form):
        self._set_get_account_currency_code(account.id)
        self.cr.execute("SELECT sum(aml.amount_currency) FROM account_move_line as aml,res_currency as rc WHERE aml.currency_id = rc.id AND aml.account_id= %s ", (account.id,))
        total = self.cr.fetchone()
        if self.account_currency:
            return_field = str(total[0]) + self.account_currency
            return return_field
        else:
            currency_total = self.tot_currency = 0.0
            return currency_total

    def _display_initial_balance(self, data):
         if self.initial_balance:
             return True
         return False

    def _display_currency(self, data):
        return self.amount_currency


report_sxw.report_sxw('report.account.partner.ledger.other.arabic', 'res.partner',
        'addons/account_arabic_reports/report/account_partner_ledger_other.rml', parser=third_party_ledger,
        header='custom landscape')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
