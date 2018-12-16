# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class hr_config_settings(osv.osv_memory):

    _inherit = 'hr.config.settings'

    _columns = {
              'add_service' :fields.integer("Add Service", required=True,help="Add Connected additional service to employee total Service Duration after this years."),
              'operation_service' :fields.integer("Operation Service", required=True,help="By This Number The Operation month of employee will be multipled."),
              'connected_service_limit' :fields.integer("Connected Service Limit", required=True,help="Connected Service Must not exceed this Limit."),
              'separated_service_limit' :fields.integer("Separated Service Limit", required=True,help="Separated Service Must not exceed this Limit."),
              'number_of_absence_escape_days' :fields.integer("Number Of Absence Days To Create Escape", required=True,help="Number of Absence Days To create Escapes"),
              'number_of_absence_payroll_days' :fields.integer("Number Of Absence Days To Deduct From Payroll", required=True,help="Number of Absence Days To Deduct From payroll"),
    }

    _defaults = {
        'add_service':8,
        'operation_service':1,
        'connected_service_limit':90,
        'separated_service_limit':10,
    }

    def get_default_add_service(self, cr, uid, fields, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return {
            'add_service': user.company_id.add_service,
        }

    def set_default_add_service(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_obj=self.pool.get('res.company')
        config = self.browse(cr, uid, ids[0], context)
        add_service= config and config.add_service
        company_id = user.company_id.id
        company_obj.write(cr, uid, company_id, {'add_service': add_service})
        return True

    def get_default_operation_service(self, cr, uid, fields, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return {
            'operation_service': user.company_id.operation_service,
        }

    def set_default_operation_service(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_obj=self.pool.get('res.company')
        config = self.browse(cr, uid, ids[0], context)
        operation_service= config and config.operation_service
        company_id = user.company_id.id
        company_obj.write(cr, uid, company_id, {'operation_service': operation_service})
        return True

    def get_default_connected_service_limit(self, cr, uid, fields, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return {
            'connected_service_limit': user.company_id.connected_service_limit,
        }

    def set_default_connected_service_limit(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_obj=self.pool.get('res.company')
        config = self.browse(cr, uid, ids[0], context)
        connected_service_limit= config and config.connected_service_limit
        company_id = user.company_id.id
        company_obj.write(cr, uid, company_id, {'connected_service_limit': connected_service_limit})
        return True

    def get_default_separated_service_limit(self, cr, uid, fields, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return {
            'separated_service_limit': user.company_id.separated_service_limit,
        }

    def set_default_separated_service_limit(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_obj=self.pool.get('res.company')
        config = self.browse(cr, uid, ids[0], context)
        separated_service_limit= config and config.separated_service_limit
        company_id = user.company_id.id
        company_obj.write(cr, uid, company_id, {'separated_service_limit': separated_service_limit})
        return True

    def get_default_absence_information(self, cr, uid, fields, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return {
            'number_of_absence_escape_days': user.company_id.number_of_absence_escape_days,
            'number_of_absence_payroll_days': user.company_id.number_of_absence_payroll_days,
        }

    def set_default_absence_information(self, cr, uid, ids, context=None):
        company_obj= self.pool.get('res.company')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        config = self.browse(cr, uid, ids[0], context)
        number_of_absence_escape_days = config.number_of_absence_escape_days
        number_of_absence_payroll_days = config.number_of_absence_payroll_days
        vals = {'number_of_absence_payroll_days': number_of_absence_payroll_days, 'number_of_absence_escape_days':number_of_absence_escape_days}
        company_obj.write(cr, uid, [user.company_id.id], vals)
        return True
