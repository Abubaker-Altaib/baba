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
                     ]
    _columns = {
        'office_ids':fields.many2many('office.office','office_sum_wizard_rel','sum','office_id',string='office'),
        'cat_ids': fields.many2many('product.category','cat_sum_wizard_rel','sum','cat_id',string='category'),
	    'product_ids' : fields.many2many('product.product','product_sum_wizard_rel','sum','product_id',string='Product'),
        'department_ids': fields.many2many('hr.department','department_sum_wizard_rel','sum','department_id',string='Department'),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',  select=True,help='Department Which this request will executed it' ,required="1"),
    }

    _defaults = {
	 
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,	
		 }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
         
        
   
        context={
            'executing_agency':data['executing_agency'],
            'department_ids': data['department_ids'],
            'office_ids': data['office_ids'],
            'product_ids': data['product_ids'],
            'cat_ids': data['cat_ids'],
             
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
