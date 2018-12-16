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

class compare_fuel(osv.osv_memory):
    """ To manage compare fuel wizard """

    _name = "compare.fuel"

    _columns = {
        'place_id':fields.many2one('vehicle.place', 'Place',),
        'first_month': fields.selection([(str(n),str(n)) for n in range(1,13)],'Month', required=True),
        'first_year': fields.char('Year',size=32, required=True),
        'second_month': fields.selection([(str(n),str(n)) for n in range(1,13)],'Month', required=True),
        'second_year': fields.char('Year',size=32, required=True),
    }

    _defaults = {
        'first_year': str(time.strftime('%Y')),
        'second_year' : str(time.strftime('%Y')),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'fuel.plan',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'compare_fuel.report',
            'datas': datas,
            }

