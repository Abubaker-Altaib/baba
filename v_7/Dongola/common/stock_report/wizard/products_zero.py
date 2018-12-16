# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class products_zero(osv.osv_memory):
    _name = "products.zero"
    _description = "zero Products  "
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location',required=True,domain = [('usage', '=', 'internal')]),
        'categ_id': fields.many2one('product.category', 'Category',required=True),
        'from_qty': fields.float('From'),
        'to_qty': fields.float('To'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]

        datas = {
             'ids': [],
             'model': 'product.product',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'products_zero.reports',
            'datas': datas,
            }

products_zero()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:






