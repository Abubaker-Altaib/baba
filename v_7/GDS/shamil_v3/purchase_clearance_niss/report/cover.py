# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2016 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw
from osv import osv
import pooler
import string


class clearance_cover_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(clearance_cover_report, self).__init__(cr, uid, name, context=context)


report_sxw.report_sxw('report.clearance_cover_report', 'purchase.clearance', 'purchase_clearance_niss/report/cover.rml', parser=clearance_cover_report,header=False)

