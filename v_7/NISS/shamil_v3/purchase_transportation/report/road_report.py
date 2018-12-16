import time
from report import report_sxw
from osv import osv
import pooler

class road_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(road_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,

        })
report_sxw.report_sxw('report.road_report','transportation.order','purchase_transportation/report/road_report.rml',parser=road_report)

