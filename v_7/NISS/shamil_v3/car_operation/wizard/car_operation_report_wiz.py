# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import fields, osv


# car operation  Report Class

class car_operation_report_wiz(osv.osv_memory):

    _name = "car.operation.report.wiz"
    _description = "Car Operation Report"


    TYPE_SELECTION = [
    ('main', 'Main'),
    ('extension', 'Extension'),
 				]  

    End_Peroids = [
    ('insure_car', 'العربات المومنة'),
    ('end_insure_car', 'العربات الغير مومنة'),
                 ]  
    
    
    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
	'operation_type': fields.selection([('license', 'License'),('insurance', 'Insurance')], 'Operation Type', required=True,), 
	'type': fields.selection(TYPE_SELECTION, 'Type',),
    'end_period': fields.selection(End_Peroids, 'End period'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'car.operation',
             'form': data,
            }
        if data['end_period']== 'insure_car' and data['operation_type']== 'insurance' :
            return {
            'type': 'ir.actions.report.xml',
            'report_name': 'car_operation.report',
            'datas': datas,
                }
        elif data['end_period']== 'end_insure_car' and data['operation_type']== 'insurance':
            return {
            'type': 'ir.actions.report.xml',
            'report_name': 'car_end_operation.report',
            'datas': datas,
            
                }
        elif data['operation_type']== 'license' :
            return {
            'type': 'ir.actions.report.xml',
            'report_name': 'car_operation.report',
            'datas': datas,
                }
    
