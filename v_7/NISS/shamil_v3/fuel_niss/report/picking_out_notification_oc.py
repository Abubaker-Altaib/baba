#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from tools.translate import _
from osv import orm
import time

class picking_out_oc(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking_out_oc, self).__init__(cr, uid, name, context)
        self.localcontext.update({
        'time':time,
        'datas': self.get_data,
        })
        self.context = context



    def get_data(self,pick):
        res = []
        count = 0
        for line in pick.stock_fuel_id:
            count = count + 1
            dicts = {
                'count': count,
                'vehicle_id': line.vehicle_id.name,
                'product_id': line.product_id.name,
                'product_qty': line.product_qty,
                'location_id': line.location_id.name,
                'location_dest_id': line.location_dest_id.name,

            }
            res.append(dicts)


        return res


    
        
report_sxw.report_sxw('report.picking_out_notification_oc', 'stock.picking.out', 'fuel_niss/report/picking_out_notification_oc.rml' ,parser=picking_out_oc ,header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

