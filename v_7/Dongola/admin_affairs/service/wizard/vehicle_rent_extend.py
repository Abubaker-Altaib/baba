 # -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv


class vehicle_rent_extend(osv.osv_memory):
    """ To manage vehicle rent contracts extend operation """
    _name = "vehicle.rent.extend"

    _description = "Extend vehicle contract"

    _columns = {
        'extend_date': fields.date('New Expiration Date', help='Date for replace the old contract expirates date with'),
        'con_id' : fields.many2one('fleet.vehicle.log.contract') ,
    }

    def extend_contract(self, cr, uid, ids, context=None):
        """ 
        Change expiration date field value by new date of expiration and return contract state to open.

        @return: Dictionary that close the wizard
        """
        obj = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('fleet.vehicle.log.contract').write(cr, uid, [context.get('con_id')], {'expiration_date':obj.extend_date,'state':'open'})
        return {'type': 'ir.actions.act_window_close'}

