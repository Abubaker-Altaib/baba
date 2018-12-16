import time
from report import report_sxw
from osv import osv
import pooler

class payments_deptness(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(payments_deptness, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw('report.payment_deptness','purchase.contract','purchase_contracts/report/payment_deptness.rml',payments_deptness,header='internal landscape')

