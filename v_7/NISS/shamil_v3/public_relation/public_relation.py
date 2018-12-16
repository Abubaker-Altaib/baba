# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields,osv
import netsvc
import time
from openerp.tools.translate import _
from django.utils.encoding import smart_str
import openerp.addons.decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar


class foreigners_purpose(osv.Model):
    """
    To manage purpose of foreign visit """
    _name = "foreigners.purpose"
    _description = 'Foreigners purpose'
    _columns = {
                'name': fields.char('Name', size=64,required=True ),
               }
       

class foreigners_degree(osv.Model):
    """
    To manage degree of foreigners """
    _name = "foreigners.degree"
    _description = 'Foreigners degree'
    _columns = {
                'name': fields.char('Name', size=64,required=True ),
               }
       
class foreigners_procedures(osv.Model):
    """
    To manage foreigners procedures """

    _name = "foreigners.procedures"
    _columns = {
    'name': fields.char('Procedure Name', size=64, required=True),
    'save_archive' : fields.boolean('Save Archive'),
    }


class public_relation_foreigners(osv.Model):
    """
    To manage Public Relation Foreigners """

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every new Foreigners Record
        @param vals: record to be created
        @return: super create() method 
      	"""
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'public.relation.foreigners')
        return super(public_relation_foreigners, self).create(cr, user, vals, context)

    def name_get(self, cr, uid, ids, context=None):
        """
        Making Foreigner name appeare like "Name Company"
        @return: dictionary,name of all analytic account
        """
        return [(r.id, (r.foreigner_name and r.foreigner_name+'-' or'')+r.company.name)for r in self.browse(cr, uid, ids, context=context)]


    _name = "public.relation.foreigners"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the Foreigner,computed automatically when foreigner record is created"),
    'foreigner_name': fields.char('Name', size=64, required=True),
    'date_of_entry' : fields.date('Date Of Entry'),
    'type_of_stay': fields.many2one('type.of.stay','Type Of Stay'),
    'passport_number': fields.char('Passport number',required=True,size=30),
    'nationality_id': fields.many2one('res.country','Nationality',),
    'profession': fields.char('Profession', size=64,),
    'date_of_first_residence' : fields.date('Date of First residence'),
    'date_of_end_of_stay' : fields.date('Date of end of stay'),
    'foreigners_degree':  fields.many2one('foreigners.degree','Degree',help="Origin Company",size=64 , required=True),
    'company':  fields.many2one('res.partner','Company',help="Origin Company",size=64 , required=True),
    'place_of_residence': fields.char('Place of residence', size=64,),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'notes': fields.text('Notes', size=256),
    'start_date_passport' : fields.date('Passport start',help="Passport Start Date"),
    'end_date_passport' : fields.date('Passport end',help="Passport End Date"),
    'last_date_exit' : fields.date('Last Exit date'),
    'last_date_entry' : fields.date('Last Entry date'),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Foreigner Reference must be unique !'),
		]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
        	'user_id': lambda self, cr, uid, context: uid,
                }
    

class foreigners_procedures_request(osv.Model):
    """
    To manage foreigners procedures request"""

    _name = "foreigners.procedures.request"

    def create(self, cr, uid, vals, context=None):
        """
        Create new entry sequence for every new foreigners procedures request record
        @param vals: record to be created
        @return: super create() method
      	"""
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'foreigners.procedures.request')
        return super(foreigners_procedures_request, self).create(cr, uid, vals, context)
    
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('requested', 'Waiting for DM To Confirm'),
        ('confirmed', 'Waiting for Genral DM To Confirm'),
        ('second_confirmed', 'Waiting for GM To Approve'),
	    ('approved', 'Waiting for PRM Manager To Process'),
	    ('second_approved', 'Waiting for PRM office Process'),
	    ('done', 'Done'),
        ('cancel', 'Cancel'), ]

    TYPE_SELECTION = [
        ('sudanese', 'Sudanese'),
        ('foreigners', 'Foreigners'),]

    PAYMENT_SELECTION = [
    		('voucher', 'Voucher'),
    		('enrich', 'Enrich'), 
    			]


    _columns = {
	   'name': fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the Foreigner request,computed automatically when foreigner procedure request is created"),
	   'request_date' : fields.date('Request Date', readonly=True),
	   'procedure_date' : fields.date('Procedure Date',readonly=True,states={'draft':[('readonly',False)]}),
	   'department_id' : fields.many2one('hr.department', 'Department', required=True,readonly=True,states={'draft':[('readonly',False)]}),
	   'user_id':  fields.many2one('res.users', 'Responsible', readonly=True),
           'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
#	   'foreinger_ids':fields.many2many('public.relation.foreigners','foreigners_request_rel','request_id', 'foreigner_id' , 'Foreigners', required=True),
#	   'foreinger_name':fields.many2one('public.relation.foreigners', 'Foreinger Name', readonly=True),
	   'procedure_id':fields.many2one('foreigners.procedures','Procedure', required=True,readonly=True,states={'draft':[('readonly',False)]}),
	   'state': fields.selection(STATE_SELECTION,'State', readonly=True),
	   'procedure_for': fields.selection(TYPE_SELECTION,'Procedure For',help="To decide The procedure is for sudanese of foreigner",required=True,readonly=True,states={'draft':[('readonly',False)]}),
	   'notes': fields.text('Notes', size=256 ,states={'done':[('readonly',True)]}),
	   'sudanese_lines_id':fields.one2many('sudanese.procedures.lines','request_id','Sudanese',readonly=True,states={'draft':[('readonly',False)]}),
	   'foreigners_lines_id':fields.one2many('foreigners.procedures.lines','request_id','Foreigners',readonly=True,states={'draft':[('readonly',False)]}),
	   'purpose':fields.many2one('foreigners.purpose','Purpose', required=True,readonly=True,states={'draft':[('readonly',False)]}),
	   'partner_id':fields.many2one('res.partner','Partner',readonly=True,states={'second_approved':[('readonly',False)]}),
	   'total_cost':fields.float('Total cost',digits=(18,2),readonly=True,states={'second_approved':[('readonly',False)]}),
       'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True),
       'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',states={'done':[('readonly',True)]}, select=True),
       'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'second_approved':[('readonly',False)]}),

    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Procedures Request Reference must be unique !'),
		]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'state': 'draft',
		        #'voucher_no': lambda self, cr, uid, context: '/',
		        'procedure_for' : 'sudanese',
                'request_date': lambda *a: time.strftime('%Y-%m-%d'),
                'procedure_date': lambda *a: time.strftime('%Y-%m-%d'),
  		        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'foreigners.procedures.request', context=c),
                }
    def requested(self,cr,uid,ids,context=None):
        """ 
        Workflow function change state to requested and check the persons 
        concerned to complete the procedure.

	    @return: Boolean True 
        """
        for record in self.browse(cr, uid, ids, context=context):
		if record.procedure_for == 'sudanese':
			if not record.sudanese_lines_id :
				raise osv.except_osv(_('Error'), _("Please enter the Persons Concerned To complete the procedure"))

		elif record.procedure_for == 'foreigners' :
			if not record.foreigners_lines_id :
				raise osv.except_osv(_('Error'), _("Please enter the Persons Concerned To complete the procedure"))
        self.write(cr, uid, ids, {'state':'requested'},context=context)
        return True

    def confirmed(self,cr,uid,ids,context=None):
        """ 
        Workflow function change  state to confirmed.

	    @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'confirmed'},context=context)
        return True

    def second_confirmed(self,cr,uid,ids,context=None):
        """ 
        Workflow function change  state to second_confirmed.

	    @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'second_confirmed'},context=context)
        return True

    def approved(self,cr,uid,ids,context=None):
        """ 
        Workflow function change  state to approved.

	    @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'approved'},context=context)
        return True

    def second_approved(self,cr,uid,ids,context=None):
        """ 
        Workflow function change  state to second_approved.

	    @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'second_approved'},context=context)
        return True

    def done(self,cr,uid,ids,context=None):
       """ 
       Workflow function changes order state to done, chech the total_cost
       and create account  voucher with the cost.

       @return: Boolean True
       """
       account_journal_obj = self.pool.get('account.journal')   
       account_obj = self.pool.get('account.account')
       voucher_obj = self.pool.get('account.voucher')
       voucher_line_obj = self.pool.get('account.voucher.line')
       affairs_account_obj = self.pool.get('admin_affairs.account')
       affairs_model_obj = self.pool.get('admin.affairs.model')
       payment_enrich_obj = self.pool.get('payment.enrich')
       payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')
       for record in self.browse(cr,uid,ids,context=context):
        if record.total_cost < 1 : 
		    raise osv.except_osv(_('Error'), _("Please enter the Right Cost "))
        # Creating enrich
        if record.payment_selection == 'enrich':
				details = smart_str('Public Relation Request No:'+record.name+'\nProcedure For:'+record.procedure_for+'\nprocedure:'+record.procedure_id.name+'\nPurpose:'+record.purpose.name)
				#details = 'Public Relation Request No:'+record.name
				enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					'enrich_id':record.enrich_category.id,
                        		'cost': record.total_cost,
					'date':time.strftime('%Y-%m-%d'),
					'state':'draft',
                        		'name':details,
					'department_id':record.department_id.id,

                            				}, context=context)
       	 			self.write(cr, uid, ids, {'state':'done'},context=context)
        elif record.payment_selection == 'voucher' :
           affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','foreigners.procedures.request')], context=context)
           affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
           if not affairs_account_ids:
                	raise osv.except_osv(_('Error'), _("Please enter the Foreigner/sudanese request accounting configuration"))
           affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
           accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','foreigners.procedures.request')], context=context)
           account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
           journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
           if journal_ids : 
                journal_id = journal_ids[0]
           else : 
                journal_id = affairs_account.journal_id.id
           if account_ids : 
                account_id = account_ids[0]
           else : 
                account_id = affairs_account.account_id.id
                analytic_id = affairs_account.analytic_id
        # Creating Voucher 
           voucher_id = voucher_obj.create(cr, uid, {
                        'amount': record.total_cost,
                        'type': 'ratification',
                        'date': time.strftime('%Y-%m-%d'),
                        'partner_id': record.partner_id.id, 
                        'department_id': record.department_id.id ,
                        'state': 'draft',
                        'journal_id':journal_id , 
                        'narration': 'Foreigner/sudanese Request no :'+record.name,
                        'amount_in_word':amount_to_text_ar(record.total_cost),
                            }, context={})
           #voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context) 
        #Creating voucher lines
           voucher_line_dict={
                     'name': record.name,
                     'voucher_id':voucher_id,
		             'account_id':account_id,
                     'account_analytic_id':analytic_id or record.department_id.analytic_account_id.id,
                     'amount':record.total_cost,
                     'type':'dr',
                               }
           voucher_line=voucher_line_obj.create(cr,uid,voucher_line_dict)
           #################### update workflow state###############
           voucher_state = 'draft'
           if record.company_id.affairs_voucher_state : 
                voucher_state = record.company_id.affairs_voucher_state 
           if voucher_id:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
                voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
       	   copy_attachments(self,cr,uid,[record.id],'foreigners.procedures.request',voucher_id,'account.voucher', context)        
           self.write(cr, uid, ids, {'state':'done','voucher_no':voucher_id},context=context)
       return True

    def cancel(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes order state to cancel.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'cancel'},context=context)
        return True


    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes state to Draft and reset the workflow.

        @return: Boolean True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
		    self.write(cr, uid, s_id, {'state':'draft'})
		    wf_service.trg_delete(uid, 'foreigners.procedures.request', s_id, cr)            
		    wf_service.trg_create(uid, 'foreigners.procedures.request', s_id, cr)
        return True


class foreigners_procedures_lines(osv.Model):
    """
    To manage foreigners procedures lines """

    _name = "foreigners.procedures.lines"    
    _columns = {
                'name': fields.text('Specification', size=256 ),
       		'request_id': fields.many2one('foreigners.procedures.request', 'Foreginer', ondelete='cascade'),
		'foreigner_id': fields.many2one('public.relation.foreigners', 'Foreginers',),
                'foreigner_name': fields.related('foreigner_id', 'foreigner_name', type='char', relation='public.relation.foreigners', string='Foreigner Name', readonly=True,store=True),
                'passport_num': fields.related('foreigner_id', 'passport_number', type='char', relation='public.relation.foreigners', string='Passport', readonly=True,store=True),
                'citizenship': fields.related('foreigner_id', 'nationality_id', type='many2one', relation='res.country', string='citizenship', readonly=True,store=True),
                'company': fields.related('foreigner_id', 'company', type='many2one', relation='res.partner', string='company', readonly=True,store=True),
                'foreigners_degree': fields.related('foreigner_id', 'foreigners_degree', type='many2one', relation='foreigners.degree', string='Degree', readonly=True,store=True),
#		'sudanese_id': fields.many2one('hr.employee', 'Sudanese',),    
               }
       

class sudanese_procedures_lines(osv.Model):
    """
    To manage Persons Concerned To complete the procedure """    

    _name = "sudanese.procedures.lines"
    
    _columns = {
                'name': fields.text('Specification', size=256),
       		'request_id': fields.many2one('foreigners.procedures.request', 'Sudanese', ondelete='cascade'),
#		'foreigner_id': fields.many2one('public.relation.foreigners', 'Foreginers',),
		'sudanese_id': fields.many2one('hr.employee', 'Sudanese',),
		'sudanese_name':fields.related('sudanese_id','name',type='char',relation='hr.employee',string='Name',readonly=True,store=True),
		'passport_num':fields.related('sudanese_id','passport_id',type='char',relation='hr.employee',string='Passport',readonly=True,store=True),     
               }


class type_of_stay(osv.Model):
    """
    To manage Foreigner Type Of Stay """

    _name = "type.of.stay"
    
    _columns = {
                'name': fields.char('Type Of Stay Name', size=64 ,required=True),
                'code': fields.integer('Code',size=5), 
               }
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
