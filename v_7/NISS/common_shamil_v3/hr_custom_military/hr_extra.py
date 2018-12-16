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

#----------------------------------------
#HR Department Status
#----------------------------------------
class hr_dep_status(osv.osv):
    _name = "hr.dep.status"
    _description = "HR Department Status"

    _columns = {
        'name': fields.char('status name', size=256),
    }
    _sql_constraints = [ ('name_unique', "unique(name)", "The Name of Department Status Must Be Unique."),  
    ]


class hr_department(osv.Model):

    _inherit = 'hr.department'

    _columns = {
        'active': fields.boolean('Active'),
        'cat_type': fields.related('cat_id','category_type',type="char",string="category type",readonly=1),
        'dep_status_id': fields.many2one('hr.dep.status', 'Status')
    }

    _defaults={
    'active':True,
    }

    def name_get_custom(self, cr, uid, ids, context=None):
        #for reports
        list_set = []
        for item in self.browse(cr, uid, ids, context=context):
            temp_name = ""
            temp_name = item.name
            if item.parent_id:
                temp_name = item.parent_id.name + '/' + temp_name
                if item.parent_id.parent_id:
                    temp_name = item.parent_id.parent_id.name + '/' + temp_name

            temp = (item.id, temp_name)
            list_set.append(temp)
		
        return ids and list_set or []


class hr_basic(osv.Model):

    _name = "hr.basic"
    _order='sequence'
    _columns = {
        'sequence': fields.integer('Sequence'),
        'name': fields.char("Name", size=64),
        'code': fields.char("Code", size=64),
        'type': fields.selection([('view', 'View'), ('normal', 'Normal')], 'Type'),
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
            idss = self.search(cr,uid, [('name', '=', rec.name),('id','!=',rec.id),('company_id','=',rec.company_id.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This name is already exisit for the company %s') % (rec.company_id.name))
        return True

    _constraints = [
         (check_name, '', []),
    ]

class hr_batch(osv.Model):

    _name = "hr.batch"
    _order='sequence'
    _columns = {
        'sequence': fields.integer('Sequence'),
        'name': fields.char("Name", size=64),
        'code': fields.char("Code", size=64),
        'type': fields.selection([('view', 'View'), ('normal', 'Normal')], 'Type'),
        'parent_id': fields.many2one('hr.batch','Parent'),
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
                ('company_id','=',rec.company_id.id)])
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
        'parent_batch':fields.many2one('hr.batch', 'Batch Group'),
        'batch':fields.many2one('hr.batch', 'Batch'),
        'placement_batch':fields.many2one('hr.batch', 'Placement Batch'),
        'parent_tribe':fields.many2one('hr.basic', 'Tribe Group'),
        'tribe':fields.many2one('hr.basic', 'Tribe'),
        'place_residence':fields.char('Place Residence', readonly=True, states={'draft':[('readonly', False)]}),
        'home_1':fields.char("Home", size=156, readonly=True, states={'draft':[('readonly', False)]}),
        'home_2':fields.char("Home2", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'home_3':fields.char("Home3", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'home_4':fields.char("Home4", size=32, readonly=True, states={'draft':[('readonly', False)]}),
    }
    def set_to_draft(self, cr, uid, ids, context=None):
        """
	    Method to change employee state to draft.	
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state == 'refuse' and rec.end_date:
                raise osv.except_osv(_('ERROR'), _('You Have To Re-employee This Employee %s') % (rec.name))
        return self.write(cr, uid, ids, {'state': 'draft', }, context=context)


    def on_change_basic(self , cr, uid ,ids , basic_id , context=None):
        res = {}
        value={}
        basic_obj = self.pool.get('hr.basic')
        if basic_id:
            basic = basic_obj.browse(cr , uid , [basic_id])[0]
            if basic.type == 'view':
                value['tribe'] = False        
        return {'value':value}

    def on_change_job(self , cr, uid ,ids , job_id , context=None):
        value={}
        if job_id:
            value['job_id'] = False        
        return {'value':value}

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

    def onchange_employment_date(self, cr, uid, ids, employment_date, context=None):
        value = {'first_employement_date': employment_date}
        return {'value': value}
