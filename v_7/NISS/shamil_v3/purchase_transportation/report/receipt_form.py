import time
from report import report_sxw
from osv import osv
import pooler

class receipt_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(receipt_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,

        })
report_sxw.report_sxw('report.receipt_form','transportation.order','purchase_transportation/report/receipt_form.rml',parser=receipt_form)

