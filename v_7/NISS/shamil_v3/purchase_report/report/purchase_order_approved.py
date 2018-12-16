# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

class Purchase_Order_approved_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Purchase_Order_approved_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self.get_order_number,
            'line3':self.get_amount,
        })
    def get_amount(self,data):
        date1 = data['form']['Date_from']
        date2 = data['form']['Date_to']
        state = data['form']['state']
        if not state:
            self.cr.execute("""SELECT sum(amount_total) AS amount From purchase_order where (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (state NOT IN ('cancel'))""",(date1,date2))
        else:
            self.cr.execute("""SELECT sum(amount_total) AS amount From purchase_order where (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (state =%s)""",(date1,date2,state))
        res = self.cr.dictfetchall()
        return res

    def get_order_number(self,data):
        date1 = data['form']['Date_from']
        date2 = data['form']['Date_to']
        state = data['form']['state']
        if not state:
            self.cr.execute("""SELECT count(name) AS order_n From purchase_order where (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (state NOT IN ('cancel')) """,(date1,date2))
        else:
            self.cr.execute("""SELECT count(name) AS order_n From purchase_order where (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (state =%s)""",(date1,date2,state))
        res = self.cr.dictfetchall()
        return res

    def _getdata(self,data):
           date1 = data['form']['Date_from']
           date2 = data['form']['Date_to']
           state = data['form']['state']
           if not state:
                self.cr.execute("""
                    select
                        pt.name as product_name,
                        pt.product_qty as qty ,
                        pt.price_unit pr,
                        rp.name as partner_name,
                        c.name as order_id,
                        c.date_order as date_order,
                        dt.name as dept
                    from purchase_order c
                    left join purchase_order_line pt on (c.id=pt.order_id)
                left join hr_department dt on (c.department_id=dt.id)
                        left join res_partner rp on (c.partner_id=rp.id)
                    where (to_char(c.date_order,'YYYY-mm-dd')>=%s and to_char(c.date_order,'YYYY-mm-dd')<=%s) and (c.state NOT IN ('cancel'))
            """,(date1,date2))
           else:
               self.cr.execute("""
                    select
                        pt.name as product_name,
                        pt.product_qty as qty ,
                        pt.price_unit pr,
                        rp.name as partner_name,
                        c.name as order_id,
                        c.date_order as date_order,
                        dt.name as dept
                        from purchase_order c
            left join purchase_order_line pt on (c.id=pt.order_id)
            left join hr_department dt on (c.department_id=dt.id)
                    left join res_partner rp on (c.partner_id=rp.id)
                where (to_char(c.date_order,'YYYY-mm-dd')>=%s and to_char(c.date_order,'YYYY-mm-dd')<=%s) and (c.state =%s)
                order by order_id
        """,(date1,date2,state)) 
           res = self.cr.dictfetchall()
           return res
report_sxw.report_sxw('report.Purchase_Order_approved.report', 'purchase.order', 'addons/purchase_report/report/Purchase_Order_approved.rml' ,parser=Purchase_Order_approved_report )
