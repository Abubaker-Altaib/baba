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

class service_cars_fuel_report(osv.osv_memory):
    """ To manage compare fuel wizard """

    _name = "service_cars.fuel"

    _columns = {
        'start_date':fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'department_ids':fields.many2many('hr.department',string='Departments'),
    }

    _defaults = {
        'start_date': str(time.strftime('%Y-%m-%d')),
        'end_date' : str(time.strftime('%Y-%m-%d')),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'fuel.qty.line',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'service_cars.report',
            'datas': datas,
            }

