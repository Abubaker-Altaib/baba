import time
from report import report_sxw
from osv import osv
import pooler

class goods_details(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(goods_details, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw('report.goods_details','purchase.contract','purchase_contracts/report/goods_details.rml',goods_details,header='internal landscape')

