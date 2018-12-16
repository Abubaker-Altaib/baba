# coding: utf-8
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import re
import pooler
from osv import fields, osv
import time
from report import report_sxw


class car_maint_purchase(report_sxw.rml_parse):
    """ To manage car maintenance purchase report """

    def __init__(self, cr, uid, name, context):
        super(car_maint_purchase, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context

report_sxw.report_sxw('report.maint_purchase', 'fleet.vehicle',
                      'addons/service/report/car_maint_purchase.rml', parser=car_maint_purchase, header=False)
