# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv


# Hotel Services wizard report for Specific period of  Time

class fuel_request_report_wizard(osv.osv_memory):
    """
    To manage fule request report """

    _name = "fuel.request.report.wizard"
    _description = "Fuel Request"

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed_s', 'Waiting for Department manager To confirm'),
    ('confirmed_d', 'Waiting for admin  affairs manager to approve '),
    ('approved', 'Waiting for service section  manager to process'),
    ('execute', 'Waiting service officer to Exceute'),
    ('picking', 'In Progress'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ]

    TYPE_SELECTION = [
         ('emergency', 'Emergency'),
         ('mission','Mission'),
         ('generator','Generator'),
         ]

    CATEGORY_SELECTION = [
         ('normal', 'Normal'),
         ('exceptional','Exceptional'),
         ]
    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
        'state': fields.selection(STATE_SELECTION,'State',),
        'purpose': fields.selection(TYPE_SELECTION,'State',),        
        'department':fields.many2one('hr.department', 'Department',),
        'car_id':fields.many2one('fleet.vehicle', 'Car',),
        'gategory': fields.selection(CATEGORY_SELECTION, 'Gategory',select=True),
   	'company_id': fields.many2one('res.company','Company',required=True,readonly=True),

    }
    _defaults = {
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
             'model': 'fuel.request',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fuel.request.report.report',
            'datas': datas,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
