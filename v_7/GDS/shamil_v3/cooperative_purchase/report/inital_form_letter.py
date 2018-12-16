import time
from report import report_sxw
from osv import osv
import pooler





class inital_form_letter(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(inital_form_letter, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,

        })
    

report_sxw.report_sxw('report.inital_form_letter','purchase.contract','cooperative_purchase/report/inital_form_letter.rml',parser=inital_form_letter,header=False)

