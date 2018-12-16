# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv
class asset_location_product(osv.osv_memory):
    _name = "asset.location.product2"
    _description = "Products by Location"
    _columns = {
        'from_date': fields.datetime('From'), 
        'to_date': fields.datetime('To'), 
        'location_id': fields.many2one('stock.location', 'Location',required=True ,domain = [('usage', '=', 'internal')]),
        'recursive': fields.boolean("Include children",help="If checked, products contained in child locations of selected location will be included as well."),
        'move': fields.selection([('moved', 'Moved Only'), ('notmoved', 'Not Moved Only'), ('all', 'All')], 'Move', required=True),
        'category_id': fields.many2one('product.category','Category',),
        'product_ids': fields.many2many('product.product', 'product_report_ids', 'report_id', 'product_id', 'Products',domain = [('type', '=', 'product')]),
        'type': fields.selection([('incoming', 'Incoming'), ('outcoming', 'Outcoming'), ('all', 'All')], 'Type', required=True),
        'department_id': fields.many2one('hr.department','Department',),
    }
    _defaults = {
        'move': 'moved',
        'type' : 'outcoming',
    }
    def onchange_category_id(self, cr, uid, ids, category_id):
        domain = {'product_ids':[('type', '=', 'product')]}
        if category_id:
            domain = {'product_ids':[('categ_id', 'child_of', category_id)]}
        return {'value': {'product_ids':False} ,'domain': domain}

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        product_ids = self.pool.get('product.product').search(cr, uid, [('asset', '=', True),('type', '=', 'product')], context={'active_test': False})
        if data['category_id']:
            product_ids = self.pool.get('product.product').search(cr, uid, [('type', '=', 'product'),('asset', '=', True),('categ_id', 'child_of', data['category_id'][0])], context={'active_test': False})

        # GET DEPARTMENT CHILDS
        department_ids=[]
        if data['department_id']:
            department_ids= self.pool.get('hr.department').search(cr, uid, [('id', 'child_of', data['department_id'][0])], context={'active_test': False})
        
 
        if data['product_ids']:
            product_ids=data['product_ids']
        context={
            'from_date':data['from_date'],
            'to_date': data['to_date'],
            'department_id': department_ids,
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
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'asset.location.product',
            'datas': datas,
            }
asset_location_product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
