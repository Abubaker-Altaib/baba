# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from base_custom import amount_to_text_ar

class account_bank_letter(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(account_bank_letter, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'convert':self.convert,
            'set_context':self.set_context,
            'debitors':self._debitors,
        })

    def convert(self, amount, cur):
        return amount_to_text_ar.amount_to_text(amount, 'ar', cur)

    def _debitors(self, move):
        return str([line.account_id.code for line in move.line_id])[1:-1]

report_sxw.report_sxw('report.account.bank.transference.letter', 'account.move',
                      'addons/account_check_writing_custom/report/bank_Transference_letter_report.rml',
                      parser=account_bank_letter)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
