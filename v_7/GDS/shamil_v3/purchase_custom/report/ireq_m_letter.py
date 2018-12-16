# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler

class ireq_m_letter(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ireq_m_letter, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw('report.ireq_m_letter','ireq.m','../purchase_custom/report/ireq_m_letter.rml',parser=ireq_m_letter)

