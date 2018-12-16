# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
import math

class AppointmentTerms(models.Model):
    _name = "hr.appointment.term"
    _description = 'Appointment Terms'
    
    name = fields.Char(string='Appointment Terms', required=True , Translate=True)
    
class ContractType(models.Model):
    _name = 'hr.contract.type'
    _inherit = ['mail.thread', 'hr.contract.type']
    
    app_term_ids = fields.Many2many('hr.appointment.term',string ="Appointment Terms")
    term_ids = fields.One2many('hr.contract.term', 'contract_type_id' ,string ="Terms", readonly=True,states={'draft': [('readonly', False)]})
    tag_id = fields.Many2one('hr.employee.category' ,string = "Employee Tag")
    resource_calendar_id = fields.Many2one('resource.calendar' ,string = "working schedule")
    trial_period = fields.Integer("Trial Period", default=3, required=True)
    trial_period_times = fields.Integer("Trial Period Times", default=3, required=True)
    temporary_period=fields.Integer("Temporary Period")
    type = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
    ],string='Type',required=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Closed'),
    ], string='Status', default='draft', track_visibility='onchange')
    number_dependents=fields.Integer("Dependents Number")
    
    
class ContractTypeTerms(models.Model):
    _name = "hr.contract.term"
    _description = 'Contract Terms'
    _order = 'term_no'

    name = fields.Char(string='Term' ,required=True)
    term_no = fields.Integer("Term Number", required=True)
    description = fields.Text('Description')
    type = fields.Selection([
        ('mandatory', 'Mandatory'),
        ('optional', 'Optional')], string='Type', default='mandatory', required=True)
    contract_type_id = fields.Many2one("hr.contract.type")
    

class Contract(models.Model):
    _inherit = 'hr.contract'

    app_term_ids = fields.Many2many('hr.appointment.term', string='Appointment Terms')
    type = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
    ],string='Type')
    number_dependents=fields.Integer("Dependents Number")

    @api.onchange('type_id')
    def onchange_type(self):
        if self.type=='temporary':
            date_start=fields.Datetime.from_string(self.date_start)
            self.date_end=date_start+relativedelta(months=self.type_id.temporary_period)
        if self.type_id:
            return {
                'domain': {
                    'app_term_ids': [('id', 'in', self.type_id.app_term_ids.ids)] ,
                }
            }


            



