 # -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from fleet import fleet


class vehicle_rent_renew(osv.osv_memory):
    """
    To manage vehicle rent contracts renew operation
    """
    _name = "vehicle.rent.renew"

    _description = "Renew Vehicle Contract"

    _columns = {
        'date_from': fields.date('New Start Date', help='Date for replace the old contract start date with'),
        'date_to': fields.date('New Expiration Date', help='Date for replace the old contract expired date with'),
        'con_id' : fields.many2one('fleet.vehicle.log.contract') ,
    }

    def renew_contract(self, cr, uid, ids, context=None):
        """ 
        Duplicate contract with new expiration date and new start date,
        return contract state to open.

        @return: Dictionary that close the wizard
        """
        obj = self.browse(cr, uid, ids[0], context=context)
        con_obj = self.pool.get('fleet.vehicle.log.contract')
	partial_id = False
        for element in con_obj.browse(cr, uid, [context.get('con_id')], context=context):
	    if ((obj.date_to == False) or (obj.date_from == False)):
		raise osv.except_osv(_('ValidateError'), _('You Must Enter new start and end date!'))
            elif (element.expiration_date >= obj.date_from):
                raise osv.except_osv(_('ValidateError'), _('Renew Start Date Must Be Greater Than Old Expiration Date!'))
            default = {
                'date': datetime.datetime.now().strftime ("%m/%d/%Y"),
                'start_date': obj.date_from,
                'expiration_date': obj.date_to,
                'state': 'draft',
            }
            newid = super(fleet.fleet_vehicle_log_contract, con_obj).copy(cr, uid, element.id, default, context=context)
            con_obj.write(cr, uid, newid, {'state':'draft'}, context=context)
        mod, modid = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'service', 'fleet_vehicle_log_contract_form_custom')
        return {
            'name':_("Renew Contract"),
            'view_mode': 'form',
            'view_id': modid,
            'view_type': 'tree,form',
            'res_model': 'fleet.vehicle.log.contract',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': '[]',
            'res_id': newid,
            'context': {'active_id':newid}, 
        }    


