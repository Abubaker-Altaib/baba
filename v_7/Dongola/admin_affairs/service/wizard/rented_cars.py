# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields
import time
from datetime import datetime
# Rented Cars Report Class

class rented_cars_wiz(osv.osv_memory):
    """ To manage rented cars reports """
    _name = "rented.cars.wiz"

    _description = "Rented Cars Report"

    def _year(self, cr, uid, context=None):
        """ 
        Select cars manufacturing years between 1970 and Current year.

        @return: list of years
        """
        fleet_veh=self.pool.get('fleet.vehicle')
        rangs=fleet_veh._selection_year(self, cr, uid)
        list_year=[]
        for years in rangs[1:len(rangs)]:
                list_year.append(years)
        return list_year

    _columns = {
        'month': fields.selection([(str(n),str(n)) for n in range(1,13)],'Month', select=True , required=True),
        'year': fields.selection(_year, 'Year', select=True, required=True),
        'department_id':fields.many2one('hr.department', 'Department',),
        'partner_id':fields.many2one('res.partner', 'Partner',),
        'choose_type':fields.selection([('manage','الاقسام/الادارت'),('gen_manager','الادارات العامة'),('project','المشاريع')],'Choose Type'),
        'company_id': fields.many2one('res.company','Company',required=True),
    }

    _defaults = {
        'year': int(time.strftime('%Y')),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'rented.cars.wiz', context=c),
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
            'report_name': 'rented_cars_report',
            'datas': datas,
            }

