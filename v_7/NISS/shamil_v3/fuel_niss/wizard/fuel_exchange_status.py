# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from tools.translate import _

class fuel_exchange_status_archive(osv.osv):
    """ To manage Fuel Exchange Status archive """

    _name = "fuel_exchange_status_archive"

    def _get_amount(self, cr, uid, ids, name, attr, context=None):
        res = {}

        for line in self.browse(cr, uid, ids, context=context):
            #if not line.vehicle_id.fuel_amount_id:
            #    print "________________",line.vehicle_id.fuel_amount_id
            #    line.vehicle_id.write({'fuel_amount_id':False})
            if line.vehicle_id.fuel_amount_id:
                print ".................",line.vehicle_id.fuel_amount_id.fuel_amount
                #res[line.id] = line.vehicle_id.fuel_amount_id.fuel_amount
            
        return res

    _columns = {
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'fuel_exchange_status': fields.selection([('exchange','Currently Disbursed'),('stop','Stopped')], 'Fuel Exchange Status'),
        'fuel_stop_reason_id': fields.many2one('fuel.stop.reasons', 'Fuel Stopped Reason'),
        'date': fields.date('Date'),
        'details':fields.text('Details'),

        'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      string='Fuel Type', help='Fuel Used by the vehicle', readonly=True),

        'use': fields.related('vehicle_id', 'use',  type='many2one',  string='Vehicle Use', readonly=True, relation='fleet.vehicle.use'),
        'fuel_amount': fields.float(string="Fuel amount"),


    }


class fuel_exchange_status(osv.osv_memory):
    """ To manage Fuel Exchange Status wizard """

    _name = "fuel_exchange_status_wizard"

    _columns = {
        'vehicles_ids': fields.many2many('fleet.vehicle', string='Vehicles'),
        'fuel_exchange_status': fields.selection([('exchange','Currently Disbursed'),('stop','Stopped')], 'Fuel Exchange Status'),
        'fuel_stop_reason_id': fields.many2one('fuel.stop.reasons', 'Fuel Stopped Reason'),
        'date': fields.date('Date'),
        'details':fields.text('Details'),
    }

    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
    }

    def process(self, cr, uid, ids, context=None):
        '''
            to stop or resume the fuel for a vehicle
        '''
        for rec in self.browse(cr, uid, ids, context=context):
            arch_obj = self.pool.get('fuel_exchange_status_archive')
            for vehicle_id in rec.vehicles_ids:
                if vehicle_id.fuel_exchange_status == rec.fuel_exchange_status:
                    raise osv.except_osv(_(''), _('can not change fuel exchange status to the previous'))
                new_id = arch_obj.create(cr, uid,{
                'vehicle_id': vehicle_id.id,
                'fuel_exchange_status': rec.fuel_exchange_status,
                'fuel_stop_reason_id': rec.fuel_stop_reason_id and rec.fuel_stop_reason_id.id or False,
                'date': rec.date,
                'details':rec.details,
                'fuel_type': vehicle_id.fuel_type,
                }, context=context)
                vehicle_id.write({
                'fuel_exchange_status': rec.fuel_exchange_status,
                'fuel_stop_reason_id': rec.fuel_stop_reason_id and rec.fuel_stop_reason_id.id or False,
                })
                arch_obj.write(cr, uid, [new_id], {'fuel_amount':vehicle_id.fuel_amount_id and vehicle_id.fuel_amount_id.fuel_amount or 0.0})


