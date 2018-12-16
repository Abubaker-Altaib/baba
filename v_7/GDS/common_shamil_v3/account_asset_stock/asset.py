# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields
from openerp.tools.translate import _

#----------------------------------------------------------
# Asset_Asset (Inherit)
#----------------------------------------------------------
class account_asset_asset(osv.Model):
    
    STATE_SELECTION = [
		('draft', 'New'),
		('released', 'Released'),
		('assigned', 'Assigned'),
        ('damage', 'Damage'),
	   ]	

    _inherit = "account.asset.asset"

    _columns = {
        'product_id': fields.many2one('product.product','Product', readonly=True),
        'stock_location_id': fields.many2one('stock.location','Stock Location', readonly=True),
        'asset_log_ids': fields.one2many('asset.log','asset_id','Asset Logs'),
        'asset_rel_ids': fields.one2many('asset.rel','asset_id','Asset Related'),
        'picking_id': fields.many2one('stock.picking','Stock Order'),
        'user_id': fields.many2one('res.users','Responsible'),
        'serial': fields.char('Serial Number', size=256),
        'state_rm': fields.selection(STATE_SELECTION, 'State',  select=True),
        
    }

    _defaults = {
        'state_rm': 'draft',
        'user_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).id,
        #'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'fuel.plan', context=c),
    }
    _sql_constraints = [
        ('name_unique', 'unique(serial)', 'you can not create same name !')
    ]

    '''def check_serial_unique(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            idss = self.search(cr,uid, [('serial', '=', rec.serial),('id','!=',rec.id),
                                        ('product_id','=',rec.product_id.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This serial is already exist'))
        return True

    _constraints = [
         (check_serial_unique, '', []),
    ]'''


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        ids = []
        if context and 'picking_out_assets' and 'picking_id' in context:
            picking_rec = self.pool.get('stock.picking').browse(cr, uid, context['picking_id'])
            for line in picking_rec.picking_out_assets:
                ids.append(line.asset_id.id)

            for asset_line in context['picking_out_assets']:
                if asset_line[2] and asset_line[2]['asset_id']: 
                    ids.append(asset_line[2]['asset_id'])
            args.append(('id', 'not in', ids))

        return super(account_asset_asset, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)



#----------------------------------------------------------
# Asset_log
#----------------------------------------------------------
class asset_log(osv.Model):

    _name = "asset.log"

    _columns = {
        'date': fields.date('Date'),
        'picking_id': fields.many2one('stock.picking','Stock Order'),
        'department_id': fields.many2one('hr.department','Department'),
        'employee_id': fields.many2one('hr.employee','Employee'),
        'state': fields.selection([('purchase','Purchase'),('released','Released'),
                                   ('added','Added'),('recieved','Recieved'),
                                   ('damage','Damage')], 'Status'),
        'asset_id': fields.many2one('account.asset.asset', 'Custody'),
        'office_id': fields.many2one('office.office', string='office'),
    }


class asset_rel(osv.Model):

    _name = "asset.rel"

    _columns = {
 
        'product_id': fields.many2one('product.product',' Product'),
        'asset_id': fields.many2one('account.asset.asset', 'Custody'),
        'serial': fields.char('Serial Number', size=256),
        'asset_id': fields.many2one('account.asset.asset', 'Custody'),
 
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
