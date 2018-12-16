# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import pooler
import time
from report import report_sxw

class products_zero(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(products_zero, self).__init__(cr, uid, name, context=context)
        self.price_total = 0.0
        self.grand_total = 0.0
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line1':self._getdata1,
            'line2':self._getdata2,
        })

    def _getdata2(self,data):
           loc_id = data['form']['location_id'][0]
           categ_id = data['form']['categ_id'][0]
           qty1 = int(data['form']['from_qty'])
           if qty1 <= 0 :
               self.cr.execute("""
             ( select  p.id,
                        p.default_code AS default_code,
                        p.name_template AS product_name,
                        u.name as uom_name
                 from
                      product_product p
                      LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                      LEFT JOIN product_uom u ON (t.uom_id=u.id)
                      LEFT JOIN product_category c ON (t.categ_id=c.id)
                where
                      c.id=%s and p.active= True
                order by 
                      p.default_code)                  
            EXCEPT
               ( select
                      i.product_id,
                      min(p.default_code) AS default_code,
                      min(p.name_template) AS product_name,
                      u.name as uom_name
                from
                      report_stock_inventory i
                      LEFT JOIN product_product p ON (i.product_id=p.id)
                      LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                      LEFT JOIN product_uom u ON (t.uom_id=u.id)
                      LEFT JOIN stock_location l ON (i.location_id=l.id)
                      LEFT JOIN product_category c ON (t.categ_id=c.id)

                where 
                      i.location_id =%s and i.state='done' and c.id=%s
                group by
                      product_id,u.name, p.default_code,l.name
                order by 
                      p.default_code)
             """,(categ_id,loc_id,categ_id)) 
           res = self.cr.dictfetchall()
           return res

    def _getdata1(self,data):  
           loc_id = data['form']['location_id'][0]  
           categ_id = data['form']['categ_id'][0]
           self.cr.execute("""
                select
                      min(l.name) AS location_name,min(c.name) AS categ_name
                from
                      product_category c, report_stock_inventory i
                      LEFT JOIN stock_location l ON (i.location_id=l.id)
                where 
                      i.location_id =%s and c.id =%s

            """,(loc_id,categ_id)) 
           res = self.cr.dictfetchall()
           return res

    def _getdata(self,data):
           loc_id = data['form']['location_id'][0]
           categ_id = data['form']['categ_id'][0]
           qty1 = int(data['form']['from_qty'])
           qty2 = int(data['form']['to_qty'])

           self.cr.execute("""
       select * from         
               (select
                      i.product_id,
                    sum(i.product_qty) AS product_qty,
                      min(p.default_code) AS default_code,
                      min(p.name_template) AS product_name,
                      u.name as uom_name,
                      l.name AS location_name
                from
                      report_stock_inventory i
                      LEFT JOIN product_product p ON (i.product_id=p.id)
                      LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                      LEFT JOIN product_uom u ON (t.uom_id=u.id)
                      LEFT JOIN stock_location l ON (i.location_id=l.id)
                      LEFT JOIN product_category c ON (t.categ_id=c.id)
                where 
                      i.location_id =%s and i.state='done' and p.active= True and c.id=%s
                group by
                      product_id,u.name, p.default_code,l.name
                order by 
                      p.default_code
                )tbl_qty where product_qty between %s and %s
        """,(loc_id,categ_id,qty1,qty2)) 
           res = self.cr.dictfetchall()
           return res
report_sxw.report_sxw('report.products_zero.reports', 'product.product', 'addons/stock_report/report/products_zero.rml', parser=products_zero)
