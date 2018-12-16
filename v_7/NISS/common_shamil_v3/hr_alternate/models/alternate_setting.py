# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp


class hr_alternative_setting(osv.Model):
    _name = "hr.alternative.setting"
   
    _description = "Hr Alternative Setting"

    
    _columns = {
        'name' :fields.char('Name'),
        'degrees_ids': fields.many2many('hr.salary.degree', string='Degrees'),
        'departments_ids': fields.many2many('hr.department', string='Execluded Departments'),
        'employees_ids': fields.many2many('hr.employee', string='Execluded Employees'),
        'company_id': fields.many2one('res.company','company'),
        'report_alerts': fields.text(string='Report Alerts'),
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

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]

    _sql_constraints = [
        ('hr_alternative_setting_name_uniqe', 'unique(name)', 'you can not create same name !')
    ]
