# -*- coding: utf-8 -*-

import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _

class model_control_line(osv.Model):
    _name = "model_control.line"
    
    _columns = {
        'parent': fields.many2one('model_control', string='Parent', ondelete='cascade'),
        'model_id': fields.many2one('ir.model', string='Model'),
        'read': fields.boolean('Read'),
        'write': fields.boolean('Write'),
        'create': fields.boolean('Ctreate'),
        'unlink': fields.boolean('Delete'),
        'is_active': fields.related('parent', 'is_active', type='boolean', string='Is Active'),
        'model': fields.related('model_id', 'model', type='char', string='model name'),

    }

class model_control(osv.Model):
    _name = "model_control"
    
    _columns = {
        'name': fields.char('Name'),
        'is_active': fields.boolean('Is Active'),
        'lines_ids': fields.one2many('model_control.line', 'parent', string="Lines"),
        'company_id': fields.many2one('res.company', string='Company', ),
    }

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