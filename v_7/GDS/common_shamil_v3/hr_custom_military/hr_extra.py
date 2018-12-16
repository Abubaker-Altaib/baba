# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime
import time
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _


class hr_basic(osv.Model):

    _name = "hr.basic"
    _columns = {
        'name': fields.char("Name", size=64),
        'type': fields.selection([('view', 'View'), ('normal', 'Normal')], 'Type'),
        'data': fields.selection([('batch', 'Batch'), ('tribe', 'Tribe')], 'Data'),
        'parent_id': fields.many2one('hr.basic','Parent'),
        'company_id': fields.many2one('res.company','company'),
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

    def check_name(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            idss = self.search(cr,uid, [('name', '=', rec.name),('id','!=',rec.id),
                ('data','=',rec.data),('company_id','=',rec.company_id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This name is already exisit for the company %s') % (rec.company_id.name))
        return True

    _constraints = [
         (check_name, '', []),
    ]


#----------------------------------------
# Employee (Inherit) 
# Adding new fields & update workflow
#----------------------------------------
class hr_employee(osv.Model):

    _inherit = "hr.employee"
    _columns = {
        'parent_job_id':fields.many2one('hr.job', 'Job Group'),
        'parent_batch':fields.many2one('hr.basic', 'Batch Group'),
        'batch':fields.many2one('hr.basic', 'Batch'),
        'parent_tribe':fields.many2one('hr.basic', 'Tribe Group'),
        #'tribe':fields.many2one('hr.basic', 'Tribe'),
        'place_residence':fields.char('Place Residence', readonly=True, states={'draft':[('readonly', False)]}),
        'home_1':fields.char("Home", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'home_2':fields.char("Home2", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'home_3':fields.char("Home3", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'home_4':fields.char("Home4", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'identification_id2':fields.char('Identification',required=False, states={'draft':[('readonly', False)]}),#الرقم الوطني
        'ex_date':fields.date('External Date', readonly=True, states={'draft':[('readonly', False)]}),#تاريخ الاستخراج
        'ex_place':fields.char('External Place', readonly=True, states={'draft':[('readonly', False)]}),#مكان الاستخراج
        'name2':fields.char('Name2', readonly=True, states={'draft':[('readonly', False)]}),#الاسم
        'birthday2':fields.date('Birthday2', readonly=True, states={'draft':[('readonly', False)]}),#تاريخ الميلاد
        'birth_place2':fields.char('Birth Place2',  readonly=True, states={'draft':[('readonly', False)]}),#مكان الميلاد
        'mother_name2':fields.char('Mother Name2', readonly=True, states={'draft':[('readonly', False)]}),#اسم الوالده
    }
    
    _sql_constraints = [

        ('identification_uniqe', 'unique (identification_id2)', 'you can not create same identification_id !'),
        
    ]
