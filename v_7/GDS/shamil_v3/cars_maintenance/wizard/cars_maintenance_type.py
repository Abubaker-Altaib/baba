# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv


# Car Maintenance Type Report Class

class cars_maintenance_type_wiz(osv.osv_memory):

    _name = "cars.maintenance.type.wiz"
    _description = "car maintenance Type wiz"

    MAINTENANCE_TYPE_SELECTION = [
    ('regular', 'Regular'),
    ('emergency', 'Emergency'),
 	]  
    STATE_SELECTION = [
        ('done', 'All completed Requests'),
	('notdone', 'All Requests incomplete'), ]


    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
        'maintenance_type': fields.selection(MAINTENANCE_TYPE_SELECTION, 'Maintenance Type',),
    	'state': fields.selection(STATE_SELECTION,'State',), 
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'car.maintenance.request',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cars_maintenance_type.report',
            'datas': datas,
            }

    
