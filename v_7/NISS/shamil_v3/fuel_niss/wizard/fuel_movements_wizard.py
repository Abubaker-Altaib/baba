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

class fuel_movements(osv.osv_memory):
    """ To manage fuel movements wizard """

    _name = "fuel.movements"

    _columns = {
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'fuel_type': fields.selection([('gasoline','Gasoline'),('diesel', 'Diesel'),('electric', 'Electric'), ('hybrid', 'Hybrid')],'Fuel type') ,
        'locations_ids': fields.many2many('stock.location', 'fuel_movement_stock_location_rel', 'fuel_movement_id', 'stock_location_id', 'Stock Location'),
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
        datas = {
             'ids': [],
             'model': 'stock.move',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fuel_movements_report.report',
            'datas': datas,
            }

