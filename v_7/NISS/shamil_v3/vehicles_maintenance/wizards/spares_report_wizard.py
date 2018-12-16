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


class spares_report_wizard(osv.osv_memory):
    """ To manage spares report wizard """

    _name = "spares.report.wizard"

    _columns = {
        'start_date': fields.datetime('Start Date'),
        'end_date': fields.datetime('End Date'),
        'vehicles_ids': fields.many2many('fleet.vehicle', 'spares_report_wizard_vehicle_rel', 'spares_report_wizard_id', 'vehicle_id', 'vehicles'),
        'products_ids': fields.many2many('product.product', 'spares_report_wizard_product_rel', 'spares_report_wizard_id', 'product_id', 'products'),
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
            'model': 'maintenance.spare',
            'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'spares_report.report',
            'datas': datas,
        }
