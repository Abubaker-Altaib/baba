# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FleetVehicleCost(models.Model):
    """
        inherit class to add state, and make other fields readonly in confirm state  
    """
    _inherit = 'fleet.vehicle.cost'
	
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True, help='Vehicle concerned by this log',states={'confirm': [('readonly', True)]})
    parent_id = fields.Many2one('fleet.vehicle.cost', 'Parent', help='Parent cost to this current cost',states={'confirm': [('readonly', True)]})
    odometer = fields.Float(compute="_get_odometer", inverse='_set_odometer', string='Odometer Value',
        help='Odometer measure of the vehicle at the moment of this log',states={'confirm': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')], string='State', default='draft')
        
    @api.multi
    def action_vehicle_cost_confirm(self):
        return self.write({'state': 'confirm'})
       
        
class FleetVehicleLogFuel(models.Model):
    """
        inherit class to add state, and make other fields readonly in confirm state  
    """
    _inherit = 'fleet.vehicle.log.fuel'
    
    liter = fields.Float(states={'confirm': [('readonly', True)]})
    price_per_liter = fields.Float(states={'confirm': [('readonly', True)]})
    purchaser_id = fields.Many2one('res.partner', 'Purchaser', domain="['|',('customer','=',True),('employee','=',True)]",states={'confirm': [('readonly', True)]})
    inv_ref = fields.Char('Invoice Reference', size=64,states={'confirm': [('readonly', True)]})
    vendor_id = fields.Many2one('res.partner', 'Vendor', domain="[('supplier','=',True)]",states={'confirm': [('readonly', True)]})
    notes = fields.Text(states={'confirm': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')], string='State', default='draft')

    @api.multi
    def action_vehicle_log_confirm(self):
        return self.write({'state': 'confirm'})

        
class FleetVehicleLogServices(models.Model):
    """
        inherit class to add state, and make other fields readonly in confirm state  
    """
    _inherit = 'fleet.vehicle.log.services'
    
    purchaser_id = fields.Many2one('res.partner', 'Purchaser', domain="['|',('customer','=',True),('employee','=',True)]",states={'confirm': [('readonly', True)]})
    inv_ref = fields.Char('Invoice Reference',states={'confirm': [('readonly', True)]})
    vendor_id = fields.Many2one('res.partner', 'Vendor', domain="[('supplier','=',True)]",states={'confirm': [('readonly', True)]})
    notes = fields.Text(states={'confirm': [('readonly', True)]})

    @api.multi
    def action_vehicle_log_services_confirm(self):
        return self.write({'state': 'confirm'})
