# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv


# Hotel Services wizard report for Specific period of  Time

class fuel_request_report_wizard(osv.osv_memory):
    """
    To manage fuel request report """
    _name = "fuel.request.report.wizard"

    _description = "Fuel Request"

    TYPE_SELECTION = [
         ('emergency', 'Emergency'),
         ('mission','Mission'),
         ('generator','Generator'),
    ]

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
        'state': fields.selection([('done','Executed Requests'),('all','All Requests')],'State',required=True),
        'purpose': fields.selection(TYPE_SELECTION,'Purpose',),        
        'department':fields.many2one('hr.department', 'Department',),
        'car_id':fields.many2one('fleet.vehicle', 'Car',),
        'company_id': fields.many2one('res.company','Company',required=True),
        'plan_type': fields.selection([('fixed_fuel','Fixed fuel'),('extra_fuel','Extra fuel')],'Plan Type'),

    }
    _defaults = {
        'state': 'all',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'fuel.request.report.wizard', context=c),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'fleet.vehicle.log.fuel',
             'form': data,
            }
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fuel.request.report',
            'datas': datas,
            }

