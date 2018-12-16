# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime,date,timedelta
from report import report_sxw

class promotion_candidate_report(report_sxw.rml_parse):
    """ To manage vehicle report """

    def __init__(self, cr, uid, name, context):
        super(promotion_candidate_report, self).__init__(cr, uid, name, context)
        self.total = {'vehicle_ids':[]}
        self.page_break = {'count': 0}
        self.name = {'name':''}
        self.localcontext.update({
            'time': time,
            'page_break': self.get_page_break,
        })


    

    def get_page_break(self, data, i):
        if self.page_break['count'] == 11 and i == 11:
            self.page_break['count'] = 13
        elif self.page_break['count'] < 13:
            self.page_break['count'] += 1
        else:
            self.page_break['count'] = 0 

        return self.page_break


    

report_sxw.report_sxw('report.promotion_candidate_report','hr.employee','addons/hr_custom_military/report/promotion_candidate_report.mako',parser=promotion_candidate_report, header=True)
