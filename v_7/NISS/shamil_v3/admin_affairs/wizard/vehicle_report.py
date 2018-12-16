# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv
import time
from datetime import datetime,date,timedelta
from tools.translate import _

class vehicle_report_wiz(osv.osv_memory):
    """ To manage enrich report wizard """
    _name = "vehicle.report.wiz"

    _description = "Vehicle Report Wizard"

    def _selection_year(self, cr, uid, context=None):
        """
        Select car manufacturing year between 1970 and Current year.

        @return: list of years 
        """
        return [(str(years), str(years)) for years in range(int(datetime.now().year) + 1, 1970, -1)]

    _columns = {
        #'date_from': fields.date('Date From'),
        #'date_to': fields.date('Date To'),
        'group_by': fields.selection([('status','Vehicle Status'),('category','Vehicle type'), 
                                    ('model','Vehicle Model'),('year','Vehicle Year'),
                                    ('degree','Degree'),('ownership','Vehicle Ownership'),
                                    ('use','Vehicle Use'),('department','Vehicle Department'),
                                    #('department_custody','Vehicles That Were and Still Under Department Custody'),
                                    #('employee_custody','Vehicles That Were and Still Under Employee Custody')
                                    ],'Group By',),
        'departments_ids': fields.many2many('hr.department','departments_vehicle_report_rel',string='Departments'),
        'models_ids': fields.many2many('fleet.vehicle.model','models_vehicle_report_rel',string='Vehicle Models'),
        'categories_ids': fields.many2many('vehicle.category','categories_vehicle_report_rel',string='Vehicle Categories'),
        'ownerships_ids': fields.many2many('fleet.vehicle.ownership','ownerships_vehicle_report_rel',string='Vehicle Ownerships'),
        'uses_ids': fields.many2many('fleet.vehicle.use','uses_vehicle_report_rel',string='Vehicle Uses'),
        'degree_ids': fields.many2many('hr.salary.degree','degree_vehicle_report_rel',string='Degrees'),
        'department_id': fields.many2one('hr.department',string='Department'),
        'model_id': fields.many2one('fleet.vehicle.model',string='Vehicle Model'),
        'brand_id': fields.many2one('fleet.vehicle.model.brand',string='Model Brand Of Vehicle'),
        'category_id': fields.many2one('vehicle.category',string='Vehicle Category'),
        'ownership_id': fields.many2one('fleet.vehicle.ownership',string='Vehicle Ownership'),
        'use_id': fields.many2one('fleet.vehicle.use',string='Vehicle Use'),
        'degree_id': fields.many2one('hr.salary.degree',string='Degree'),
        'vehicle_id': fields.many2one('fleet.vehicle',string='Vehicle'),
        'employee_id': fields.many2one('hr.employee',string='Employee'),
        #'employees_ids': fields.many2many('hr.employee','employee_vehicle_report_rel',string='Employees'),
        'vehicle_status':fields.selection([('operation', 'Operational Use'), ('internal', 'Internal Use'),('supply_custody', 'Supply Custody'),
            ('disabled', 'Disabled'),('off', 'Off'),('custody', 'Custody'),('sold', 'Sold'),('for_sale', 'For Sale'),
            ('removal', 'Removal'),('missing', 'Missing')], 'Vehicle Status'),
        'year': fields.selection(_selection_year, 'Model'),
        'company_id': fields.many2one('res.company', 'Company'),
        'total_report': fields.boolean('Total Vehicle Report'),
        'included_department': fields.boolean('Includes sub-departments'),
        'status': fields.selection([('active', 'Active'), ('inactive', 'InActive')], 'vehicle Activation'),
        'old_system_driver': fields.char('Driver In Old System'),
        'report_type': fields.selection([('normal_report', 'Vehicles Report'),('total_report', 'Total Report'),('total_report_out', 'Total Out Report'),('total_number_report', 'Total Number Report') ], 'vehicle Activation'),
        'vehicle_type': fields.selection([('state', 'State'),('non-state', 'Non-state')], 'vehicle Type'),
        'place_id': fields.many2one('vehicle.place',string='Vehicle Place'),
        #out vehicles
        'out_driver': fields.char('Driver'),
        'out_department': fields.many2one('vehicle.out.department', 'External Department'),

    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
        'total_report': False,
        'included_department': False,
        'report_type': 'normal_report',
    }

    '''def check_date(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.date_from > rec.date_to:
                raise osv.except_osv(_('ERROR'), _('The Start Date Must Be Before or Equal To the End Date'))
            
        return True

    _constraints = [
         (check_date, '', []),
    ]'''


    def onchange_brand(self, cr, uid, ids, brand_id, context={}):
        """
        """
        vals = {}
        if brand_id:
            vals['model_id'] = False

        return {'value':vals}


    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        datas = {}
        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]
        data['employee_name'] = False
        data['employee_degree'] = False
        if 'employee_id' in data and data['employee_id']:
            emp = self.pool.get('hr.employee').browse(cr, uid,data['employee_id'][0])
            data['employee_name'] = emp.name.encode('utf-8') 
            data['employee_degree'] = emp.degree_id.name.encode('utf-8') 
        
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'fleet.vehicle',
             'form': data
             }

        #if data['total_report'] == True:
        if data['report_type'] in ['total_report']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'total_vehicle_report',
                'datas':datas,
            }
        elif data['report_type'] in ['total_report_out']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'total_out_vehicle_report',
                'datas':datas,
            }
        elif data['report_type'] in ['total_number_report']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'total_vehicle_number_report',
                'datas':datas,
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'vehicle_report',
                'datas':datas,
            }