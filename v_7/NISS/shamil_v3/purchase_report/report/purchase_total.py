# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# purchases total report
class purchase_total_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(purchase_total_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })
   
    def _getdata(self,data):
        product=data['form']['product']
        if not product: 
           self.cr.execute("""
                select
                    min(l.id) as id,
                    min(u.name) as uom_name,
                    min(l.name) as product_name,
                    sum(l.product_qty) as quantity,
                    count(*) as nbr,
                    (min(l.price_unit)*sum(l.product_qty))::decimal(16,2) as price_total
                from purchase_order s
                    left join purchase_order_line l on (s.id=l.order_id)
                        left join product_product p on (l.product_id=p.id)
                    left join product_uom u on (u.id=l.product_uom)
                where s.state='done'and 
                (to_char(s.date_approve,'YYYY-mm-dd')>=%s and to_char(s.date_approve,'YYYY-mm-dd')<=%s)
                group by
                    l.product_id 
             """,(data['form']['from_date'],data['form']['to_date']))
        else:
             self.cr.execute("""
                select
                    min(l.id) as id,
                    min(u.name) as uom_name,
                    min(l.name) as product_name,
                    sum(l.product_qty) as quantity,
                    count(*) as nbr,
                    (min(l.price_unit)*sum(l.product_qty))::decimal(16,2) as price_total
                from purchase_order s
                    left join purchase_order_line l on (s.id=l.order_id)
                        left join product_product p on (l.product_id=p.id)
                    left join product_uom u on (u.id=l.product_uom)
                where l.product_id is not null and s.state='done'and 
                (to_char(s.date_approve,'YYYY-mm-dd')>=%s and to_char(s.date_approve,'YYYY-mm-dd')<=%s)
                 and p.id = %s
                group by
                    l.product_id 
             """,(data['form']['from_date'],data['form']['to_date'],product[0]))
        res = self.cr.dictfetchall()
        return res
report_sxw.report_sxw('report.purchase_total.report', 'purchase.order', 'addons/purchase_report/report/purchase_total.rml' ,parser=purchase_total_report )

