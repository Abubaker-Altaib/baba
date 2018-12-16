# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _

#----------------------------------------
# Class building fill insurance
#----------------------------------------
class building_fill_insurance(osv.osv_memory):
    _name = "building.fill.insurance"
    _description = "Import Insurance"
    _columns = {
        'building_id': fields.many2one('building.manager', 'Building', required=True),
        'recursive': fields.boolean("Include children",help="If checked, items contained in child buildings of selected building will be included as well."),
        'set_cost_zero': fields.boolean("Set cost to zero",help="If checked, all items cost will be set to zero."),
    }
    def view_init(self, cr, uid, fields_list, context=None):
        """
         Creates view dynamically and adding fields at runtime.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view with new columns.
        """
        if context is None:
            context = {}
        super(building_fill_insurance, self).view_init(cr, uid, fields_list, context=context)

        if len(context.get('active_ids',[])) > 1:
            raise osv.except_osv(_('Error!'), _('You cannot perform this operation on more than one building.'))

        if context.get('active_id', False):
            insurance = self.pool.get('building.insurance').browse(cr, uid, context.get('active_id', False))

            if insurance.state in ('confirmed','done'):
                raise osv.except_osv(_('Warning!'), _('Building insurance is already confirmed.'))
        return True

    def fill_insurance(self, cr, uid, ids, context=None):
        """ To Import items according to building available in the selected buildings.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
            
        building_obj = self.pool.get('building.manager')
        item_obj = self.pool.get('building.item')
        insurance_line_obj = self.pool.get('building.insurance.line')
        if ids and len(ids):
            ids = ids[0]
        else:
            return {'type': 'ir.actions.act_window_close'}
        fill_insurance = self.browse(cr, uid, ids, context=context)

        if fill_insurance.recursive:
            building_ids = building_obj.search(cr, uid, [('parent_id',
                             'child_of', [fill_insurance.building_id.id])], order="id",
                             context=context)
        else:
            building_ids = [fill_insurance.building_id.id]


        item_ids = item_obj.search(cr, uid, [('building_id','in', building_ids)], order="building_id", context=context)
        if not item_ids:
            raise osv.except_osv(_('Warning !'), _('No items in this building.'))
        insurance_line_dict = {}
        for item in item_obj.browse(cr, uid, item_ids, context):

            insurance_line_dict.update({'insurance_id': context['active_ids'][0] ,'item_id': item.id})

            if fill_insurance.set_cost_zero:
                insurance_line_dict.update({'cost': 0})
            else:
                insurance_line_dict.update({'cost': item.price})

            insurance_line_obj.create(cr, uid, insurance_line_dict, context=context)

        return {'type': 'ir.actions.act_window_close'}

building_fill_insurance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
