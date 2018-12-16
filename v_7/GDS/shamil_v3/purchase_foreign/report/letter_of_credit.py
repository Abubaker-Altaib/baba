# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw
from openerp.osv import osv,fields
import pooler

class letter_of_credit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(letter_of_credit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw('report.letter_of_credit_report','purchase.letter.of.credit','purchase_foreign/report/letter_of_credit.rml',parser=letter_of_credit)












# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
