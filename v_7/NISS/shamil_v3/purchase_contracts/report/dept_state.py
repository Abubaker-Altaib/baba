import time
from report import report_sxw
from osv import osv
import pooler

class dept_state(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(dept_state, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw('report.dept_state','purchase.contract','purchase_contracts/report/dept_state.rml',dept_state,header=False)

