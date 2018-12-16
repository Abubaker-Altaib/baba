# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import fields, osv


# licensed Cars Report Class

class licensed_cars_wiz(osv.osv_memory):

    _name = "licensed.cars.wiz"
    _description = "Licensed Cars Report"


    LICENSE_TYPE_SELECTION = [
    ('main', 'Main'),
    ('extension', 'Extension'),
 				]  


    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
	'license_type': fields.selection(LICENSE_TYPE_SELECTION, 'License Type',)
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'car.operation',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'licensed_cars.report',
            'datas': datas,
            }
    
