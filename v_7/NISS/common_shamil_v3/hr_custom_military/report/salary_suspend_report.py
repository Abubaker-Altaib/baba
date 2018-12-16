
# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from dateutil.relativedelta import relativedelta


def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class salary_suspend(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(salary_suspend, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'to_arabic': self.get_arabic,
        })

    def get_arabic(self, st):
        st = st=='suspend' and 'إيقاف المرتب' or st=='resume' and 'فك المرتب' or st
        return st

report_sxw.report_sxw('report.salary_suspend_report', 'hr2.basic.salary.suspend.archive',
                      'addons/hr_custom_military/report/salary_suspend_report.rml', parser=salary_suspend, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
