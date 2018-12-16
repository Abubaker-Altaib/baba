# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import pooler
from report import report_sxw

class exchange_report2(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(exchange_report2, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line1':self._getdata1,
        })
    def _getdata1(self,data):
        company_id = data['form']['company_id'][0]
        self.cr.execute("""
                select
                    name 
                from res_company
                where id = %s
               """%company_id) 
        res = self.cr.dictfetchall()
        return res

    def _getdata(self,data):
        date1 = data['form']['from_date']
        date2 = data['form']['to_date']
        company_id = data['form']['company_id'][0]
        self.cr.execute("""
               select 
                  (product_id),min(default_code)default_code,
                  min(name_template)name_template,sum(product_qty)product_qty,
                  sum(approved_qty)approved_qty,sum(delivered_qty)delivered_qty,sum(send_qty)send_qty,
                  min(uom_name)uom_name
               from (
                  select
                      (l.product_id)product_id,(p.default_code)default_code,
                      (p.name_template)name_template,(l.product_qty)product_qty,
                      (l.approved_qty)approved_qty,(l.delivered_qty)delivered_qty,
                      (u.name) uom_name,
                      (select sum(product_qty) from stock_move m where m.exchange_line_id = l.id and m.state = 'done' and m.company_id = 16)send_qty
                 from
                      exchange_order e
                      LEFT JOIN exchange_order_line l ON (e.id=l.order_id) 
                      LEFT JOIN product_product p ON (l.product_id =p.id)
                      LEFT JOIN product_uom u on (u.id=l.product_uom)       
                 where
                      e.ttype = 'store' and e.company_id  = %s and 
                      (to_char(e.date_order,'YYYY-mm-dd')>=%s and to_char(e.date_order,'YYYY-mm-dd')<=%s)
   
                 order by 
                    p.default_code
  )tbl
         group by product_id
       order by default_code   
        """,(company_id,date1,date2)) 
        res = self.cr.dictfetchall()
        return res
report_sxw.report_sxw('report.exchange_report.reports', 'exchange.order', 'addons/stock_exchange/report/exchange_report.rml', parser=exchange_report2)
