# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv


# Mission Cars  wizard report for Specific period of  Time

class cars_mission_wiz(osv.osv_memory):
    """
    To manage cars mission """

    _name = "cars.mission.wiz"

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),

        'car_id':fields.many2one('fleet.vehicle', 'Car',),

    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'fuel.request',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cars_mission.report',
            'datas': datas,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
