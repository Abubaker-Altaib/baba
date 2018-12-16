#coding:utf-8
import time
from report import report_sxw

#******************** the new report **************
class purchase_picking_status(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(purchase_picking_status, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })
    def _getdata(self,data):
           date1 = data['form']['Date_from']
           date2 = data['form']['Date_to']
           state = data['form']['state']
           char='%'
           concat_char=':'
           test='%IN%'
           if not state :
               self.cr.execute("""
                SELECT   
                    pa.name as partner,
                    po.name as name,
                    po.date_order date,
                    p.invoice_state state,
                    inv.date_invoice inv_date
                FROM
                    stock_move m
                    left join stock_picking p on (p.id = m.picking_id and p.type = 'in')
                    left join purchase_order po on (p.purchase_id = po.id)
                    left join res_partner pa on (po.partner_id =pa.id)
                    left join account_invoice inv on (inv.origin like %s||p.name||%s||po.name||%s)
                WHERE
                    p.purchase_id IN (select id from purchase_order where state='done') and po.state like 'done' and p.invoice_state not in('none') and p.state in ('assigned','done') and (p.name like %s) and (to_char(po.date_order,'YYYY-mm-dd')>=%s and to_char(po.date_order,'YYYY-mm-dd')<=%s)
                GROUP BY 
                    pa.name , po.name ,po.date_order, p.invoice_state,inv.date_invoice
                ORDER BY 
                    po.name
                """,(char,concat_char,char,test,date1,date2))
           else:
               self.cr.execute("""
                SELECT   
                    pa.name as partner,
                    po.name as name,
                    po.date_order date,
                    p.invoice_state state,
                    inv.date_invoice inv_date
                FROM
                    stock_move m
                    left join stock_picking p on (p.id = m.picking_id and p.type = 'in')
                    left join purchase_order po on (p.purchase_id = po.id)
                    left join res_partner pa on (po.partner_id =pa.id)
                    left join account_invoice inv on (inv.origin like %s||p.name||%s||po.name||%s)
                WHERE
                    p.purchase_id IN (select id from purchase_order where state='done') and po.state like 'done' and p.invoice_state not in('none') and p.state in ('assigned','done') and (p.name like %s) and (to_char(po.date_order,'YYYY-mm-dd')>=%s and to_char(po.date_order,'YYYY-mm-dd')<=%s) and p.invoice_state = %s
                GROUP BY 
                    pa.name , po.name ,po.date_order, p.invoice_state,inv.date_invoice
                ORDER BY 
                    po.name
                """,(char,concat_char,char,test,date1,date2,state))

           result = self.cr.dictfetchall() 
           return result
report_sxw.report_sxw('report.po_status.report', 'purchase.order', 'addons/purchase_report/report/po_status.rml' ,parser=purchase_picking_status )
