# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime
from openerp.tools.translate import _
#----------------------------------------
#payroll addendum rollback
#----------------------------------------
class payroll_addendum_rollback(osv.osv_memory):

    _name= "payroll.addendum.rollback"
    _description = 'Rollback the caculation of a salary or addendum'
    _columns = {
        	'scale_ids': fields.many2many('hr.salary.scale','rollback_scale_rel','parent_id','child_id', 'Salary Scale',required=True),	
        	'year' :fields.integer("Year" , required= True ), 
                'month' :fields.selection([(n,n) for n in range(1,13)],"Month",required=True), 
                'type':fields.selection([('salary','Salary'),('addendum','Addendum')],"Type",required=True),
               }

    _defaults ={
               'year': int(time.strftime('%Y')),
                }


    def rollback(self,cr,uid,ids,context={}):
        """Method that deletes records of spacefic salary or addendum from main archive when rolback a calculated salary or addendum.
        @return: dictionary   
        """
        for rec in self.browse(cr,uid,ids,context=context):
            if rec.type=='salary':
                domain=[('in_salary_sheet','=',True),('month','=',rec.month),('year','=',rec.year),('scale_id','in',[scale.id for scale in rec.scale_ids])]
            else:
                domain=[('in_salary_sheet','=',False),('month','=',rec.month),('year','=',rec.year),('scale_id','in',[scale.id for scale in rec.scale_ids])]
            deletion_ids=self.pool.get('hr.payroll.main.archive').search(cr,uid,domain,context=context)
            if not deletion_ids:
                raise orm.except_orm(_('Sorry'), _('No Such %s In The %sth Month Year Of %s To Be Rollbacked')%(rec.type,rec.month,rec.year,))
            self.pool.get('hr.payroll.main.archive').unlink(cr, uid,deletion_ids)             
        return {}

