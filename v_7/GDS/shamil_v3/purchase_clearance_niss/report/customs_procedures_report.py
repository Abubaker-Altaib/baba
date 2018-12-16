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


class customs_procedures_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(customs_procedures_report, self).__init__(cr, uid, name, context=context)


report_sxw.report_sxw('report.customs_procedures_report', 'purchase.clearance', 'purchase_clearance_niss/report/customs_procedures_report.rml', parser=customs_procedures_report, header=False)

