# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv


#----------------------------------------------------------
# Stock inventory  (Inherit)
#----------------------------------------------------------
class stock_inventory(osv.osv):
    _inherit = "stock.inventory"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    _columns = {
           'inventory_type' : fields.selection([('location','Location'),('custody','Custody'),('all','All')], 'Inventory Type', required=True, select=True, readonly=True ,states={'draft':[('readonly',False)]}),
           'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),

    }
    _defaults = {
        'inventory_type': 'location',
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }

stock_inventory()
#----------------------------------------------------------
# Stock inventory line (Inherit)
#----------------------------------------------------------
class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

    _defaults = {
        'product_id': False,
    }

    def on_change_product_id(self, cr, uid, ids, location_id, product,inventory_type, uom=False, to_date=False):
        result= super(stock_inventory_line, self).on_change_product_id(cr, uid, ids, location_id, product, uom=False, to_date=False)
        domain={'product_id':[('type','<>','service')]}
        if inventory_type == 'location':
            domain['product_id'].append(('asset', '=', False))
        if inventory_type == 'custody':
            domain['product_id'].append(('asset', '=', True))

        return {'value': result, 'domain': domain}

stock_inventory_line()

#----------------------------------------------------------
# Stock Piching in (Inherit)
#----------------------------------------------------------
class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    _columns = {
           'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),

    }
    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }

stock_picking_in()

#----------------------------------------------------------
# Stock Piching out (Inherit)
#----------------------------------------------------------
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    _columns = {
           'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
	       'department_id' : fields.many2one('hr.department','Department'),

    }
    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }

stock_picking_out()

#----------------------------------------------------------
# Stock Picking (Inherit)
#----------------------------------------------------------
class stock_picking(osv.Model):
    _inherit = "stock.picking"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    _columns = {
           'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
	       'department_id' : fields.many2one('hr.department','Department'),

    }
    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }

stock_picking()

# ----------------------------------------------------
# Product category inherit
# ----------------------------------------------------
class product_category(osv.osv):
    _inherit = "product.category"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    _columns = {
           'executing_agency':fields.selection(USERS_SELECTION, 'executing_agency', select=True , help='Select Department Which this user belongs to it'),
           'custody': fields.boolean('Custody'),
           #'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),

    }
    '''_defaults = {
       # 'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }'''

product_category()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
