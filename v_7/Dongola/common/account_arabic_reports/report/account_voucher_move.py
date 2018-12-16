# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from tools import amount_to_text_en

class report_voucher_move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_voucher_move, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert':self.convert,
            'get_title': self.get_title,
            'debit':self.debit,
            'credit':self.credit,
        })
        self.user = uid

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
            debit += move.debit
        return debit

    def credit(self, move_ids):
        credit = 0.0
        for move in move_ids:
            credit += move.credit
        return credit

report_sxw.report_sxw(
    'report.account.move.voucher',
    'account.move',
    'addons/account_arabic_reports/report/account_voucher_move.rml',
    parser=report_voucher_move, header="external"
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
