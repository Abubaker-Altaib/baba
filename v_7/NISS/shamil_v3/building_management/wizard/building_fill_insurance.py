# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, orm
from tools.translate import _

#----------------------------------------
# Class building fill insurance
#----------------------------------------
class building_fill_insurance(orm.TransientModel):
    """
    To manage building fill insurance """

    _name = "building.fill.insurance"
    _description = "Import Insurance"
    _columns = {
        'building_id': fields.many2one('building.building', 'Building', required=True),
        'recursive': fields.boolean("Include children",help="If checked, items contained in child buildings of selected building will be included as well."),
    }
    def view_init(self, cr, uid, fields_list, context=None):
        """
        Creates view dynamically and adding fields at runtime.

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
        """ 
        To Import items according to building available in the selected buildings.

        @param context: A standard dictionary
        @return: Action
        """
        if context is None:
            context = {}
            
        building_obj = self.pool.get('building.building')
        item_line_obj = self.pool.get('building.item.line')
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

        for building_id in building_ids:
            item_line_ids = item_line_obj.search(cr, uid, [('building_id','=', building_id)], order="building_id", context=context)
            #if not item_line_ids:
                #raise osv.except_osv(_('Warning !'), _('No items in this building.'))
            insurance_line_dict = {}
            for line in item_line_obj.browse(cr, uid, item_line_ids, context):

                insurance_line_dict.update({'insurance_id': context['active_ids'][0] ,
                                            'building_id': building_id,
                                            'item_id': line.item_id.id,
                                            'qty': line.qty,
                                            'price': line.price,
                                            'cost': line.qty * line.price,
                                            })

                insurance_line_obj.create(cr, uid, insurance_line_dict, context=context)

        return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
