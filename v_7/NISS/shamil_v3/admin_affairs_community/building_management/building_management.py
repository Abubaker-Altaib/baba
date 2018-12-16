# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, orm
import openerp.tools
from openerp import netsvc
from openerp import tools

# ----------------------------------------------------
# Class building building
# ----------------------------------------------------
class building_building(orm.Model):
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _total_price(self, cr, uid, ids, field_name, arg, context={}):
        """ Finds the the total of price.
        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in record.item_ids:
                val += line.price_subtotal
            res[record.id] = val 
        return res

    def _building_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = "building.building"
    _parent_name = "parent_id"
    _parent_store = True
    _order = 'parent_left'

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'complete_name': fields.function(_building_name_get_fnc, type="char", string='Name'),
        'partner_id':fields.many2one('res.partner', 'Owner', select=True, ),
        'parent_id': fields.many2one('building.building', 'Parent Building'),
        'manager_id': fields.many2one('res.users', 'Building manager'),
        'address_id': fields.many2one('res.partner','Address'),
        'price': fields.function(_total_price, string='Price', required=True),    
        'child_ids': fields.one2many('building.building', 'parent_id', 'Child Buildings'),
        'item_ids':fields.one2many('building.item.line', 'building_id' , 'Items'), 
        'company_id': fields.many2one('res.company', 'Company', select=True, required=False),
        'note': fields.text('Note', size=256),
        #'type': fields.selection([('view','View'), ('normal','Normal')], 'Building Type',required=True, help="A category of the view type is a virtual building that can be used as the parent of another building to create a hierarchical structure."),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Image",
            help="This field holds the image used as image for the building, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'building.building': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of the building. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'building.building': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the building. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'building.building', context=c),
                }

    def _check_recursion(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from building_building where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You can not create recursive buildings.', ['parent_id'])
    ]

building_building()

#----------------------------------------
# Class item category
#----------------------------------------
class item_item(orm.Model):
    _name = "item.item"
    _description = 'Items'
    _columns = {
                'name': fields.char('Name', size=64,required=True ),
                'parent_id': fields.many2one('item.item', 'Parent Item', select=True),
                'code': fields.char('Code', select=1),
                'type': fields.selection([('view','View'), ('normal','Normal')], 'Type', required=True, help="An item of the view type is a virtual item that can be used as the parent of another item to create a hierarchical structure."),
               }
    _defaults = {
         'type' : 'normal',  
            }

    _sql_constraints = [
        ('code_uniqu', 'Unique (code)', 'The code must be unique')
    ]

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for item in self.browse(cr, uid, ids, context=context):
            item_name = item.code and '[' + item.code  + '] ' or ''
            item_name += item.name
            res.append((item.id,item_name))
        return res


# ----------------------------------------------------
# Class building item
# ----------------------------------------------------
class building_item(orm.Model):
    _name = "building.item.line"
    _description = 'building item'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price *line.qty or 0.0         
            res[line.id] = price
        return res
    
    _columns = {
                'name': fields.char('Desciription', size=64),
                'price': fields.float('Item Price', required=True),
                'qty': fields.float('Quantity', required=True),        
                'item_id': fields.many2one('item.item', 'Item', required=True),
                'building_id': fields.many2one('building.building', 'Building', required=True),
                'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
                'notes': fields.text('Notes', size=256), 
               }

    _defaults = {
         'price' : 1.0, 
         'qty' : 1.0,   
            }

    _sql_constraints = [
        ('item_unique', 'Unique (item_id,building_id)', 'The item must be unique per building'),
        ('price_check', 'Check (price > 0)', 'The item price must be greater than zero'),
        ('qty_check', 'Check (qty > 0 )', 'The item quantity must be greater than zero')

    ]

    def onchange_item_id(self, cr, uid, ids, item_id ):

        if not item_id:
            return {'value': {'name': '',}}
        item_name = self.pool.get('item.item').name_get(cr, uid, [item_id ] )[0][1]
        result = {'name':item_name,}
        return {'value': result}
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
