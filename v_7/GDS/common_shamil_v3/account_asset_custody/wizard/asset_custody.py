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
class asset_custody_sum(osv.osv_memory):
    _name = "asset.custody.sum"
    _description = "Custudies by Department"
    USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
					 
    STATE_SELECTION = [
		('draft', 'New'),
		('released', 'Released'),
		('assigned', 'Assigned'),
        ('damage', 'Damage'),
	   ]	
    _columns = {
        'state_rm': fields.selection(STATE_SELECTION, 'State',  select=True),
	    'custody_type': fields.selection([('personal','Personal'),('management','Management')], string='Custody Type'),	 
        'cat_id': fields.many2one('product.category','Category',),
        'product_id': fields.many2one('product.product','Product',),
        'department_id': fields.many2one('hr.department','Department',),
        'employee_id': fields.many2one('hr.employee','Employee',),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',  select=True,required="1"),
        'date_from': fields.date('Start Date', ),
        'date_to': fields.date('End Date',),
    }

    _defaults = {
	 
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,	
		 }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
         
        
   
        context={
            'state_rm': data['state_rm'],
            'custody_type': data['custody_type'],
            'executing_agency':data['executing_agency'],
            'department_id': data['department_id'],
            'employee_id': data['employee_id'],
            'product_id': data['product_id'],
            'cat_id': data['cat_id'],
            'date_from': data['date_from'],
            'date_to': data['date_to'],
             
        }   
 
 
        datas = {
             'ids': [],
             'model': 'asset.custody',
             'form': data,
             'context':context
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'asset.custody.sum',
            'datas': datas,
            }
asset_custody_sum()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
