from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import mute_logger
# Service Report Class

class location_wiz(osv.osv_memory):
    """ To manage services locations """
    _name = "fill.location"

    _description = "location wizard"

    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'recursive': fields.boolean("Include children",help="If checked, products contained in child locations of selected location will be included as well."),
    }

    def fill_inventory(self, cr, uid, ids, context=None):
        """ To Import stock inventory according to products available in the selected locations.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        inventory_line_obj = self.pool.get('stock.inventory.line')
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        if ids and len(ids):
            ids = ids[0]
        else:
             return {'type': 'ir.actions.act_window_close'}
        fill_inventory = self.browse(cr, uid, ids, context=context)
        res = {}
        res_location = {}

        if fill_inventory.recursive:
            location_ids = location_obj.search(cr, uid, [('location_id',
                             'child_of', [fill_inventory.location_id.id])], order="id",
                             context=context)
        else:
            location_ids = [fill_inventory.location_id.id]

        res = {}
        flag = False
        list_lines = []
        for location in location_ids:
            datas = {}
            res[location] = {}
            move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done')], context=context)
            local_context = dict(context)
            local_context['raise-exception'] = False
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                prod_id = move.product_id.id
                if move.location_dest_id.id != move.location_id.id:
                    if move.location_dest_id.id == location:
                        qty = uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)
                    else:
                        qty = -uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)


                    if datas.get(prod_id):
                        qty += datas[prod_id]['quantity']
                    
                    datas[prod_id] = {'product_id':prod_id,'quantity': qty,'amount':move.product_id.standard_price}
                    
                    

            if datas:
                flag = True
                res[location] = datas

        if not flag:
            raise osv.except_osv(_('Warning!'), _('No product in this location. Please select a location in the product form.'))

        list_lines = [(0,0,item) for item in datas.values()]

        contract_obj = self.pool.get('fleet.vehicle.log.contract')
        contract_obj.write(cr,uid,context['active_ids'][0],{'location_id':location,'cost_ids':None}) 
        lines_ids =  [item.id for item in contract_obj.browse(cr,uid,context['active_ids'][0],context).cost_ids]
        self.pool.get('fleet.vehicle.cost').unlink(cr,uid,lines_ids,context)
        contract_obj.write(cr,uid,context['active_ids'][0],{'cost_ids':list_lines}) 


        return {'type': 'ir.actions.act_window_close'}

location_wiz()
