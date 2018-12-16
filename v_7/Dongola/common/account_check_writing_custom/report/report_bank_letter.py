# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class account_bank_letter(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(account_bank_letter, self).__init__(cr, uid, name, context=context)

report_sxw.report_sxw('report.bank.letter', 'account.voucher', 
                      'addons/account_check_writing_custom/report/bank_letter.rml', 
                      parser=account_bank_letter)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
