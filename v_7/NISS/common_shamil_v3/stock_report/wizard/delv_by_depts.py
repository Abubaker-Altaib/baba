# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm

class delv_by_depts(osv.osv_memory):
    _name = "delv.by.depts"
    _description = "Delivery by  departments"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location',required=True,domain = [('usage', '=', 'internal')]),
        'from_date': fields.datetime('From'), 
        'to_date': fields.datetime('To'), 
        'category_id': fields.many2one('product.category','Category',),
        'product_ids': fields.many2many('product.product', 'product_report_ids', 'report_id', 'product_id', 'Products',domain = [('type', '=', 'product')]),
 
   }     
    def print_report(self, cr, uid, ids, context=None):
        datas ={'form': self.read(cr, uid, ids, [])[0]}
 

        

        return {'type': 'ir.actions.report.xml','report_name': 'delv.by.depts', 'datas': datas}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
