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


class tribe(osv.osv_memory):
    _name = "tribe.wizard"

    _columns = {
        'parent_tribe': fields.many2one('hr.basic', string="Tribe Group"),
        'tribe': fields.many2one('hr.basic', string="Tribe"),
        'department_id': fields.many2one('hr.department', string="Department"),
        'with_childs': fields.boolean(string="with childs"),
        'company_id': fields.many2one('res.company','company'),
        'job_id': fields.many2one('hr.job','Job'),
        'degree_id': fields.many2one('hr.salary.degree','degree'),
    }

    def on_change_basic(self , cr, uid ,ids , basic_id , context=None):
        res = {}
        value={}
        basic_obj = self.pool.get('hr.basic')
        if basic_id:
            basic = basic_obj.browse(cr , uid , [basic_id])[0]
            if basic.type == 'view':
                value['tribe'] = False        
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
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.tribe.report', 'datas': data}
            
