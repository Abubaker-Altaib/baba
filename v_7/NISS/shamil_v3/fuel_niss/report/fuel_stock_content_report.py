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

class location_content(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(location_content, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process':self.process,
            'get_location':self.get_location,
            'get_cat':self.get_cat,
           
        })

    def get_location(self,location_id):  
           location_obj = pooler.get_pool(self.cr.dbname).get('stock.location')
           location_name = location_obj.read(self.cr, self.uid, [location_id],['name'])[0]['name']
           return location_name


    def get_cat(self,category_id):  
           cat_obj = pooler.get_pool(self.cr.dbname).get('product.category')
           cat_name = cat_obj.read(self.cr, self.uid, [category_id],['name'])[0]['name']
           return cat_name

    def process(self,data,location):
        type_obj = self.pool.get('product.category') 
        product_id = data['product_id'] and data['product_id'][0] or False
        location_id = location
        conditions = ""
        if product_id :
          conditions = conditions + " and p.id=(%s)"%product_id  
        if location_id :
          conditions = conditions + " and i.location_id=(%s)"%location_id    
        self.cr.execute("""
                SELECT
                      i.product_id,
                      sum(i.product_qty) AS product_qty,
                      min(p.default_code) AS default_code,
                      min(p.id) AS product_id,
                      min(t.categ_id) AS cat_id,
                      min(p.name_template) AS product_name,
                      cat.name as cat_name,
                      u.name as uom_name,
                      l.name AS location_name,
                      t.standard_price,
                      sum(t.standard_price*i.product_qty) as sum_price

                FROM
                      report_stock_inventory i
                      LEFT JOIN product_product p ON (i.product_id=p.id)
                      LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                      LEFT JOIN product_uom u ON (t.uom_id=u.id)
                      LEFT JOIN stock_location l ON (i.location_id=l.id) 
                      LEFT JOIN product_category cat ON (t.categ_id=cat.id)
                WHERE 
                      i.state='done' """ + conditions + """

                GROUP BY
                      product_id,u.name, p.default_code,l.name,t.standard_price , cat.name 
                ORDER BY 
                      p.default_code
        """) 
 
        res = self.cr.dictfetchall()
        count = 0
        for x in res:
            count += 1
            x['count'] = count

        '''if data['product_id']:
           res=[x for x in res if x['product_id']==data['product_id'][0]]
        res=[x for x in res if x['product_qty']!=0]'''
        return res
           

report_sxw.report_sxw('report.fuel_stock_content_report', 'stock.location', 'addons/fuel_niss/report/fuel_stock_content_report.rml', parser=location_content, header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

