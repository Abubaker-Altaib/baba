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


class specifections_letter(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(specifections_letter, self).__init__(cr, uid, name, context=context)


report_sxw.report_sxw('report.specifections_letter', 'purchase.clearance', 'purchase_clearance_niss/report/specifections_letter.rml', parser=specifections_letter,header=False)

