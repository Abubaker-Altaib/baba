# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from datetime import datetime
from tools.translate import _


class batch(osv.osv_memory):
    _name = "batch.wizard"

    _columns = {
        'parent_batch': fields.many2one('hr.batch', string="Batch Group"),
        'batch': fields.many2one('hr.batch', string="Batch"),
        'placement_batch': fields.many2one('hr.batch', string="Placement Batch"),
        'department_id': fields.many2one('hr.department', string="Department"),
        'with_childs': fields.boolean(string="with childs"),
        'company_id': fields.many2one('res.company','company'),
        'job_id': fields.many2one('hr.job','Job'),
        'degree_id': fields.many2one('hr.salary.degree','degree'),
    }

    def on_change_batch(self , cr, uid ,ids , batch_id , context=None):
        res = {}
        value={}
        batch_obj = self.pool.get('hr.batch')
        if batch_id:
            batch = batch_obj.browse(cr , uid , [batch_id])[0]
            if batch.type == 'view':
                value['batch'] = False 
                value['placement_batch'] = False       
        return {'value':value}

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }
    
    def print_report(self, cr, uid, ids, context={}):
        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.batch.report', 'datas': data}
            
