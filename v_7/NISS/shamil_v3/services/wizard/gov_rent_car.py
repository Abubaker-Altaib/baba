# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields
import time


# Goverment and rented  Cars Report Class

class gov_rent_cars_wiz(osv.osv_memory):

    _name = "gover.rented.cars.wiz"
    _description = "Rented Cars Report"


    _columns = {
        'choose_type':fields.selection([('goverment','Government'),('rented','Rented'),('all_car','All_car')],'Choose Type',required=True),
        'year': fields.integer('Year',size=32),
    }
    _defaults = {
        'year': int(time.strftime('%Y')),
		}

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'rented.cars',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'gov_rent.report',
            'datas': datas,
            }
gov_rent_cars_wiz()
    
