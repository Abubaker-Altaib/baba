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
    _name = "fuel.slice.report.wiz"

    _description = "Fuel Slice Report Wizard"

    def _selection_year(self, cr, uid, context=None):
        """
        Select car manufacturing year between 1970 and Current year.

        @return: list of years 
        """
        return [(str(years), str(years)) for years in range(int(datetime.now().year) + 1, 1970, -1)]

    _columns = {
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'process_type': fields.selection([('modify','Modify'),('insert','Insert')],'Process Type'),
        'department_id': fields.many2one('hr.department',string='Department'),
        'category_id': fields.many2one('vehicle.category',string='Vehicle Category'),
        'year': fields.selection(_selection_year, 'Model'),
        'included_department': fields.boolean('Includes sub-departments'),
        'company_id': fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
        'included_department': False,
    }

    def check_date(self, cr, uid, ids, context=None):
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
    ]


    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        datas = {}
        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]
        
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'vehicle.fuel.slice',
             'form': data
             }

        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'fuel_slice_report',
                'datas':datas,
            }

        #if data['total_report'] == True:
        '''if data['report_type'] in ['total_report']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'total_vehicle_report',
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
            }'''