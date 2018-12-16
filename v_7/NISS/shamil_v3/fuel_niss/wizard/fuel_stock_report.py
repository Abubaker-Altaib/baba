# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv
import pooler
import time
from datetime import datetime,date,timedelta
from tools.translate import _

class vehicle_report_wiz(osv.osv_memory):
    """ To manage enrich report wizard """
    _name = "fuel.stock.report.wiz"

    _description = "Fuel Stock Report Wizard"

    _columns = {
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'pick_type': fields.selection([('in','Recieve'),('out','Delivery'),('both','Both')],'Type',),
        'location_id': fields.many2one('stock.location', 'Stock'),
        'locations_ids': fields.many2many('stock.location', string='Stock'),
        'product_id': fields.many2one('product.product', 'Product'),
        #'departments_ids': fields.many2many('hr.department','departments_vehicle_report_rel',string='Departments'),
        'company_id': fields.many2one('res.company', 'Company'),
        'maintenance': fields.boolean('Maintenance'),
        'fuel': fields.boolean('Fuel'),
        'content': fields.boolean('Content'),
        'details': fields.boolean('Details'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
        'maintenance': 0,
        'fuel': 0,
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        datas = {}
        if context is None:
            context = {}

        rec = self.browse(cr, uid, ids[0])
        data = self.read(cr, uid, ids)[0]
        #location_obj = pooler.get_pool(cr.dbname).get('stock.location')
        #location_name = location_obj.read(cr, uid, [rec.location_id.id],['name'])[0]['name']
        #data['location_name'] = location_name
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'stock.picking',
             'form': data
             }
        if rec.fuel == True:
            if rec.details and rec.pick_type == 'in':
                return {'type': 'ir.actions.report.xml', 
                        'report_name': 'fuel.fuel_in_details.report', 
                        'datas': data}
            if not (rec.details and rec.pick_type == 'in') :
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'fuel_stock_report',
                    'datas':datas,
                }
        '''if rec.maintenance == True:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'maintenance_stock_report',
                'datas':datas,
            }'''
        if rec.content == True:
            datas['model'] = 'stock.location'
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'fuel_stock_content_report',
                'datas':datas,
            }