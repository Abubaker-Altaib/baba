# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from tools.translate import _
from datetime import datetime

class fleet_vehicles(osv.osv):
    """ To manage fleet vehicles """
    def _selection_year(self, cr, uid, context=None):
        """
        Select car manufacturing year between 1970 and Current year.

        @return: list of years 
        """
        return [(str(years),years) for years in range(int(datetime.now().year)+1,1970,-1)]

    def _get_odometer(self, cr, uid, ids, odometer_id, arg, context):
        """
        Select odometer value.

        @param odometer_id: id of odometer
        @param arg: extra argument
        @return: dictionary of odometer value 
        """
        res = dict.fromkeys(ids, 0)
        for record in self.browse(cr,uid,ids,context=context):
            ids = self.pool.get('fleet.vehicle.odometer').search(cr, uid, [('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if len(ids) > 0:
                res[record.id] = self.pool.get('fleet.vehicle.odometer').browse(cr, uid, ids[0], context=context).value
        return res

    def _set_odometer(self, cr, uid, id, name, value, args=None, context=None):
        """
        Set odometer value.

        @param value: value to set on odometer
        @param arg: extra argument
        @return: dictionary of odometer value 
        """
        if value:
            date = fields.date.context_today(self, cr, uid, context=context)
            data = {'value': value, 'date': date, 'vehicle_id': id}
            return self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)

    _inherit = "fleet.vehicle"

    _columns = {
        'model_id': fields.many2one('fleet.vehicle.model', 'Model', required=True,readonly=True, help='Model of the vehicle', 
                                    states={'draft':[('readonly',False)]}),
        'license_plate': fields.char('License Plate', size=32,readonly=True, states={'draft':[('readonly',False)]},
                                      required=True, help='License plate number of the vehicle (ie: plate number for a car)'),
        'tag_ids' :fields.many2many('fleet.vehicle.tag', 'fleet_vehicle_vehicle_tag_rel', 'vehicle_tag_id','tag_id', 
                                    'Tags',readonly=True,states={'draft':[('readonly',False)]}),
        'driver_id': fields.many2one('res.partner', 'Driver', help='Driver Of The Vehicle',readonly=True, 
                                     states={'draft':[('readonly',False)]}),
        'location': fields.char('Location', size=128, help='Location of the vehicle (garage, ...)',readonly=True,
                                states={'draft':[('readonly',False)]}),
        'vin_sn': fields.char('Chassis Number', size=32, help='Unique number written on the vehicle motor (VIN/SN number)',readonly=True,
                              states={'draft':[('readonly',False)]}),
        'acquisition_date': fields.date('Acquisition Date', required=False,readonly=True, help='Date when the vehicle has been bought',
                                        states={'draft':[('readonly',False)]}),
        'car_value': fields.float('Car Value', help='Value of the bought vehicle',readonly=True,states={'draft':[('readonly',False)]}),
        'odometer_unit': fields.selection([('kilometers', 'Kilometers'),('miles','Miles')], 'Odometer Unit', help='Unit of the odometer ',
                                          required=True,readonly=True, states={'draft':[('readonly',False)]}),
        'transmission': fields.selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission', 
                                         help='Transmission Used by the vehicle',readonly=True,states={'draft':[('readonly',False)]}),
        'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Diesel'), ('electric', 'Electric'), ('hybrid', 'Hybrid')], 
                                      'Fuel Type', help='Fuel Used by the vehicle',readonly=True,states={'draft':[('readonly',False)]}),
        'co2': fields.float('CO2 Emissions', help='CO2 emissions of the vehicle',readonly=True,
                            states={'draft':[('readonly',False)] }),
        'horsepower': fields.integer('Horsepower',readonly=True,states={'draft':[('readonly',False)] }),
        'horsepower_tax': fields.float('Horsepower Taxation',readonly=True,states={'draft':[('readonly',False)] }),
        'power': fields.integer('Power (KW)', help='Power in kW of the vehicle',readonly=True,
                                states={'draft':[('readonly',False)] }),
        'seats': fields.integer('Seats Number', help='Number of seats of the vehicle',readonly=True,
                                states={'draft':[('readonly',False)]  }),
        'doors': fields.integer('Doors Number', help='Number of doors of the vehicle',readonly=True,
                                states={'draft':[('readonly',False)]  }),
        'color': fields.char('Color', size=32, help='Color of the vehicle',readonly=True,
                             states={'draft':[('readonly',False)] }),
        'year': fields.selection(_selection_year, 'Year',readonly=True, 
                                 states={'draft':[('readonly',False)] }),
        'depracc':fields.many2one('account.account',string='Depreciation Account',required=False,readonly=True,
                                  states={'draft':[('readonly',False)] }),
        'type': fields.many2one('vehicle.category', string='Class',readonly=True, 
                                  required=True,states={'draft':[('readonly',False)] }), 
        'status': fields.selection([('active','Active'),('inactive','InActive')], 'Status', required=True,readonly=True,
                                   states={'draft':[('readonly',False)] }),
        'ownership': fields.selection([('owned','Owned'),('rented','Rented'),('generator','Generator'),('mile','Instead mile')],
                                      'Ownership', required=True,readonly=True,states={'draft':[('readonly',False)] }), 
        'company_id':fields.many2one('res.company','Company',required=True,readonly=True,
                                     states={'draft':[('readonly',False)] }),
        'department_id':fields.many2one('hr.department','Department',readonly=True,
                                        states={'draft':[('readonly',False)] }),  
        'machine_no': fields.char('Machine No', size=64,readonly=True,
                                  states={'draft':[('readonly',False)] }), 
        'state': fields.selection([('draft', 'Draft'),('confirm', 'Confirm'),('outservice', 'Out Service'),],
                                  'State', readonly=True, select=True,states={'draft':[('readonly',False)]}),  
        'user_id':  fields.many2one('res.users', 'Responsible', readonly=True,
                                    states={'draft':[('readonly',False)] }), 
        'notes': fields.text('Notes', size=256 ,readonly=True,states={'draft':[('readonly',False)] }),
        'serial':fields.char('productSerial #',size=50,readonly=True,states={'draft':[('readonly',False)] }),
        'machine_capacity':fields.char('Machine Capacity',size=50,readonly=True,states={'draft':[('readonly',False)] }),
        'odometer': fields.function(_get_odometer, fnct_inv=_set_odometer, type='float',readonly=True,states={'draft':[('readonly',False)]}, string='Last Odometer', help='Odometer measure of the vehicle at the moment of this log'),
        'product_id': fields.many2one('product.product','Fuel',readonly=True, states={'draft':[('readonly',False)]}),
    }

    _defaults={
        'state': 'draft', 
        'user_id': lambda self, cr, uid, context: uid,  
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'fleet.vehicles', context=c),              
    }

    _sql_constraints = [
        ('Chassis_number_uniq', 'unique(vin_sn)', _('The Chassis Number Must Be Unique!'))
    ]

    def _check_negative_vals(self, cr, uid, ids, context=None):
        """ 
        Check group of values if greater than zero.

        @return: boolean true of false
        """
        count = 0
        for fleet in self.browse(cr, uid, ids, context=context):
            message = _("The Value Of ")
            if fleet.car_value < 0:
                message += _("Car Value")
                count += 1
            if fleet.co2 < 0:
                if (count > 0):
                        message += ", "
                message += _("CO2 Emissions")
                count += 1
            if fleet.horsepower < 0:
                if (count > 0):
                        message += ", "
                message += _("Horsepower")
                count += 1
            if fleet.horsepower_tax < 0:
                if (count > 0):
                        message +=  ", "
                message += _("Horsepower Taxation")
                count += 1
            if fleet.power < 0:
                if (count > 0):
                        message += ", "
                message += _("Power")
                count += 1
            if fleet.doors < 0:
                if (count > 0):
                        message += ", "
                message += _("Doors Number")
                count += 1
            if fleet.seats < 0:
                if (count > 0):
                        message += _(" And ")
                message += _("Seats Number")
                count += 1
        message += _(" Must Be Greater Than Zero!")
        if count > 0 :
                raise osv.except_osv(_('ValidateError'), _(message)) 
        return True

    _constraints = [
        (_check_negative_vals, '', ['car_value','co2','horsepower','horsepower_tax','power','doors','seats']),
    ]

    def confirmed(self, cr, uid, ids, context=None):
        """
        Workflow function changes state to confirm.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)

    def set_draft(self, cr, uid, ids, context=None):
        """
        Workflow function set state to draft.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def out_service(self, cr, uid, ids, context=None):
        """
        Workflow function changes state to outservice.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'outservice'}, context=context)


