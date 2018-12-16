# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm

class location_content(osv.osv_memory):
    _name = "location.content"
    _description = "Location Content"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location',required=True,domain = [('usage', '=', 'internal')]),
        'category_id': fields.many2one('product.category', 'category', ),
        'product_id': fields.many2one('product.product', 'product', ),
        'report_type': fields.selection([('1','Location content'), ('3','physical Location quantity & price')],
                                        'Report Style', required=True),
    }
    _defaults = {
            'report_type':'1',
    }
    def print_report(self, cr, uid, ids, context=None):
        datas ={'form': self.read(cr, uid, ids, [])[0]}
        datas['form'].update({'report_type': datas['form']['report_type']})

        if datas['form']['report_type'] == '1':
                 return {'type': 'ir.actions.report.xml', 'report_name': 'location.content', 'datas': datas}
#        elif datas['form']['report_type'] == '2':
 #                return {'type': 'ir.actions.report.xml', 'report_name': 'location.inventory.overview', 'datas': datas}

        return {'type': 'ir.actions.report.xml','report_name': 'location.overview', 'datas': datas}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
