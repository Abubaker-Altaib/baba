# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields, models,_
from odoo.exceptions import ValidationError

class FleetVehicle(models.Model):
    """
        inherit class to add state, and make other fields readonly in confirm state  
    """
    _inherit = "fleet.vehicle"
	
    company_id = fields.Many2one('res.company', 'Company',states={'confirm': [('readonly', True)]})
    license_plate = fields.Char(required=True, track_visibility="onchange",
        help='License plate number of the vehicle (i = plate number for a car)',states={'confirm': [('readonly', True)]})
    vin_sn = fields.Char('Chassis Number', help='Unique number written on the vehicle motor (VIN/SN number)', copy=False,states={'confirm': [('readonly', True)]})
    driver_id = fields.Many2one('res.partner', 'Driver', track_visibility="onchange", help='Driver of the vehicle', copy=False,states={'confirm': [('readonly', True)]})
    model_id = fields.Many2one('fleet.vehicle.model', 'Model', required=True, help='Model of the vehicle',states={'confirm': [('readonly', True)]})
    acquisition_date = fields.Date('Immatriculation Date', required=False, help='Date when the vehicle has been immatriculated',states={'confirm': [('readonly', True)]})
    color = fields.Char(help='Color of the vehicle',states={'confirm': [('readonly', True)]})
    location = fields.Char(help='Location of the vehicle (garage, ...)',states={'confirm': [('readonly', True)]})
    seats = fields.Integer('Seats Number', help='Number of seats of the vehicle',states={'confirm': [('readonly', True)]})
    model_year = fields.Char('Model Year',help='Year of the model',states={'confirm': [('readonly', True)]})
    doors = fields.Integer('Doors Number', help='Number of doors of the vehicle', default=5,states={'confirm': [('readonly', True)]})
    tag_ids = fields.Many2many('fleet.vehicle.tag', 'fleet_vehicle_vehicle_tag_rel', 'vehicle_tag_id', 'tag_id', 'Tags', copy=False,states={'confirm': [('readonly', True)]})
    odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer', string='Last Odometer',
        help='Odometer measure of the vehicle at the moment of this log',states={'confirm': [('readonly', True)]})
    odometer_unit = fields.Selection([
        ('kilometers', 'Kilometers'),
        ('miles', 'Miles')
        ], 'Odometer Unit', default='kilometers', help='Unit of the odometer ', required=True,states={'confirm': [('readonly', True)]})
    transmission = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission', help='Transmission Used by the vehicle',states={'confirm': [('readonly', True)]})
    fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
        ], 'Fuel Type', help='Fuel Used by the vehicle',states={'confirm': [('readonly', True)]})
    horsepower = fields.Integer(states={'confirm': [('readonly', True)]})
    horsepower_tax = fields.Float('Horsepower Taxation',states={'confirm': [('readonly', True)]})
    power = fields.Integer('Power', help='Power in kW of the vehicle',states={'confirm': [('readonly', True)]})
    co2 = fields.Float('CO2 Emissions', help='CO2 emissions of the vehicle',states={'confirm': [('readonly', True)]})
    image = fields.Binary(related='model_id.image', string="Logo")
    image_medium = fields.Binary(related='model_id.image_medium', string="Logo (medium)",
states={'confirm': [('readonly', True)]})
    car_value = fields.Float(string="Catalog Value (VAT Incl.)", help='Value of the bought vehicle',
states={'confirm': [('readonly', True)]})
    residual_value = fields.Float(states={'confirm': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')], string='State', default='draft')

    @api.multi
    def action_vehicle_confirm(self):
        return self.write({'state': 'confirm'})
        
        
class FleetVehicleOdometer(models.Model):
    """
        inherit class to add state, and make other fields readonly in confirm state  
    """
    _inherit = 'fleet.vehicle.odometer'
    
    date = fields.Date(default=fields.Date.context_today,states={'confirm': [('readonly', True)]})
    value = fields.Float('Odometer Value', group_operator="max",states={'confirm': [('readonly', True)]})
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True,states={'confirm': [('readonly', True)]})
    unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True,states={'confirm': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')], string='State', default='draft')

    @api.multi
    def action_vehicle_odometer_confirm(self):
        return self.write({'state': 'confirm'})


