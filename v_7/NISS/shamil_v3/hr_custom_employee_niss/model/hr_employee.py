# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

#from openerp.osv import osv, fields
from __future__ import division
from mx import DateTime
from openerp import tools
import time
import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
from openerp import netsvc
import openerp.addons.decimal_precision as dp
import math
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.osv.orm import except_orm



#----------------------------------------------------------
# Hr_employee Inherit
#----------------------------------------------------------
class hr_employee(osv.Model):

    _inherit = "hr.employee"

    def _curr_id(self, cr, uid, ids, name, args, context=None):
        result = {}
        user_obj = self.pool.get('res.users')
        for emp in self.browse(cr, uid, ids, context=context):
            if emp.user_id.id == uid:
                result[emp.id] = True
            else:
                result[emp.id] = False
        return result

    def _curr_id_hr(self, cr, uid, ids, name, args, context=None):
        result = {}
        user_obj = self.pool.get('res.users')
        for emp in self.browse(cr, uid, ids, context=context):
            if user_obj.has_group(cr,uid,'base.group_hr_user') or user_obj.has_group(cr,uid,'hr_custom_employee_niss.group_hr_overview_employee_data'):
                result[emp.id] = True
            else:
                result[emp.id] = False
        return result


    _columns = {
        'curr_uid': fields.function(_curr_id,type="boolean", string='current_user'),
        'curr_uid_hr': fields.function(_curr_id_hr, type="boolean", string='hr user'),
        
    }

    def _curr_user(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        if user_obj.has_group(cr,uid,'base.group_hr_user') or user_obj.has_group(cr,uid,'hr_custom_employee_niss.group_hr_overview_employee_data'):
                result = True
        
        return result


    _defaults = {
        'curr_uid_hr' : _curr_user,
    
    }


    def name_get(self, cr, uid, ids, context=None):
        """Append the employee code to the name"""
        if not ids:
            return []
        if type( ids ) is not list:
            ids = [ids]
        res = []
        #res = super(hr_employee, self).name_get(cr, uid, ids, context)
        for r in self.read(cr, uid, ids, ['name_related', 'emp_code', 'degree_id', 'otherid'],context):

            name = ''
            if r['otherid'] :
                name += u'[' + r['otherid'] + u']'
            if r['degree_id'] :
                name += u'[' + r['degree_id'][1] + u']'
            if r['name_related'] :
                name += u' ' + r['name_related']
            res.append((r['id'],name))

        return res