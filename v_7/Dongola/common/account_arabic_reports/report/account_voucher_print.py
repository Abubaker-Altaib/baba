# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import datetime
from report import report_sxw
from tools import amount_to_text_en
import pooler

class report_voucher_move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_voucher_move, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'datetime':datetime,
            'convert':self.convert,
            'get_name': self._get_name,
            'get_title': self.get_title,
            'debit':self.debit,
            'credit':self.credit,
            'get_creator':self.get_creator,
            'get_authoriser':self.get_authoriser,
            'write_date':self.get_write_date,
            'create_date':self. get_create_date,
            'get_info':self.get_info,
            'is_Cash':self.is_Cash,
            'cash_credit':self.cash_credit,
            'cash_debit':self.cash_debit,
            'receipt_voucher':self.receipt_voucher,
            'payment_voucher':self.payment_voucher,
            'usd_rate':self.usd_rate,
            'eur_rate':self.eur_rate,
            'is_payment_voucher':self.is_payment_voucher,
            'is_receipt_voucher':self.is_receipt_voucher,
            'no_lines':self._no_lines,
            'auditLog_fn':self._auditLog_fn,
            'get_users':self._get_users,
            'get_vouchers':self._get_vouchers,
        })
        self.user = uid
        self.auditLog = {'closer':0,'close_date':0,'auditor':0,'audit_date':0,'completer':0,'complete_date':0,'authoriser':0,'authorise_date':0,}

    def _get_name(self, move_line):
        name = ''
        for move in move_line:
            if move.name:
                name =move.name
        
        return name

    def _get_vouchers(self,move):
        print move
        vouchers = pooler.get_pool(self.cr.dbname).get('account.voucher').search(self.cr, self.uid, [('move_id','=',move.id)])
        return pooler.get_pool(self.cr.dbname).get('account.voucher').browse(self.cr, self.uid, vouchers)


    def _get_users(self, key):
        return self.auditLog[key]

    def _auditLog_fn(self, move_id):
        self.cr.execute("SELECT usr.signature,timestamp,aud.method FROM 	res_users usr INNER JOIN audittrail_log aud ON aud.user_id = usr.id WHERE aud.res_id = %s AND  aud.object_id = ( SELECT id FROM ir_model WHERE model='account.move' ) ORDER BY  timestamp desc",(move_id,))
        res = self.cr.dictfetchall()
        for r in res:

            if r['method'] == 'completed' and self.auditLog['completer'] == 0:
                print 'completer'
                self.auditLog['completer'] = r['signature']
                self.auditLog['complete_date'] =r['timestamp']

            if r['method'] == 'closed' and self.auditLog['closer'] == 0:
                print 'closer'
                self.auditLog['closer'] = r['signature']
                self.auditLog['close_date'] =r['timestamp']
            '''
            if r['method'] == 'audited' and self.auditLog['auditor'] == 0:
                print 'auditor'
                self.auditLog['auditor'] = r['signature']
                self.auditLog['audit_date'] =r['timestamp']
            '''
            if r['method'] == 'post' and self.auditLog['authoriser'] == 0:
                print 'authoriser'
                self.auditLog['authoriser'] = r['signature']
                self.auditLog['authorise_date'] =r['timestamp']


    def _no_lines(self, move_id):
        return len(self.pool.get('account.move.line').search(self.cr, self.user, [('move_id','=',move_id)] ))

    def convert(self, amount):
        user_id = self.pool.get('res.users').browse(self.cr, self.user, [self.user])[0]
        return amount_to_text_en.amount_to_text(amount, 'en', user_id.company_id.currency_id.name)

    def get_title(self, voucher):
        title = ''
        if voucher.journal_id:
            type = voucher.journal_id.type
            title = type[0].swapcase() + type[1:] + " Voucher"
        return title

    def debit(self, move_ids):
        debit = 0.0
        for move in move_ids:
            debit +=move.debit
        return debit

    def credit(self, move_ids):
        credit = 0.0
        for move in move_ids:
            credit +=move.credit
        return credit
    
    def cash_debit(self, move_line):
        debit = 0.0
        for move in move_line:
            if move.account_id.user_type.code == 'cash':
                debit +=move.debit
        return debit

    def cash_credit(self, move_line):
        credit = 0.0
        for move in move_line:
            if move.account_id.user_type.code == 'cash':
                credit +=move.credit
        return credit

    def get_creator(self, move_ids):
        self.cr.execute('SELECT usr.name FROM account_move move INNER JOIN res_users usr ON usr.id = move.create_uid WHERE move.id=%s',(move_ids,))
        res = self.cr.fetchone()[0] or 0.0
        return res

    def get_authoriser(self, move_ids):
        self.cr.execute('SELECT usr.name FROM account_move move INNER JOIN res_users usr ON usr.id = move.write_uid WHERE move.id=%s',(move_ids,))
        res = self.cr.fetchone()[0] or 0.0
        return res

    def get_write_date(self, move_ids):
        self.cr.execute('SELECT write_date FROM account_move WHERE id=%s',(move_ids,))
        res = self.cr.fetchone()[0] or 0.0
        return res

    def get_create_date(self, move_ids):
        self.cr.execute('SELECT create_date FROM account_move WHERE id=%s',(move_ids,))
        res = self.cr.fetchone()[0] or 0.0
        return res

    def get_info(self, move_ids):
        result = {}
        self.cr.execute('SELECT create_date,write_date FROM account_move WHERE id=%s',(move_ids,))
        res = self.cr.fetchone()        
        result['create_date'] = res[0]
        result['write_date'] = res[1]

        self.cr.execute('SELECT usr.name as creator FROM account_move move INNER JOIN res_users usr ON usr.id = move.create_uid WHERE move.id=%s',(move_ids,))
        result['creator'] = self.cr.fetchone()[0]

        self.cr.execute('SELECT usr.name as authoriser FROM account_move move INNER JOIN res_users usr ON usr.id = move.write_uid WHERE move.id=%s',(move_ids,))
        result['authoriser'] = self.cr.fetchone()[0]
        return result

    def is_Cash(self, move_ids):
        moves = self.pool.get('account.move').browse(self.cr, self.user, move_ids).line_id
        for line in moves:
            if line.account_id.user_type.code == 'cash':
                return True
        return False

    def receipt_voucher(self, move_ids):
        self.cr.execute("SELECT SUM(ml.debit) amount,ml.ref,p.name FROM account_move move INNER JOIN account_move_line ml ON ml.move_id = move.id INNER JOIN account_account a ON a.id = ml.account_id INNER JOIN account_account_type acct ON acct.id = a.user_type LEFT OUTER JOIN res_partner p ON p.id = ml.partner_id WHERE move.id = %s AND acct.code = 'cash' GROUP BY p.id,p.name,ml.ref HAVING SUM(ml.debit) <> 0",(move_ids,))
        res = self.cr.dictfetchall()
        return res

    def payment_voucher(self, move_ids):
        self.cr.execute("SELECT SUM(ml.credit) amount,ml.ref,p.name FROM account_move move INNER JOIN account_move_line ml ON ml.move_id = move.id INNER JOIN account_account a ON a.id = ml.account_id INNER JOIN account_account_type acct ON acct.id = a.user_type LEFT OUTER JOIN res_partner p ON p.id = ml.partner_id WHERE move.id = %s AND acct.code = 'cash' GROUP BY p.id,p.name,ml.ref HAVING SUM(ml.credit) <> 0",(move_ids,))

        #self.cr.execute("SELECT SUM(ml.debit) amount,ml.ref,p.name FROM account_move move INNER JOIN account_move_line ml ON ml.move_id = move.id INNER JOIN res_partner p ON p.id = ml.partner_id INNER JOIN account_account a ON a.id = ml.account_id INNER JOIN account_account_type acct ON acct.id = a.user_type WHERE move.id = %s AND NOT(acct.code = 'cash') GROUP BY p.id,p.name,ml.ref HAVING SUM(ml.debit) <> 0",(move_ids,))
        res = self.cr.dictfetchall()
        return res

    def is_receipt_voucher(self, move_ids):
        self.cr.execute("SELECT COALESCE(SUM(ml.debit),0.0) amount FROM account_move move INNER JOIN account_move_line ml ON ml.move_id = move.id INNER JOIN account_account a ON a.id = ml.account_id INNER JOIN account_account_type acct ON acct.id = a.user_type WHERE move.id = %s AND acct.code = 'cash'  ",(move_ids,))
        res = self.cr.fetchone()[0]
        return res

    def is_payment_voucher(self, move_ids):
        print move_ids
        self.cr.execute("SELECT COALESCE(SUM(ml.credit),0.0) amount FROM account_move move INNER JOIN account_move_line ml ON ml.move_id = move.id INNER JOIN account_account a ON a.id = ml.account_id INNER JOIN account_account_type acct ON acct.id = a.user_type WHERE move.id = %s AND acct.code = 'cash'  ",(move_ids,))

        #self.cr.execute("SELECT COALESCE(SUM(ml.debit),0.0) amount FROM account_move move INNER JOIN account_move_line ml ON ml.move_id = move.id INNER JOIN account_account a ON a.id = ml.account_id INNER JOIN account_account_type acct ON acct.id = a.user_type WHERE move.id = %s AND NOT(acct.code = 'cash') AND ml.partner_id IS NOT NULL ",(move_ids,))
        res = self.cr.fetchone()[0]
        return res

    def usd_rate(self):
        self.cr.execute("SELECT rate.rate, cur.name FROM res_currency cur INNER JOIN res_currency_rate rate ON  cur.id = rate.currency_id WHERE cur.name = 'USD'")
        res = self.cr.dictfetchall()
        return res

    def eur_rate(self):
        self.cr.execute("SELECT rate.rate, cur.name FROM res_currency cur INNER JOIN res_currency_rate rate ON  cur.id = rate.currency_id WHERE cur.name = 'EUR'")
        res = self.cr.dictfetchall()
        return res

    def debit(self, move_ids):
        debit = 0.0
        for move in move_ids:
            debit +=move.debit
        
        return debit

    def credit(self, move_ids):
        credit = 0.0
        for move in move_ids:
            credit +=move.credit
        
        return credit

report_sxw.report_sxw(
    'report.account.move.voucher.arabic',
    'account.move',
    'addons/account_arabic_reports/report/account_voucher_print.rml',
    parser=report_voucher_move,header="external"
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
