# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class fuel_location_product(osv.osv_memory):
    _name = "fuel.location.product"
    _description = "Products by Location"
    _columns = {
        'from_date': fields.datetime('From'), 
        'to_date': fields.datetime('To'), 
        'location_id': fields.many2one('stock.location', 'Location'),
        'move': fields.selection([('moved', 'Moved Only'), ('notmoved', 'Not Moved Only'), ('all', 'All')], 'Move', required=True),
    }
    _defaults = {
        'move': 'moved',
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        u = self.pool.get('res.users').browse(cr, uid,uid).company_id.id
        product_ids = self.pool.get('product.product').search(cr, uid, [('fuel_ok', '=', 'true'),('company_id', '=', u)], context={'active_test': False})
        context={
            'from_date':data['from_date'],
            'to_date': data['to_date'],
            'move':data['move'],
            'compute_child':False,
            'currency_id':self.pool.get('res.users').browse(cr, uid, uid,context=context).company_id.currency_id.id
        }

        datas = {
             'ids': [],
             'model': 'product.product',
             'form': data,
             'product_ids': product_ids,
             'context':context
            }
        print ",,,,,,,,,,,,,,,,,,,,,",datas
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fuel.location.product',
            'datas': datas,
            }

fuel_location_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
