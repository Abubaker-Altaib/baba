# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm

class product_order_point(osv.osv_memory):
    _name = "product.order.point"
    _description = "Minimum Stock Rules"
    _columns = {
        'max': fields.boolean('Maximum only'), 
        'critical': fields.boolean('Critical only'), 
        'location_id': fields.many2one('stock.location', 'Location',required=True, domain = [('usage', '!=', 'view')] ),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'stock.location',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'product_orderpoint.reports',
            'datas': datas,
            }




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
