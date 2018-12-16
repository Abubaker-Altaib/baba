# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import re
import pooler
from report import report_sxw
import calendar
import datetime
import netsvc

class product_orderpoint(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(product_orderpoint, self).__init__(cr, uid, name, context=context)
        self.price_total = 0.0
        self.grand_total = 0.0
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line1':self._getdata1,
        })
    
    def _getdata1(self,data):  
           loc_id = data['form']['location_id'][0]  
           self.cr.execute("""
                select
                      min(l.name) AS location_name
                from
                      report_stock_inventory i
                      LEFT JOIN stock_location l ON (i.location_id=l.id)
                where 
                      i.location_id =%s

            """%loc_id) 
           res = self.cr.dictfetchall()
           return res

    def _getdata(self,data):
           loc_id = data['form']['location_id'][0]
           critical = data['form']['critical']
           maximum = data['form']['max']
           l = pooler.get_pool(self.cr.dbname).get('stock.location')
           loc=l.browse(self.cr, self.uid,loc_id)
           if (critical and maximum) or (not critical and not maximum):
               self.cr.execute("""
                           select
                    min(tbl.location_id) AS location_id ,
                    tbl.product_id,
                    min(product_qty) AS product_qty,
                    min(default_code) AS default_code,
                    min(product_name) AS product_name,
                    min(uom_name) AS uom_name,
                    min(product_minn_qty) AS product_minn_qty,
                    min(product_min_qty) AS product_min_qty,
                    min(product_max_qty) AS product_max_qty
           from
                (select
                      min(l.id) AS location_id,
                      i.product_id AS product_id,
                      sum(i.product_qty) AS product_qty,
                      min(p.default_code) AS default_code,
                      min(p.name_template) AS product_name,
                      u.name as uom_name
                from
                      report_stock_inventory i
                      LEFT JOIN product_product p ON (i.product_id=p.id)
                      LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                      LEFT JOIN product_uom u ON (t.uom_id=u.id)
                      LEFT JOIN stock_location l ON (i.location_id=l.id)
                where 
                      i.location_id =%s and i.state='done' and p.active= True

                group by
                      i.product_id,u.name, p.default_code,l.name)tbl
                      LEFT JOIN stock_warehouse_orderpoint s ON (s.product_id=tbl.product_id and s.location_id=tbl.location_id)
                                group by
                      tbl.product_id
                order by 
                      min(default_code)                 
            """%loc_id) 
               res = self.cr.dictfetchall()

           elif critical:
               self.cr.execute("""
                           select
                    min(tbl.location_id) AS location_id ,
                    tbl.product_id,
                    min(product_qty) AS product_qty,
                    min(default_code) AS default_code,
                    min(product_name) AS product_name,
                    min(uom_name) AS uom_name,
                    min(product_minn_qty) AS product_minn_qty,
                    min(product_min_qty) AS product_min_qty,
                    min(product_max_qty) AS product_max_qty
           from
                (select
                      min(l.id) AS location_id,
                      i.product_id AS product_id,
                      sum(i.product_qty) AS product_qty,
                      min(p.default_code) AS default_code,
                      min(p.name_template) AS product_name,
                      u.name as uom_name
                from
                      report_stock_inventory i
                      LEFT JOIN product_product p ON (i.product_id=p.id)
                      LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                      LEFT JOIN product_uom u ON (t.uom_id=u.id)
                      LEFT JOIN stock_location l ON (i.location_id=l.id)
                where 
                      i.location_id =%s and i.state='done' and p.active= True

                group by
                      i.product_id,u.name, p.default_code,l.name)tbl
                      LEFT JOIN stock_warehouse_orderpoint s ON (s.product_id=tbl.product_id and s.location_id=tbl.location_id)
                where
                      product_qty < product_minn_qty
                group by
                      tbl.product_id
                order by 
                      min(default_code)                 
          """%loc_id) 
               res = self.cr.dictfetchall()
           elif maximum:
               self.cr.execute("""
                           select
                    min(tbl.location_id) AS location_id ,
                    tbl.product_id,
                    min(product_qty) AS product_qty,
                    min(default_code) AS default_code,
                    min(product_name) AS product_name,
                    min(uom_name) AS uom_name,
                    min(product_minn_qty) AS product_minn_qty,
                    min(product_min_qty) AS product_min_qty,
                    min(product_max_qty) AS product_max_qty
           from
                (select
                      min(l.id) AS location_id,
                      i.product_id AS product_id,
                      sum(i.product_qty) AS product_qty,
                      min(p.default_code) AS default_code,
                      min(p.name_template) AS product_name,
                      u.name as uom_name
                from
                      report_stock_inventory i
                      LEFT JOIN product_product p ON (i.product_id=p.id)
                      LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                      LEFT JOIN product_uom u ON (t.uom_id=u.id)
                      LEFT JOIN stock_location l ON (i.location_id=l.id)
                where 
                      i.location_id =%s and i.state='done' and p.active= True

                group by
                      i.product_id,u.name, p.default_code,l.name)tbl
                      LEFT JOIN stock_warehouse_orderpoint s ON (s.product_id=tbl.product_id and s.location_id=tbl.location_id)
                where
                      product_qty > product_max_qty
                group by
                      tbl.product_id
                order by 
                      min(default_code)                 
            """%loc_id) 
               res = self.cr.dictfetchall()
          
           return res
report_sxw.report_sxw('report.product_orderpoint.reports', 'stock.location', 'addons/procurement_custom/report/product_order_point.rml', parser=product_orderpoint)
