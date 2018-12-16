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
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations

#--------------------------
#   Fleet Vehicle
#--------------------------


class fleet_vehicle_state(osv.osv):
    """ To Add fleet vehicle state"""
    _inherit = "fleet.vehicle.state"

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]

    _sql_constraints = [
        ('state_name_uniqe', 'unique(name)', 'you can not create same name !')
    ]


class fleet_vehicle_ownership(osv.osv):
    """ To Add fleet vehicle ownership"""
    _name = "fleet.vehicle.ownership"
    _columns = {
        'name': fields.char('Ownership', size=256),
        'vehicles_ids': fields.one2many('fleet.vehicle', 'ownership', string='Vehicles'),
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]

    _sql_constraints = [
        ('ownership_name_uniqe', 'unique(name)', 'you can not create same name !')
    ]

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.vehicles_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(fleet_vehicle_ownership, self).unlink(cr, uid, ids, context=context)


class fleet_vehicle_use(osv.osv):
    """ To Add fleet vehicle use"""
    _name = "fleet.vehicle.use"
    _columns = {
        'name': fields.char('Use', size=256),
        'type': fields.selection([('management', 'Management'), ('dedicated', 'Dedicated'), ('dedicated_managemnet', 'Dedicated Management')], 'Use Type'),
        'vehicles_ids': fields.one2many('fleet.vehicle', 'use', string='Vehicles'),
        'company_id': fields.many2one('res.company','company'),
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id

        return company

    _defaults = {
        'company_id' : _default_company
    }

    _constraints = [
        (_check_spaces, '', ['name'])
    ]
    _sql_constraints = [
        ('fleet_vehicle_use_name_uniqe', 'unique(name)',
         'you can not create same name !')
    ]

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.vehicles_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(fleet_vehicle_use, self).unlink(cr, uid, ids, context=context)


class fleet_vehicle_custody(osv.osv):
    """ To Add fleet vehicle Custody"""
    _name = "fleet.vehicle.custody"
    _columns = {
        'name': fields.char('Custody Name', size=256),
        'number': fields.integer('Custody Number'),
        'default': fields.boolean('Default Custody'),
        'vehicle_type':fields.many2many('vehicle.category', 'vehicle_type_custody_rel', 'custody_id', 'vehicle_type_id', string='Class'),
        'vehicles_ids': fields.many2many('fleet.vehicle', 'fleet_vehicle_vehicle_custody_rel', 'custody_id', 'vehicle_custody_id', 'Vehicles'),
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]

    _sql_constraints = [
        ('fleet_vehicle_custody_name_uniqe',
         'unique(name)', 'you can not create same name !'),
        ('check_custody_number_bigger_than_zero', "CHECK(number > 0)",
         _("The number Must Be Bigger than Zero")),
    ]

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.vehicles_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(fleet_vehicle_custody, self).unlink(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name + '(%s)' % (record.number)
            res.append((record.id, name))
        return res


class fleet_vehicle_color(osv.osv):
    """ To Add fleet vehicle colors"""
    _name = "fleet.vehicle.color"
    _columns = {
        'name': fields.char('Color', size=256),
        'code': fields.char('Code', size=256),
        'vehicles_ids': fields.one2many('fleet.vehicle', 'color', string='Vehicles'),
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if len(rec.name.replace(' ', '')) <= 0:
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
            if rec.code and (len(rec.code.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("code must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['code', 'name'])
    ]
    _sql_constraints = [
        ('color_name_uniq', 'unique(name)', _('Color Name Must Be Unique!'))
    ]

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.vehicles_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(fleet_vehicle_color, self).unlink(cr, uid, ids, context=context)

    def create(self, cr, uid, vals, context=None):
        """
        Override create method to check if color name contains spaces
        @return: super create method
        """
        if 'name' in vals:
            vals['name'] = vals['name'].strip()

        return super(fleet_vehicle_color, self).create(cr, uid, vals, context=context)


class fleet_vehicles(osv.osv):
    """ To manage fleet vehicles """

    def _selection_year(self, cr, uid, context=None):
        """
        Select car manufacturing year between 1970 and Current year.

        @return: list of years 
        """
        return [(str(years), str(years)) for years in range(int(datetime.now().year) + 1, 1970, -1)]

    def _get_odometer(self, cr, uid, ids, odometer_id, arg, context):
        """
        Select odometer value.

        @param odometer_id: id of odometer
        @param arg: extra argument
        @return: dictionary of odometer value 
        """
        res = dict.fromkeys(ids, 0)
        for record in self.browse(cr, uid, ids, context=context):
            ids = self.pool.get('fleet.vehicle.odometer').search(
                cr, uid, [('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if len(ids) > 0:
                res[record.id] = self.pool.get('fleet.vehicle.odometer').browse(
                    cr, uid, ids[0], context=context).value
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

    def _vehicle_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.model_id.brand_id.name + '/' + \
                record.model_id.modelname + ' / ' + record.license_plate + ' / ' + record.vin_sn
            if record.use and record.use.type == 'dedicated' and record.employee_id:
                res[record.id] += ' / ' + record.employee_id.name
        return res

    _inherit = "fleet.vehicle"

    _columns = {
        'code': fields.char('Code',readonly=1),
        'code_plate': fields.char('Code and License Plate',readonly=1),
        'belong_to': fields.selection([('in', 'In'), ('out', 'Out')], 'Belong To', required=False, readonly=True,
                                   states={'draft': [('readonly', False)]}),
        'name': fields.function(_vehicle_name_get_fnc, type="char", string='Name', store=True),
        'model_id': fields.many2one('fleet.vehicle.model', 'Car\'s Model', required=True, readonly=True, help='Model of the vehicle',
                                    states={'draft': [('readonly', False)]}),
        'license_plate': fields.char('License Plate', size=32, readonly=True, states={'draft': [('readonly', False)]},
                                     required=True, help='License plate number of the vehicle (ie: plate number for a car)'),
        'tag_ids': fields.many2many('fleet.vehicle.tag', 'fleet_vehicle_vehicle_tag_rel', 'vehicle_tag_id', 'tag_id',
                                    'Tags', readonly=True, states={'draft': [('readonly', False)]}),
        'custody_ids': fields.many2many('fleet.vehicle.custody', 'fleet_vehicle_vehicle_custody_rel', 'vehicle_custody_id', 'custody_id', 'Custody'),
        'driver_id': fields.many2one('res.partner', 'Driver', help='Driver Of The Vehicle', readonly=True,
                                     states={'draft': [('readonly', False)]}),
        'driver': fields.many2one('hr.employee', 'Driver', help='Driver Of The Vehicle', readonly=True,
                                     states={'draft': [('readonly', False)]}),
        'purchaser': fields.char('Purchaser', size=156),
        'sale_ref': fields.char('Sale Reference', size=156),
        'vehicle_status': fields.selection([('operation', 'Operational Use'), ('internal', 'Internal Use'), ('supply_custody', 'Supply Custody'),
                                            ('disabled', 'Disabled'), ('off', 'Off'), ('custody',
                                                                                       'Custody'), ('sold', 'Sold'), ('for_sale', 'For Sale'),
                                            ('removal', 'Removal'), ('missing', 'Missing')], 'Vehicle Status'),
        'employee_id': fields.many2one('hr.employee', "Employee"),
        'degree_id': fields.related('employee_id', 'degree_id', type="many2one", relation="hr.salary.degree", string="Degree", readonly=1, store=True),
        'location': fields.many2one('vehicle.place', "Vehicle Place", required=True),
        'vin_sn': fields.char('Chassis Number', size=32, help='Unique number written on the vehicle motor (VIN/SN number)', readonly=True,
                              states={'draft': [('readonly', False)]}),
        'vehicle_register': fields.char('Vehicle Register', size=256),
        'acquisition_date': fields.date('Acquisition Date', required=False, readonly=True, help='Date when the vehicle has been bought',
                                        states={'draft': [('readonly', False)]}),
        'car_value': fields.float('Car Value', help='Value of the bought vehicle', readonly=True, states={'draft': [('readonly', False)]}),
        'odometer_unit': fields.selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], 'Odometer Unit', help='Unit of the odometer ',
                                          required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'transmission': fields.selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission',
                                         help='Transmission Used by the vehicle', readonly=True, states={'draft': [('readonly', False)]}),
        'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      'Fuel Type', help='Fuel Used by the vehicle', readonly=True, states={'draft': [('readonly', False)]}),
        'co2': fields.float('CO2 Emissions', help='CO2 emissions of the vehicle', readonly=True,
                            states={'draft': [('readonly', False)]}),
        'horsepower': fields.integer('Horsepower', readonly=True, states={'draft': [('readonly', False)]}),
        'horsepower_tax': fields.float('Horsepower Taxation', readonly=True, states={'draft': [('readonly', False)]}),
        'power': fields.integer('Power (KW)', help='Power in kW of the vehicle', readonly=True,
                                states={'draft': [('readonly', False)]}),
        'seats': fields.integer('Seats Number', help='Number of seats of the vehicle', readonly=True,
                                states={'draft': [('readonly', False)]}),
        'doors': fields.integer('Doors Number', help='Number of doors of the vehicle', readonly=True,
                                states={'draft': [('readonly', False)]}),
        'color': fields.many2one('fleet.vehicle.color', 'Color', help='Color of the vehicle', readonly=True, states={'draft': [('readonly', False)]}),
        #'color': fields.char('Color', help='Color of the vehicle',readonly=True,states={'draft':[('readonly',False)] }),
        'year': fields.selection(_selection_year, 'Model', readonly=True,
                                 states={'draft': [('readonly', False)]}),
        'depracc': fields.many2one('account.account', string='Depreciation Account', required=False, readonly=True,
                                   states={'draft': [('readonly', False)]}),
        'type': fields.many2one('vehicle.category', string='Class', readonly=True,
                                required=True, states={'draft': [('readonly', False)]}),
        'status': fields.selection([('active', 'Active'), ('inactive', 'InActive')], 'vehicle Activation', required=False, readonly=True,
                                   states={'draft': [('readonly', False)]}),
        'ownership': fields.many2one('fleet.vehicle.ownership', 'Ownership'),
        'use': fields.many2one('fleet.vehicle.use', 'Use'),
        'use_type': fields.char(string="Use Type"),
        'incoming': fields.char('Incoming Certificate', size=256),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', 'Department', readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'machine_no': fields.char('Machine No', size=64, readonly=True,
                                  states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('outservice', 'Out Service'), ],
                                  'State', readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'user_id':  fields.many2one('res.users', 'Responsible', readonly=True,
                                    states={'draft': [('readonly', False)]}),
        'notes': fields.text('Notes', size=256, readonly=True, states={'draft': [('readonly', False)]}),
        'serial': fields.char('productSerial #', size=50, readonly=True, states={'draft': [('readonly', False)]}),
        'machine_capacity': fields.char('Machine Capacity', size=50, readonly=True, states={'draft': [('readonly', False)]}),
        'odometer': fields.function(_get_odometer, fnct_inv=_set_odometer, type='float', store=True, readonly=True, states={'draft': [('readonly', False)]}, string='Last Odometer', help='Odometer measure of the vehicle at the moment of this log'),
        'product_id': fields.many2one('product.product', 'Fuel', readonly=True, states={'draft': [('readonly', False)]}),
        'contracts': fields.many2many('fleet.vehicle.log.contract', 'fleet_vehicle_contract_vehicle', 'vehicle_id', 'model_id', string='Contracts'),
        'accidents_ids': fields.one2many('vehicle.accident', 'vehicle_id', string='Accident'),
        'moves_ids': fields.one2many('vehicle.move', 'vehicle_id', string='Move'),   
        'license_date': fields.date('Last License Date'),
        'insurance_date': fields.date('Last Insurance Date') ,
        'out_driver': fields.char('Driver'),
        'insurance_type': fields.selection([('part', 'Third Part'),('all', 'All'),('other','Other')],'Insurance Type'), 
        'incoming_type': fields.selection([('local','Local'),('incoming','Incoming')], 'Incoming Type'),
        'out_department': fields.many2one('vehicle.out.department', 'External Department'),
        'old_system_driver': fields.char('Driver In Old System'),
        'old_system_degree': fields.char('Degree In Old System'),
        'move_note':fields.text('Move Notes'),

    }


    _defaults = {
        'belong_to':'in',
        'state': 'draft',
        'user_id': lambda self, cr, uid, context: uid,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'fleet.vehicles', context=c),
        'status': 'active',
        'code': '/',
        'code_plate':'/',
        'insurance_type': 'other',

    }

    _sql_constraints = [
        ('Chassis_number_uniq', 'unique(vin_sn)',
         _('The Chassis Number Must Be Unique!')),
        ('machine_no_uniq', 'unique(machine_no)',
         _('The Machine Number Must Be Unique!')),
        ('license_plate_uniq', 'unique(license_plate)',
         _('The License Plate Must Be Unique!')),
    ]

    def create(self, cr, uid, data, context=None):
        """
        To set status of vehicle inactive base on vehicle_status 
        and set code and code_plate
        """
        if 'archive' in context:
            raise  osv.except_osv(_('Error'), _('You can not create vehicle from archive') )
        if 'vehicle_status' in data:
            if data['vehicle_status'] in ('disabled', 'off', 'sold', 'removal', 'missing'):
                data['status'] = 'inactive'
        if data.get('code', False) in ['/', False]:
            seq = self.pool.get('ir.sequence').next_by_code(cr, uid, 'fleet.vehicle.code')
            data['code'] = seq
            data['code_plate'] = seq +':'+ data['license_plate']
            if not seq:
                raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'fleet.vehicle.code\'') )
        return super(fleet_vehicles, self).create(cr, uid, data, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        To set status of vehicle inactive base on vehicle_status
        and set code and code_plate
        """
        rec=self.browse(cr ,uid, ids,context=context)[0]
        if 'vehicle_status' in vals:
            if vals['vehicle_status'] in ('disabled', 'off', 'sold', 'removal', 'missing'):
                vals['status'] = 'inactive'
        if 'license_plate' in vals:
            vals['code_plate'] = rec.code + vals['license_plate']
        return super(fleet_vehicles, self).write(cr, uid, ids, vals, context)

    def onchange_vehicle_status(self, cr, uid, ids, vehicle_status, context=None):
        """
        Set vehicle Activation depend on vehicle_status.

        @param vehicle_status: selection of vehicle_status
        @return: Dictionary of values 
        """
        value = {}
        if vehicle_status:
            if vehicle_status in ('disabled', 'off', 'sold', 'removal', 'missing'):
                value = {'status': 'inactive'}
            else:
                value = {'status': 'active'}
        return {'value': value}

    def onchange_out_driver(self, cr, uid, ids, out_driver):
        """
        check if out_driver contains space and return it without space
        """
        vals = {}
        if out_driver:
            vals['out_driver'] = out_driver.strip()

        return {'value': vals}

    def onchange_type(self, cr, uid, ids, typee, context=None):
        """
        To set custodys value and domain base on type.

        @param typee: vehicle category
        @return: Dictionary of values and domain
        """
        value = {}
        domain = {}
        custody_obj = self.pool.get('fleet.vehicle.custody')
        if typee:
            ttype=[]
            custodys = custody_obj.search(cr, uid, [('default', '=', True)])
            custodyss = custody_obj.browse(cr, uid, custodys, context=context)
            for custody in custodyss:
                for t in custody.vehicle_type:
                    if t.id == typee:
                        ttype.append(custody.id)
            value['custody_ids']=ttype

            ttype=[]
            custodys = custody_obj.search(cr, uid, [])
            custodyss = custody_obj.browse(cr, uid, custodys, context=context)
            for custody in custodyss:
                for t in custody.vehicle_type:
                    if t.id == typee:
                        ttype.append(custody.id)
            domain['custody_ids']=[('id', 'in', ttype)]
        return {'value': value,'domain': domain}


    def onchange_vehicle_use(self, cr, uid, ids, use, department_id, employee_id, belong_to, context={}):
        """
        To make employee_id and department_id requierd base on use type.

        @param use: Id of use
        @return: Dictionary of values 
        """
        emp_obj = self.pool.get('hr.employee')
        dept_obj = self.pool.get('hr.department')
        vals={}
        domain={}
        vals['use_type'] = False
        vals['department_id'] = False
        vals['employee_id'] = False
        vals['out_driver'] = False
        if use:
            
            vals['use_type'] = self.pool.get('fleet.vehicle.use').browse(
                cr, uid, use, context=context).type
            if not belong_to or belong_to == 'in':
                if vals['use_type'] == 'dedicated':
                    vals['employee_id'] = False
                    vals['department_id'] = False
                    domain['employee_id'] = [('state','=','approved')]
                    domain['department_id'] = [('id','in',[])]
                    if employee_id:
                        department = emp_obj.browse(cr, uid, employee_id).department_id.id
                        vals['department_id'] = department
                        domain['department_id'] = [('id','in',[department])]
                        vals['employee_id'] = employee_id
                else:
                    vals['employee_id'] = False
                    vals['department_id'] = False
                    domain['employee_id'] = [('id','in',[])]
                    dep_ids = dept_obj.search(cr,uid,[])
                    domain['department_id'] = [('id','in',dep_ids)]
                    if department_id:
                        #department = emp_obj.browse(cr, uid, employee_id).department_id.id
                        domain['employee_id'] = [('department_id','in',[department_id]),('state','=','approved')]
                        vals['department_id'] = department_id
                        if employee_id:
                            department = emp_obj.browse(cr, uid, employee_id).department_id.id
                            vals['employee_id'] = department in [department_id] and employee_id or False
        return {'value':vals,'domain':domain}

    def onchange_belong_to(self, cr, uid, ids, belong_to, context={}):
        """
        """
        vals = {}
        if belong_to and belong_to == 'out':
            vals['employee_id'] = False
            vals['degree_id'] = False
            vals['department_id'] = False
            vals['driver'] = False

        if belong_to and belong_to == 'in':
            vals['out_driver'] = False
            vals['out_department'] = False

        return {'value': vals}

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
                    message += ", "
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
            if fleet.odometer < 0:
                if (count > 0):
                    message += _(" And ")
                message += _("Odometer Number")
                count += 1
        message += _(" Must Be Greater Than Zero!")
        if count > 0:
            raise osv.except_osv(_('ValidateError'), _(message))
        return True

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
            if rec.vin_sn and (len(rec.vin_sn.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'), _(
                    "vin_sn must not be spaces"))
        return True

    def get_date(self, str):
        return datetime.strptime(str, "%Y-%m-%d")

    def get_datetime(self, str):
        return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")

    def _check_contracts(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for contract in rec.contracts:
                start_date = self.get_date(contract.start_date)
                expiration_date = self.get_date(contract.expiration_date)
                for sub in rec.contracts:
                    sub_start_date = self.get_date(sub.start_date)
                    sub_expiration_date = self.get_date(sub.expiration_date)
                    if sub.id == contract.id:continue
                    if sub.state != 'confirm':continue
                    if sub.category not in ['license']:continue
                    if contract.category == sub.category:
                        if sub_start_date >= start_date:
                            if sub_start_date <= expiration_date:
                                raise osv.except_osv(_('ValidateError'), _(
                                    "this operation is already exist for this vehicle in this date range"))
                        if start_date >= sub_start_date:
                            if start_date <= sub_expiration_date:
                                raise osv.except_osv(_('ValidateError'), _(
                                    "this operation is already exist for this vehicle in this date range"))

        return True
    _constraints = [
        (_check_negative_vals, '', [
         'car_value', 'co2', 'horsepower', 'horsepower_tax', 'power', 'doors', 'seats','odometer']),
        (_check_spaces, '', ['name', 'vin_sn']),
    ]

    def confirmed(self, cr, uid, ids, context=None):
        """
        Workflow function changes state to confirm.

        @return: write state
        """
        '''if not self.pool.get('ir.attachment').search(cr,uid,[('res_model','=','fleet.vehicle'),('res_id','=',ids[0])],context=context):
                raise osv.except_osv(_('ValidateError'), _("Plase attach Insurance Certificate"))'''
        for rec in self.browse(cr, uid, ids):
            if not rec.use:
                raise osv.except_osv(_('Error'), _("Plase Enter Vehicle Use"))
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def set_draft(self, cr, uid, ids, context=None):
        """
        Workflow function set state to draft.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def out_service(self, cr, uid, ids, context=None):
        """
        Workflow function changes state to outservice.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state': 'outservice'}, context=context)

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.fuel_plan_ids or rec.maintenance_spare_ids or rec.contracts or rec.accidents_ids or rec.moves_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
            if rec.state != 'draft':
                raise osv.except_osv(
                    _(''), _("can not delete record not in draft state"))
        return super(fleet_vehicles, self).unlink(cr, uid, ids, context=context)

    def get_licences(self, cr, uid, ids, context=None):
        """
        Method that return licenses related to the selected vehicle.

        @return: write state
        """
        license_obj = self.pool.get('fleet.vehicle.log.contract')
        license_line_obj = self.pool.get('fleet.vehicle.log.contract.line')
        mod_obj = self.pool.get('ir.model.data')
        return_ids = []
        
        license_ids = license_obj.search(
            cr, uid, [('category', '=', 'license')])
        
        fetch = []
        if license_ids:
            license_line_ids = license_line_obj.search(cr, uid, [('fleet_contract_id','in',license_ids),
                ('vehicle_id','=',ids[0])])
            #cr.execute("""select model_id from fleet_vehicle_contract_vehicle where model_id in %s and vehicle_id =%s""", (tuple(
            #    license_ids), ids[0]))
            #fetch = [x[0] for x in cr.fetchall()]

            fetch = [x.fleet_contract_id.id for x in license_line_obj.browse(cr, uid, license_line_ids)]

        model_data_tree_ids = mod_obj.search(cr, uid, [(
            'model', '=', 'ir.ui.view'), ('name', '=', 'vehicle_license_tree')], context=context)
        tree_id = mod_obj.read(cr, uid, model_data_tree_ids, fields=[
                               'res_id'], context=context)[0]['res_id']

        model_data_form_ids = mod_obj.search(cr, uid, [(
            'model', '=', 'ir.ui.view'), ('name', '=', 'vehicle_license_form')], context=context)
        form_id = mod_obj.read(cr, uid, model_data_form_ids, fields=[
                               'res_id'], context=context)[0]['res_id']

        return {
            'domain': [('id', 'in', fetch)],
            'name': u'التراخيص',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'fleet.vehicle.log.contract',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'type': 'ir.actions.act_window',
        }

    def get_insurances(self, cr, uid, ids, context=None):
        """
        Method that return Insurances related to the selected vehicle.

        @return: write state
        """
        insurance_obj = self.pool.get('fleet.vehicle.log.contract')
        insurance_line_obj = self.pool.get('fleet.vehicle.log.contract.line')
        mod_obj = self.pool.get('ir.model.data')
        return_ids = []
        insurance_ids = insurance_obj.search(
            cr, uid, [('category', '=', 'insurance')])
        fetch = []
        if insurance_ids:
            insurance_line_ids = insurance_line_obj.search(cr, uid, [('fleet_contract_id','in',insurance_ids),
                ('vehicle_id','=',ids[0])])

            #cr.execute("""select model_id from fleet_vehicle_contract_vehicle where model_id in %s and vehicle_id =%s""", (tuple(
            #    insurance_ids), ids[0]))
            #fetch = [x[0] for x in cr.fetchall()]

            fetch = [x.fleet_contract_id and x.fleet_contract_id.id for x in insurance_line_obj.browse(cr, uid, insurance_line_ids)]

        model_data_tree_ids = mod_obj.search(cr, uid, [(
            'model', '=', 'ir.ui.view'), ('name', '=', 'vehicle_insurance_tree')], context=context)
        tree_id = mod_obj.read(cr, uid, model_data_tree_ids, fields=[
                               'res_id'], context=context)[0]['res_id']

        model_data_form_ids = mod_obj.search(cr, uid, [(
            'model', '=', 'ir.ui.view'), ('name', '=', 'vehicle_insurance_form')], context=context)
        form_id = mod_obj.read(cr, uid, model_data_form_ids, fields=[
                               'res_id'], context=context)[0]['res_id']

        return {
            'domain': [('id', 'in', fetch)],
            'name': u'التأمينات',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'fleet.vehicle.log.contract',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'type': 'ir.actions.act_window',
        }


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        lines = []
        emp_cost=[]
        vehicle_ids = []
        ids = []
        sale_line_obj = self.pool.get('vehicle.sale.lines')
        contract_line_obj = self.pool.get('fleet.vehicle.log.contract.line')
        if context is None:
            context = {}

        ids = self.search(cr, uid, [('vin_sn', operator, name)]+ args, limit=limit, context=context)
        ids += self.search(cr, uid, [('license_plate', operator, name)]+ args, limit=limit, context=context)
        ids = list(set(ids))
        args.append(('id','in',ids))

        if 'model' in context and context['model'] == 'vehicle.sale':

            line_ids = resolve_o2m_operations(cr, uid, self.pool.get('vehicle.sale.lines'),
                                                context.get('line_id'), ["vehicle_id"], context)
            
            args.append(('id', 'not in', [isinstance(
                d['vehicle_id'], tuple) and d['vehicle_id'][0] or d['vehicle_id'] for d in line_ids]))
            
            '''for sale_line in context.get('line_id'):
                if sale_line[1]:
                    vehicle_ids.append(sale_line_obj.browse(cr, uid, sale_line[1], context).vehicle_id.id)
                if sale_line[2]:
                    vehicle_ids.append(sale_line[2]['vehicle_id'])

            if vehicle_ids:
                args.append(('id', 'not in', vehicle_ids))'''

        if 'model' in context and context['model'] == 'fleet.vehicle.log.contract.line':

            line_ids = resolve_o2m_operations(cr, uid, self.pool.get('fleet.vehicle.log.contract.line'),
                                                context.get('line_id'), ["vehicle_id"], context)

            args.append(('id', 'not in', [isinstance(
                d['vehicle_id'], tuple) and d['vehicle_id'][0] or d['vehicle_id'] for d in line_ids]))

            '''for contract_line in context.get('line_id'):
                if contract_line[1]:
                    vehicle_ids.append(contract_line_obj.browse(cr, uid, contract_line[1], context).vehicle_id.id)
                if contract_line[2]:
                    vehicle_ids.append(contract_line[2]['vehicle_id'])

            if vehicle_ids:
                args.append(('id', 'not in', vehicle_ids))'''

        return super(fleet_vehicles, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

    def name_get(self, cr, uid, ids, context=None):
        """Append the employee code to the name"""
        if not ids:
            return []
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        for record in self.browse(cr, uid, ids, context=context):
            name = record.model_id.brand_id.name + '/' + \
                record.model_id.modelname + ' / ' + record.license_plate + ' / ' + record.vin_sn
            if record.use and record.use.type == 'dedicated' and record.employee_id:
                name += ' / ' + record.employee_id.name
            res.append((record.id,name))
        
        return res
        

#--------------------------
#   Inherit hr_department
#--------------------------
class hr_department(osv.osv):

    _inherit = 'hr.department'

    def name_get(self, cr, uid, ids, context=None):
        """
        """
        if context is None:
            context = {}
        if not ids:
            return []
        
        new_res = []
        if 'fleet' in context:
            reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
            res = []
            for record in reads:
                name = record['name']
                if record['parent_id']:
                    name = record['parent_id'][1].split(')')[1]+' / '+ name 
                name = '(' + str(record['id']) + ')' +  name
                res.append((record['id'], name))
        
            return res

        else:
            return super(hr_department,self).name_get(cr , uid, ids, context=context)



#--------------------------
#   fleet_vehicle_model (Inherit)
#--------------------------
class fleet_vehicle_model(osv.osv):

    _inherit = "fleet.vehicle.model"

    def _model_name_get_fnc(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            name = record.modelname
            if record.brand_id.name:
                name = record.brand_id.name + ' / ' + name
            res[record.id] = name
        return res

    def _get_barands(self, cr, uid, ids, context=None):
        idss = []
        if ids:
            idss = self.pool.get('fleet.vehicle.model').search(cr, uid, [('brand_id','in', ids)])
        return idss

    _columns = {
        'name': fields.function(_model_name_get_fnc,  type="char", string='Name',
            store={
                'fleet.vehicle.model': (lambda self, cr, uid, ids, c={}: ids, ['note','modelname','brand_id'], 20),
                'fleet.vehicle.model.brand': (_get_barands, ['name'], 10),
            }),
        'note': fields.char('Note'),
    }