import time
from report import report_sxw
from osv import osv
import pooler

class contract_report(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
          super(contract_report, self).__init__(cr, uid, name, context=context)
          self.localcontext.update({
            'time': time,
            'line' : self._getPremium,
            'line2' : self._getRemain,
            'line3' : self._getPayable,
        })
      def _getPremium(self,fees_ids):
          
          prem = 0
          for i in fees_ids:
              if i.state not in ['cancel','done'] :
                 prem = prem + 1
                 
          return prem
      def _getPayable(self,fees_ids):
          
          amount = 0
          for i in fees_ids:
              if i.state == 'done' :
                 amount = amount + i.fees_amount
                 
          return amount
      def _getRemain(self,contract_id):
          letter = '%'
          self.cr.execute("""select sum(inv.residual) as total 
      from contract_fees as f
           left join account_invoice inv on (inv.reference like %s||f.name||%s and inv.contract_id = %s)
           left outer join account_move am on (inv.move_id = am.id)
           left outer join account_move_line aml on (am.id = aml.move_id AND (aml.reconcile_id is not null or aml.reconcile_partial_id is not null))
           left outer join account_move_reconcile amr on (aml.reconcile_id = amr.id)
           left outer join account_move_line amll on (inv.move_id <> amll.move_id AND amll.reconcile_id = amr.id)
           where am.state <> 'reversed' and inv.residual < inv.amount_total """,(letter,letter,contract_id))
          res = self.cr.dictfetchall() 
          return res[0]['total']  

report_sxw.report_sxw('report.contract_report','purchase.contract','purchase_contracts/report/contract_report.rml',parser=contract_report,header=False)

