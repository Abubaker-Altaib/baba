# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields
import time

# Rented Cars Report Class

class rented_cars_wiz(osv.osv_memory):

    _name = "rented.cars.wiz"
    _description = "Rented Cars Report"

    def _get_months(self, cr, uid, context):
       months=[(str(n),str(n)) for n in range(1,13)]
       return months

    _columns = {
        'month': fields.selection(_get_months,'Month', select=True , required=True),
        'year': fields.integer('Year', size=32,required=True),
    	'department_id':fields.many2one('hr.department', 'Department',),
    	'partner_id':fields.many2one('res.partner', 'Partner',),
        'choose_type':fields.selection([('manage','الاقسام/الادارت'),('gen_manager','الادارات العامة'),('project','المشاريع')],'Choose Type'),
    	'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    }
    _defaults = {
        'year': int(time.strftime('%Y')),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'rented.cars.wiz', context=c),

                }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'rented.cars',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'rented_cars.report',
            'datas': datas,
            }
rented_cars_wiz()
    
