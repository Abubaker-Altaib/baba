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


class vehicles_theft_report(osv.osv_memory):
    """ To manage vehicles Theft report wizard """

    _name = "vehicle.theft.report.wizard"

    _columns = {
        'type': fields.selection([('model', 'Model'), ('type', 'Type'), ('employee', 'Employee'), ('period', 'Period'), ('place','Place')], 'Type', required=True),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'place': fields.char('Place'),
	    'model_ids': fields.many2many('fleet.vehicle.model', 'fleet_vehicle_theft_report_model_rel', 'model_id','report_id', string='Model'),
        'type_ids': fields.many2many('vehicle.category', 'fleet_vehicle_theft_report_type_rel', 'type','report_id', string='Class'), 
        'employee_ids': fields.many2many('hr.employee', 'fleet_vehicle_theft_report_employee_rel', 'employee_id','report_id', string="Employee"),
    }

    _defaults = {
        'start_date': time.strftime('%Y-%m-%d'),
        'end_date': time.strftime('%Y-%m-%d'),
    }


    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
	print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>data",data
        datas = {
            'ids': [],
            'model': 'fleet.vehicle',
            'form': data
        }

        return {
	'type': 'ir.actions.report.xml',
	'report_name': 'vehicles_theft_report.report',
	'datas': datas,
        }
       
