#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from tools.translate import _
from osv import osv,orm
import time

class fuel_request(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fuel_request, self).__init__(cr, uid, name, context)
        self.localcontext.update({
        'time':time,
        'datas': self.get_data,
        })
        self.context = context



    def get_data(self,picks):
        for pick in picks:
            if pick.stock_in_type != 'claim':
                raise osv.except_osv(_(''), _("Fuel must be claim Type "))
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
        


        return picks


    
        
report_sxw.report_sxw('report.fuel_request', 'stock.picking.in', 'fuel_niss/report/fuel_request.rml' ,parser=fuel_request ,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

