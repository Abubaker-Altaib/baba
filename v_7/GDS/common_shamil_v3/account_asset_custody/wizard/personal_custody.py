# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2016 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
class asset_custody_personal(osv.osv_memory):
    _name = "asset.custody.personal"
    _description = "Custudies by Employee"
    USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
    _columns = {
        'type': fields.selection([('product', 'product'),
                                              ('category', 'category'),
                                              ('employee', 'employee'),
                                              ('department', 'department')],
                                              "Type",  ),
        'employee_id': fields.many2one('hr.employee','Employee', ),
        'department_id': fields.many2one('hr.department','Department',),
        'cat_id': fields.many2one('product.category','Category',),
        'product_id': fields.many2one('product.product','Product',),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',  select=True,required="1",),
    }
    
    
    _defaults = {
	 
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,	
		 }
    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
         
        context={
 
            'department_id':data['department_id'],
            'executing_agency':data['executing_agency'],
            'employee_id': data['employee_id'],
            'product_id': data['product_id'],
            'cat_id': data['cat_id'],
             
        }
 
        
        datas = {
             'ids': [],
             'model': 'asset.custody',
             'form': data,
             'context':context
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'asset.custody.personal',
            'datas': datas,
            }
asset_custody_personal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
