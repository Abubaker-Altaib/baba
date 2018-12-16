# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

class product_prices(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(product_prices, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'test':self._getpp,
        })
    def _getpp(self,data):
        date1 = data['form']['Date_from']
        date2 = data['form']['Date_to']
        check1=0
        check2=0
        check3=0
        list1=[]
        list2=[]
        p=0
        self.cr.execute("""
select distinct
 product_id as pd_id ,name  as pd_name
from 
purchase_order_line where (to_char(create_date,'YYYY-mm-dd')>=%s and to_char(create_date,'YYYY-mm-dd')<=%s)
""",(date1,date2))
        res = self.cr.dictfetchall()
 
        for b in res :
            dic={
                'pd_id':b['pd_id'],
                'pd_name':b['pd_name'],
                }

            list1.append(dic)
        for b in list1:
            self.cr.execute("""
select distinct max(price_unit)as max from purchase_order_line 
where price_unit=(select max(price_unit)from purchase_order_line where product_id=%s)
group by price_unit
        """%b['pd_id'])
            res1 = self.cr.dictfetchall() 
            p=0
            if len(res1)>p:
               check1=res1[p]['max']
            else :
               check1=0
            self.cr.execute("""
select distinct min(price_unit)as min from purchase_order_line 
where price_unit=(select min(price_unit)from purchase_order_line where product_id=%s)
group by price_unit
        """%b['pd_id'])
            res2 = self.cr.dictfetchall() 

            if len(res2)>0:
               check2=res2[p]['min']
            else:
                check2=0
            self.cr.execute("""
 select price_unit as last from purchase_order_line where product_id=%s order by name,create_date desc """%b['pd_id'])
            res3 = self.cr.dictfetchall()
            if len(res2)>0:
               check3=res3[p]['last']
            else:
                check2=0
            dic1={
                'maxx':check1,
                'minn':check2,
                'lase_pr':check3,
                'avg':0,
                'pd_name':b['pd_name'],
                   }            
            list2.append(dic1)
            p+=1
        return list2
report_sxw.report_sxw('report.product_prices.report','purchase.order','addons/purchase/report/product_prices.rml',parser=product_prices)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
