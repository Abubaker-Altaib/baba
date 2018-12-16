# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
###############################################################################

from openerp.osv import fields, osv

class res_company(osv.osv):
    _inherit = "res.company"

    _columns = {
            'stock_journal_id': fields.many2one('account.journal', 'Stock Journal', domain=[('type','=','general')]),
            'property_stock_inventory': fields.many2one('stock.location', 'Inventory Location'),
            'backorder': fields.boolean('Back Order', help=" Does not generate a  backorder."),
    }
    _defaults = {
        'backorder': False,
    }
class stock_config_settings(osv.osv_memory):

    _inherit = 'stock.config.settings'

    _columns = {
          'company_id': fields.many2one('res.company', 'Company'),
          'stock_journal_id': fields.related('company_id', 'stock_journal_id', type='many2one', 
                                             relation='account.journal', string='Stock Journal'),
          'property_stock_inventory': fields.related('company_id', 'property_stock_inventory', required=True, 
                                                     type='many2one', relation='stock.location', string='Inventory Location'),
          'backorder': fields.related('company_id','backorder',type='boolean',string='Back Order',  help=" Does not generate a  backorder."),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid, context=ctx).company_id.id,
        'backorder': False,
    }

    def create(self, cr, uid, values, context=None):
        id = super(stock_config_settings, self).create(cr, uid, values, context)
        # Hack: to avoid some nasty bug, related fields are not written upon record creation.
        # Hence we write on those fields here.
        vals = {}
        print values
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [id], vals, context)
        property_pool = self.pool.get('ir.property')
        fields_id = self.pool.get('ir.model.fields').search(cr, uid, [('model','=','product.template'),('name','=','property_stock_inventory')], context=context)
        default = property_pool.search(cr, uid, [('fields_id','=',fields_id and fields_id[0]),('res_id','=',False),('company_id','=',values.get('company_id',False))], context=context)
        property_pool.unlink(cr, uid, default, context=context)
        property_pool.create(cr, uid, {"name":'property_stock_inventory', "fields_id":fields_id and fields_id[0], 'company_id': values.get('company_id',False),
                                                      "value":'stock.location,'+str(vals.get('property_stock_inventory',''))}, context=context)
        return id

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        # update related fields
        inv_location = False
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            inv_location = company.property_stock_inventory
        if not inv_location:
            property_pool = self.pool.get('ir.property')
            fields_id = self.pool.get('ir.model.fields').search(cr, uid, [('model','=','product.template'),('name','=','property_stock_inventory')], context=context)
            default = property_pool.search(cr, uid, [('fields_id','=',fields_id and fields_id[0]),('res_id','=',False),('company_id','=',False)], context=context)
            inv_location = default and property_pool.browse(cr, uid, default, context=context)[0].value_reference
        return {'value': {
            'stock_journal_id': company_id and company.stock_journal_id.id,
            'property_stock_inventory': inv_location and inv_location.id,
            'backorder':company and company.backorder,
        }}
