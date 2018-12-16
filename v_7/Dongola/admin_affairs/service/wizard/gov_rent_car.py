# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields
import time


class gov_rent_cars_wiz(osv.osv_memory):
    """ To manage government rented cars reports """
    _name = "gover.rented.cars.wiz"

    _description = "Rented Cars Report"

    _columns = {
        'choose_type':fields.selection([('government','Government'),('rented','Rented'),('all_car','All_car')],'Choose Type',required=True),
        'year': fields.integer('Year',size=32),
    }

    _defaults = {
        'year': int(time.strftime('%Y')),
    }

    def print_report(self, cr, uid, ids, context=None):
        """ 
        Print report.

        @return: Dictionary of print attributes
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'fleet.vehicle.log.contract',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'gov_rent.report',
            'datas': datas,
            }

