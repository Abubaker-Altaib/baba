 # -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class hr_config_settings_inherit(osv.Model):

    _inherit = 'res.company'

    _columns = {
              'add_service' :fields.integer("Add Service", required= True),
              'operation_service' :fields.integer("Operation Service", required=True,help="By This Number The Operation month of employee will be multipled."),
              'connected_service_limit' :fields.integer("Connected Service Limit", required=True,help="Connected Service Must not exceed this Limit."),
              'separated_service_limit' :fields.integer("Separated Service Limit", required=True,help="Separated Service Must not exceed this Limit."),
              'number_of_absence_escape_days' :fields.integer("Number Of Days To Create Escape", required=True,help="Number of Absence Days To create Escapes"),
              'number_of_absence_payroll_days' :fields.integer("Number Of Days To Deduct From Payroll", required=True,help="Number of Absence Days To Deduct From payroll"),
               }

    _defaults = {
         'add_service':8,
         'operation_service':1,
         'connected_service_limit':90,
         'separated_service_limit':10,
         'number_of_absence_payroll_days':5,
         'number_of_absence_escape_days': 21,

        }
