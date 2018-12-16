# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from osv import osv

class delv_by_depts(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(delv_by_depts, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_location':self.get_location,
            'get_depts':self.get_depts,
 
        })

    def get_location(self,data):
        result = []
        location_obj = self.pool.get('stock.location')
        if data['form']['location_id']:
            location_id=data['form']['location_id'][0] 
             
            location_ids = [location_id]
        else :
            location_ids = location_obj.search(self.cr, self.uid, [])
        result = location_obj.browse(self.cr,self.uid, location_ids)
        return result

    def get_depts(self,data):
        result = []
        move_obj = self.pool.get('stock.move')
        dept_obj = self.pool.get('hr.department')
        moves=move_obj.search(self.cr, self.uid, [('state','=','done')])
        print "<<<<<<<<<<<<<<<<<<<<<",moves

        
        return result


    def _get_data(self,data,dept_id):

        all_data=[]
        self.cr.execute('''
                        SELECT c.product_qty AS qty ,p.name as name ,p.default_code as code  
                        FROM stock_move c 
                        LEFT JOIN product_template p ON (c.product_id=p.id)
 
                        LEFT JOIN product_product ppp ON (c.product_id=c.ppp.id)
                        where
                        c.state = 'done' ''')
        data=self.cr.dictfetchall() 
    
        print data,">>>>>>>>>>>>>>>>>>>>>"


report_sxw.report_sxw('report.stock.delv_by.depts','stock.picking','addons/stock_report/report/delv_by_depts.rml',parser=delv_by_depts)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
