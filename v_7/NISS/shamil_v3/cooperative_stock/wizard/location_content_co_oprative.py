# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm

class location_content(osv.osv_memory):
    _name = "location.content.cooprative"
    _description = "Location Content"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location',required=True,domain = [('usage', '=', 'internal')]),
        'report_type': fields.selection([('1','Location content'), ('3','physical Location quantity & price')],
                                        'Report Style', required=True , readonly=True),
        'order_by': fields.selection([('code','Code'),('prod_qty','Quantity'),('price','Price'),('prod_name','Name'),('price_value',' Price Value')], 'Order by', required=True),
        'order_type': fields.selection([('asc','Asc'),('desc','Desc')], 'Order Type', required=True ),
        'sale_categ_id': fields.many2one('sale.category', 'Sale Category',required=True ),
    }
    _defaults = {
            'report_type':'1',
            'order_by': 'code',
            'order_type': 'asc',
    }
    def print_report(self, cr, uid, ids, context=None):
        datas ={'form': self.read(cr, uid, ids, [])[0]}
        datas['form'].update({'report_type': datas['form']['report_type']})

        if datas['form']['report_type'] == '1':
                 return {'type': 'ir.actions.report.xml', 'report_name': 'location.content.cooprative', 'datas': datas}
#        elif datas['form']['report_type'] == '2':
 #                return {'type': 'ir.actions.report.xml', 'report_name': 'location.inventory.overview', 'datas': datas}

        return {'type': 'ir.actions.report.xml','report_name': 'location.overview', 'datas': datas}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
