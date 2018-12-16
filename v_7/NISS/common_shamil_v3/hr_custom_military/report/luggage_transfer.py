import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from dateutil.relativedelta import relativedelta


def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class luggage_transfer(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(luggage_transfer, self).__init__(cr, uid, name, context)
        self.localcontext.update({
        })

report_sxw.report_sxw('report.luggage_transfer', 'luggage.transfer',
                      'addons/hr_custom_military/report/luggage_transfer.rml', parser=luggage_transfer, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
