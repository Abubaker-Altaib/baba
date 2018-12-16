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

class fuel_exchange_status_report(osv.osv_memory):
    """ To manage fuel fuel exchange status report wizard """

    _name = "fuel_exchange_status_report"

    _columns = {
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'fuel_type': fields.selection([('gasoline','Gasoline'),('diesel', 'Diesel'),('electric', 'Electric'), ('hybrid', 'Hybrid')],'Fuel type') ,
        'fuel_exchange_status': fields.selection([('exchange','Currently Disbursed'),('stop','Stopped')], 'Fuel Exchange Status'),
        'use': fields.many2one('fleet.vehicle.use', 'Use'),
        'vehicles_ids': fields.many2many('fleet.vehicle', string='Vehicles'),
        'employees_ids': fields.many2many('hr.employee', string='Employees'),
        'company_id': fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
        'start_date': time.strftime('%Y-%m-%d'),
        'end_date': time.strftime('%Y-%m-%d'),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'fuel_exchange_status_archive',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fuel.fuel_exchange_status.report',
            'datas': datas,
            }

