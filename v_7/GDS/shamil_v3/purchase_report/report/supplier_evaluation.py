# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Suppliers Evaluation report         ----------------------------------------------------------------------------------------------------------------
class supplier_eval_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(supplier_eval_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })

    def _getdata(self,data):
        date1 = data['form']['from_date']
        date2 = data['form']['to_date']
        self.cr.execute("""
                select
                    min(r.name) as partner_name,
                    count(a.supplier_id) as quote_all,
                    count(b.supplier_id) as qoute_win,
                    (count(b.supplier_id)*100)/count(a.supplier_id) as quote_rate,
                    count(c.partner_id) as po_all,
                    count(d.partner_id) as po_done,
                    (count(d.partner_id)*100) / NULLIF(count(c.partner_id), 0.0) as po_rate
                from pur_quote a
                    left join ireq_m ir on (a.pq_ir_ref = ir.id)
                    left join res_partner r on (a.supplier_id=r.id)
                    left join pur_quote b on (a.id=b.id and a.state='done')
                    left join purchase_order c on (a.id=c.pq_id)
                    left join purchase_order d on (a.id=d.pq_id and d.state='done')

                where (a.supplier_id is not null) and ((to_char(ir.ir_date,'YYYY-mm-dd')>=%s and to_char(ir.ir_date,'YYYY-mm-dd')<=%s) ) 
                group by a.supplier_id,r.id
                order by quote_rate  DESC""",(date1,date2)) 
        res = self.cr.dictfetchall()
        return res
report_sxw.report_sxw('report.supplier_eval.report', 'purchase.order', 'addons/purchase_report/report/supplier_eval.rml' ,parser=supplier_eval_report ,header=False)
