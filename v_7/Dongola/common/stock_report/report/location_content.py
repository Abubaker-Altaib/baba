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
           
        })

    def get_location(self,location_id):  
           location_obj = pooler.get_pool(self.cr.dbname).get('stock.location')
           location_name = location_obj.read(self.cr, self.uid, [location_id],['name'])[0]['name']
           return location_name

    def process(self,location_id):
           
           self.cr.execute("""
                SELECT
                      i.product_id,
                      sum(i.product_qty) AS product_qty,
                      min(p.default_code) AS default_code,
                      min(p.name_template) AS product_name,
                      u.name as uom_name,
                      l.name AS location_name

                FROM
                      report_stock_inventory i
                      LEFT JOIN product_product p ON (i.product_id=p.id)
                      LEFT JOIN product_template t ON (p.product_tmpl_id=t.id)
                      LEFT JOIN product_uom u ON (t.uom_id=u.id)
                      LEFT JOIN stock_location l ON (i.location_id=l.id)
                WHERE 
                      i.location_id =%s and i.state='done'

                GROUP BY
                      product_id,u.name, p.default_code,l.name,t.standard_price 
                ORDER BY 
                      p.default_code
        """%location_id) 
           res = self.cr.dictfetchall()
           return res
           

report_sxw.report_sxw('report.location.content', 'stock.location', 'addons/stock_report/report/location_content.rml', parser=location_content)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

