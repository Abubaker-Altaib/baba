# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time

# fuel plan wizard report for Specific plan

class fuel_plan_report_wizard(osv.osv_memory):
    """ Fuel plan report wizard """
    _name = "fuel.plan.report.wizard"

    _description = "Fuel Plan"

    _columns = {
        'month': fields.selection([(str(n),str(n)) for n in range(1,13)],'Month', select=True),
        'year': fields.integer('Year', size=32,),
        'department_id': fields.many2one('hr.department', 'Department'),
        'place_id':fields.many2one('vehicle.place', 'Place'),
    }

    _defaults = {
        'year': int(time.strftime('%Y'))
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        context={
            'user_id':uid,
        }
        datas = {
             'ids': [],
             'model': 'fuel.plan',
             'form': data,
             'context':context
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fix_fule_plan.report',
            'datas': datas,
            }

