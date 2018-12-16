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


class vehicles_sale_report(osv.osv_memory):
    """ To manage vehicles Sale report wizard """

    _name = "vehicle.sale.report.wizard"

    _columns = {
        'type': fields.selection([('type', 'Type'), ('model', 'Model')], 'Type'),
	    'model_ids': fields.many2many('fleet.vehicle.model', 'fleet_vehicle_sale_report_model_rel', 'model_id','report_id', string='Model'),
        'type_ids': fields.many2many('vehicle.category', 'fleet_vehicle_sale_report_type_rel', 'type','report_id', string='Class'), 
        'sale_type': fields.selection([('pension','Pension'),('public','Public'),('all','All')],string="sale Type"),
        'start_date': fields.date(string="From"),
        'end_date': fields.date(string="To"),
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
            'model': 'vehicle.sale',
            'form': data
        }

        return {
	'type': 'ir.actions.report.xml',
	'report_name': 'vehicles_sale_report.report',
	'datas': datas,
        }
       
