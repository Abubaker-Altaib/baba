# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# All Inventory report         ----------------------------------------------------------------------------------------------------------------
class all_inventory_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(all_inventory_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self._get_lines_data,
            'loc':self.get_location,
            'pro':self.get_product,
        })

    def get_location(self,data):
        self.cr.execute('SELECT name AS location From stock_location where id=%d'%(data['form']['location_id'][0]))
        res = self.cr.dictfetchall()
        return res

    def get_product(self,data, pro):
        self.cr.execute('SELECT name_template AS product From product_product where id=%s'%(pro))
        res = self.cr.dictfetchall()
        return res

    def _getdata(self,data):
        where = """ """
        if data['form']['state'] : where += """and state = '%s'"""%data['form']['state']
        self.cr.execute("""
                SELECT
 			id as id,
       			name as name,
       			date as date 
       			from stock_inventory 
			  where (to_char(date,'YYYY-mm-dd')>=%s and to_char(date,'YYYY-mm-dd')<=%s) 
			"""+where,(data['form']['Date_from'],data['form']['Date_to'])) 
        res = self.cr.dictfetchall()
        return res

    def _get_lines_data(self,data,record):
            #where_line = """ """
            #if data['form']['location_id'][0]: where_line += """and location_id = %d """%data['form']['location_id'][0]
            self.cr.execute("""
                  SELECT 
                        product_id as product, 
                        product_qty as qty 
                        from stock_inventory_line where inventory_id = %s
            """%record )
            res = self.cr.dictfetchall()
            return res 
     

report_sxw.report_sxw('report.all_inventory','stock.inventory','addons/cooperative_stock_inventory/report/summrize_stock_inventory.rml',parser=all_inventory_report )


