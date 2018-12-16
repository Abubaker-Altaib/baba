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
                     ]
    _columns = {
        'office_ids':fields.many2many('office.office','office_detail_wizard_rel','detail','office_id',string='office'),
        'cat_id': fields.many2one('product.category','Category',),
        'product_id': fields.many2one('product.product','Product',),
        'department_id': fields.many2one('hr.department','Department', required="1"),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',  select=True,help='Department Which this request will executed it' ,required="1"),
    }
    
    

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
         
        context={
            'executing_agency':data['executing_agency'],
            'department_id': data['department_id'],
            'office_ids': data['office_ids'],
             
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
