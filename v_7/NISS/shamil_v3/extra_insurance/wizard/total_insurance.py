# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import fields, osv


# Total Insurance Report Class

class total_insurance_wiz(osv.osv_memory):

    _name = "total.insurance.wiz"
    _description = "Report For all Insurance"

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
        'car_insurance': fields.boolean('Car Insurance'),
        'station_insurance': fields.boolean('Station Insurance'),
        'bankers_insurance': fields.boolean('Bankers Insurance'),
        'stock_insurance': fields.boolean('Stock Insurance'),
        'sea_insurance': fields.boolean('Sea Insurance'),
        'accident_cost': fields.boolean('Accident/Repayment Cost'),
    }
    _defaults = {
 		'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
                }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'bankers.insurance',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'total_insurance.report',
            'datas': datas,
            }
total_insurance_wiz()
    
