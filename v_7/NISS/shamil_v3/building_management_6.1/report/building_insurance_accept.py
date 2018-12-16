#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import re
import pooler
import wizard
from osv import fields, osv
import time
from report import report_sxw
from tools.translate import _


class building_insurance_accept(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(building_insurance_accept, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })


report_sxw.report_sxw('report.building_insurance_accept', 'building.insurance', 'addons/building_management/report/building_insurance_accept.rml' ,parser=building_insurance_accept , header=False)
