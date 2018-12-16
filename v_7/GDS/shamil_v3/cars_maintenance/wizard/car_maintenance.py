# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv


# Car Maintenance Report Class

class car_maintenance_wiz(osv.osv_memory):

    _name = "car.maintenance.wiz"
    _description = "Car Maintenance Wizard"

    STATE_SELECTION = [
        ('completed', 'Completed orders'),
        ('incomplete', 'Incomplete orders'), ]

    MAINTENANCE_TYPE_SELECTION = [
    ('regular', 'Regular'),
    ('emergency', 'Emergency'),
 	]  

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
    	'car_id':fields.many2one('fleet.vehicle', 'Car Name',),
        'state': fields.selection(STATE_SELECTION,'State',),
        'maintenance_type': fields.selection(MAINTENANCE_TYPE_SELECTION, 'Maintenance Type',),
        'partner_id': fields.many2one('res.partner', 'Partner',),
        'department_id': fields.many2one('hr.department', 'Department',),
	'details': fields.boolean('With details' ,),
        'product_id': fields.many2one('product.product','Item',),
    
               }
    _defaults = {
               'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'car.maintenance.wiz', context=c),
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
            'report_name': 'car_maintenance.report',
            'datas': datas,
            }

    
