# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Purchases Statuses report 
class purchase_status_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(purchase_status_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })
    def _getdata(self,data):
           date1 = data['form']['from_date']
           date2 = data['form']['to_date'] 
           department= data['form']['department']
           if not department:
             self.cr.execute("""
                select
                    min(d.name) as department,
                    min(s.name) as name,
                    min(s.state) as state,
            CASE min(s.state) WHEN 'done' THEN 'تم'
                     WHEN 'approved' THEN 'تم تصديقه '
            END "state2" ,
                    min(s.date_approve) as date,
                    min(rp.name) as partner_name,
                    (sum(l.price_unit)*sum(l.product_qty)) as price_total
                from purchase_order s
                    left join res_partner rp on (s.partner_id=rp.id)
                    left join purchase_order_line l on (s.id=l.order_id)
                    left join hr_department d on (s.department_id=d.id)
                where s.state in ('done','approved') and 
                (to_char(s.date_approve,'YYYY-mm-dd')>=%s and to_char(s.date_approve,'YYYY-mm-dd')<=%s)
                group by
                    s.id
                order by min(s.date_approve)
               """,(date1,date2)) 
           else:
              self.cr.execute("""
                select
                    min(d.name) as department,
                    min(s.name) as name,
                    min(s.state) as state,
            CASE min(s.state) WHEN 'done' THEN 'تم'
                          WHEN 'approved' THEN 'تم تصديقه '
            END "state2" ,
                    min(s.date_approve) as date,
                    min(rp.name) as partner_name,
                    (sum(l.price_unit)*sum(l.product_qty)) as price_total
                from purchase_order s
                    left join res_partner rp on (s.partner_id=rp.id)
                    left join purchase_order_line l on (s.id=l.order_id)
                    left join hr_department d on (s.department_id=d.id)
                where s.state in ('done','approved') and 
                (to_char(s.date_approve,'YYYY-mm-dd')>=%s and to_char(s.date_approve,'YYYY-mm-dd')<=%s)
                and s.department_id = %s
                group by
                    s.id
                order by min(s.date_approve)
               """,(date1,date2,department[0] ))
           res = self.cr.dictfetchall()
           return res
report_sxw.report_sxw('report.purchase_status.report', 'purchase.order', 'addons/purchase_report/report/purchase_status.rml' ,parser=purchase_status_report )
