# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################



from osv import fields, osv
import tools
import decimal_precision as dp

# ----------------------------------------------------
# Class building manager
# ----------------------------------------------------
class building_manager(osv.osv):
    
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
                val += line.price
            res[record.id] = val 
        return res

    def _building_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    CATEGORY_SELECTION = [
    ('building','Building'),
    ('station','Station'), 
    ]    


    _name = "building.manager"
    _columns = {
        'name': fields.char('Building Name', size=64, required=True),
        'complete_name': fields.function(_building_name_get_fnc, type="char", string='Name'),
        'manager_id':fields.many2one('res.users', 'Manager', select=True, required=False),
        'department_id': fields.many2one('hr.department','Department',select=True, required=False),        
        'parent_id': fields.many2one('building.manager', 'Parent Building', select=True),
        'address': fields.char('Address', size=128),
        'price': fields.function(_total_price, string='Price',digits_compute=dp.get_precision('Account'), required=True),    
        'child_ids': fields.one2many('building.manager', 'parent_id', 'Child Buildings'),
        'item_ids':fields.one2many('building.item', 'building_id' , 'Items'), 
        'company_id': fields.many2one('res.company', 'Company', select=True, required=False),
        'note': fields.text('Note', size=256),
        'building_category': fields.selection(CATEGORY_SELECTION,'Category', select=True),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'building.manager', context=c),
                }

    def _check_recursion(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from building_manager where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You can not create recursive buildings.', ['parent_id'])
    ]

building_manager()

#----------------------------------------
# Class item category
#----------------------------------------
class item_category(osv.osv):
    _name = "item.category"
    _description = 'Item category'
    _columns = {
                'name': fields.char('Name', size=64,required=True ),
               }
       
item_category()

# ----------------------------------------------------
# Class building item
# ----------------------------------------------------
class building_item(osv.osv):
    _name = "building.item"
    _description = 'building item'
    _columns = {
                'name': fields.char('Name', size=64, required=True),
                'price': fields.float('Price',digits_compute=dp.get_precision('Account'), required=True),
                'qty': fields.float('Qty',digits_compute=dp.get_precision('Account'), required=True),        
                'category_id': fields.many2one('item.category', 'Category', required=True),
                'building_id': fields.many2one('building.manager', 'Building', required=True),
                'notes': fields.text('Notes', size=256), 
               }
    
building_item()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
