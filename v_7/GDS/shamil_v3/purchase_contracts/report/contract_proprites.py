import time
from report import report_sxw
from osv import osv
import pooler

class contract_proprites(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
          super(contract_proprites, self).__init__(cr, uid, name, context=context)
          self.localcontext.update({
            'time': time,
           
            
        })
      



report_sxw.report_sxw('report.contract_proprites','purchase.contract','purchase_contracts/report/contract_proprites.rml',parser=contract_proprites,header=False)

