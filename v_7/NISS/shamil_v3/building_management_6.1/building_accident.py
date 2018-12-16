# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields,osv
import time
import netsvc
from tools.translate import _
import decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments

#************************************************************
# This class To Manage the Buliding accident
#************************************************************
# Class Buliding accident 


class building_accident(osv.osv):

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every building accident Record
        @param cr: cursor to database
        @param user: id of current user
        @param vals: list of record to be process
        @param context: context arguments, like lang, time zone
        @return: return a result 
      	"""
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'building.accident')
        return super(building_accident, self).create(cr, user, vals, context)


    def copy(self, cr, uid, id, default=None, context=None):
        """ Override copy function to edit sequence """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'building.accident'),
        })
        return super(building_accident, self).copy(cr, uid, id, default, context)

    CATEGORY_SELECTION = [
    ('car', 'Cars'),
    ('building', 'Building '),
    ('station', 'Station'),
    ('other', 'Other'), ]

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('section', 'Waiting for service section manager to confirm '),
    ('approve', 'Waiting for Insurance section manager to confirm '),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ]    


    _name = "building.accident"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the building accident,computed automatically when occasion services record is created"),
    'date' : fields.date('Date',readonly=True),
    'accident_date' : fields.date('Accident Date',required=True ,states={'done':[('readonly',True)]}),
    'building_id': fields.many2one('building.manager','Building',states={'done':[('readonly',True)]}),
    'station_id': fields.many2one('building.manager','Station',states={'done':[('readonly',True)]}),
    'car_id': fields.many2one('fleet.vehicles','Car',states={'done':[('readonly',True)]}),
    'station_company_id':  fields.related('station_id', 'company_id', type='many2one', relation='res.company',store=True, string='Station Company', readonly=True ),
    'building_company_id':  fields.related('building_id', 'company_id', type='many2one', relation='res.company',store=True, string='Building Company', readonly=True ),
    'car_department_id':  fields.related('car_id', 'department_id', type='many2one', relation='hr.department',store=True, string='Department', readonly=True ),
    'accident_type_id': fields.many2one('accident.type','Accident Type',required=True ,states={'done':[('readonly',True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'accident_desc': fields.text('Accident Description', size=256 ,states={'done':[('readonly',True)]}),
    'maintenance_desc': fields.text('Maintenance Description', size=256 ,states={'done':[('readonly',True)]}),
    'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
    'accident_category': fields.selection(CATEGORY_SELECTION,'Category', select=True,states={'done':[('readonly',True)]}),
    'accident_location': fields.char('Accident Location', size=128,states={'done':[('readonly',True)]}),
    'estimated_cost':fields.float('Estimated Cost',size=64,states={'done':[('readonly',True)]}),
    'notify_insurance_date' : fields.date('Insurance Date',help="This is the date you notify The Insurance Company",states={'done':[('readonly',True)]}),
    'notify_workshop_date' : fields.date('Workshop Date',help="This is the date you notify The maintance Workshop",states={'done':[('readonly',True)]}),
    'coverage_date' : fields.date('Coverage Date',states={'done':[('readonly',True)]}),
    'repayment_cost':fields.float('Repayment Cost',size=64,states={'done':[('readonly',True)]}),
    'partner_id':fields.many2one('res.partner','Partner',states={'done':[('readonly',True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),

    }
    _sql_constraints = [
        ('accident_name_uniq', 'unique(name)', 'Building Accident Reference must be unique !'),
		]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
        	'user_id': lambda self, cr, uid, context: uid,
                'date': lambda *a: time.strftime('%Y-%m-%d'),
		'state':'draft',
		'accident_category':'car',
 		'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
                }

    def section(self, cr, uid, ids, context=None):             
        self.write(cr, uid, ids, {'state':'section'})
        return True

    def approve(self, cr, uid, ids, context=None):             
        self.write(cr, uid, ids, {'state':'approve'})
        return True

    def done(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'done'},context=context)
        return True
    def cancel(self, cr, uid, ids, context=None):
        # Cancel Building Accident  
        #if not notes:
#        notes = ""
#        u = self.pool.get('res.users').browse(cr, uid,uid).name
#        notes = notes +'\n'+'Building Accident Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        # Reset the Building Accident 
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            self.write(cr, uid, id, {'state':'draft'})
            wf_service.trg_delete(uid, 'building.accident', id, cr)
            wf_service.trg_create(uid, 'building.accident', id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """delete the Building Accident record,
        and create log message to the deleted record
        @return: res,
        """
        buliding_accedint = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in buliding_accedint:
            if t['state'] in ['draft','cancel']:
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a building accident record, you must first cancel it, or in draft state .'))
        for id in unlink_ids:
            buliding_accedint_name = self.browse(cr, uid, id, context=context).name
            message = _("Buliding Accident '%s' has been deleted.") % buliding_accedint_name
            self.log(cr, uid, id, message)
        return super(building_accident, self).unlink(cr, uid, unlink_ids, context=context)



building_accident()

# Accident Type Configuration

class accident_type(osv.osv):
    
    _name = "accident.type"
    _description = 'Accident Type'
    
    _columns = {
                'name': fields.char('Accident Type', size=64 ,required=True),
                'code': fields.integer('Code',size=5), 
               }
       
accident_type()

