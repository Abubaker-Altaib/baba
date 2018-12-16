# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2016 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv
class asset_custody_detail(osv.osv_memory):
    _name = "asset.custody.detail"
    _description = "Custudies by Department"
    USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
    _columns = {
        'date_from': fields.date('Start Date', required="1"),
        'date_to': fields.date('End Date', required="1"),
        'office': fields.many2one('office.office','office',),
        'cat_id': fields.many2one('product.category','Category',),
        'product_id': fields.many2one('product.product','Product',),
        'department_id': fields.many2one('hr.department','Department',),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',  select=True,required="1",),
    }
    
    
    _defaults = {
	 
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,	
		 }
    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
         
        context={
            'executing_agency':data['executing_agency'],
            'department_id': data['department_id'],
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
            'report_name': 'asset.custody.detail',
            'datas': datas,
            }
asset_custody_detail()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
