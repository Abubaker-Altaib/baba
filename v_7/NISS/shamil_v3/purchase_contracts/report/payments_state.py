import time
from report import report_sxw
from osv import osv
import pooler

class payments_state(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(payments_state, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'line' : self._getdata,
            'line2' : self._getmonth,
        })
      def _getdata(self,data):
          from_date = data['form']['from_date']
          to_date   = data['form']['to_date']
          self.cr.execute(""" select pc.contract_title as title , part.name as partner,cur.name as currency, fc.fees_amount as amount, fc.fees_amount_in_euro as euro,inv.name as invoive
                              from purchase_contract as pc ,
                                   contract_fees as fc ,
                                   res_partner as part ,
                                   account_invoice as inv ,
                                   res_currency as cur 
                              where (pc.partner_id = part.id) and (pc.currency_id = cur.id) and (fc.contract_id = pc.id) and (inv.reference = pc.name) and ((to_char(pc.contract_date,'YYYY-mm-dd')>=%s and to_char(pc.contract_date,'YYYY-mm-dd')<=%s)  )""",(from_date,to_date))
          res = self.cr.dictfetchall() 
          return res
      def _getmonth(self,data):
          from_date = data['form']['from_date']
          to_date   = data['form']['to_date']
          self.cr.execute(""" select fc.month as month
                              from 
                                   contract_fees as fc , purchase_contract pc
                              where (fc.contract_id = pc.id) and ((to_char(pc.contract_date,'YYYY-mm-dd')>=%s and to_char(pc.contract_date,'YYYY-mm-dd')<=%s)  ) group by fc.month""",(from_date,to_date))
          res = self.cr.dictfetchall() 
          return res
           
report_sxw.report_sxw('report.payments_state','purchase.contract','purchase_contracts/report/payments_state.rml',payments_state,header=False)

