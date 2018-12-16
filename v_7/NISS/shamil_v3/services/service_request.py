# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields
import netsvc
import time
from datetime import datetime,date,timedelta
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
#from django.utils.encoding import smart_str
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom import amount_to_text_ar

#
# Model definition
#
class service_request_category(osv.osv):
    _name = "service.request.category"
    _description = 'Services Request Category'
    _columns = {
                'name': fields.char('Name', size=64,required=True ),
                'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
       		'templet_id': fields.many2one('account.account.template','Account Templet'),
       		'code': fields.related('templet_id','code',type='char',relation='account.account.template',string='Code', store=True, readonly=True),
       		'name_type': fields.many2one('account.account.type','Account Type'),
       		'analytic_id': fields.property('account.analytic.account',
            		type='many2one', 
            		relation='account.analytic.account',
            		string='Analytic account', 
            		method=True, 
            		view_load=True),
               }
    _defaults = {
               'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'service.request.category', context=c),
		}
       

  
class  service_request(osv.osv):

    def create(self, cr, user, vals, context=None):
        """
	Creates new entry sequence for every service request
	@param vals: Dictionary contains the entered data
	@return: Super create method
          """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'service.request')
        return super(service_request, self).create(cr, user, vals, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
	Mehtod overwrites copy method duplicates the value of the given id and updates the value of sequence fields.
	@param default: Dictionary of data    
	@return: Super copy method
        """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'service.request'),
            
        })
        return super(service_request, self).copy(cr, uid, id, default, context)    
    
    def unlink(self, cr, uid, ids, context=None):
        """
	Method that overwrites unlink method to prevent the the deletion of record not in 'draft' or 'cancel' state
	and creates log message for the deleted record.
	@return: Super unlink method       
        """
        service_request = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in service_request:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a service request order(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'service.request', id, 'cancel', cr)
            service_request_name = self.browse(cr, uid, id, context=context).name
            message = _("service request order '%s' has been deleted.") % service_request_name
            self.log(cr, uid, id, message)
        return super(service_request, self).unlink(cr, uid, unlink_ids, context=context)

    STATE_SELECTION = [
    		('draft', 'Draft'),
    		('confirmed_d', 'Waiting for department manager To confirm'),
    		('confirmed', 'Waiting admin affairs manager to approve '),
    		('approved_gn', 'Waiting for admin  affairs  service manager to approve'),
    		('approved_sc', 'Waiting for admin affairs service officer / Department of financial and administrative affairs'),
    		('done', 'Done'),
    		('cancel', 'Cancel'), 
    			]

    PAYMENT_SELECTION = [
    		('voucher', 'Voucher'),
    		('enrich', 'Enrich'), 
    			]
    
    _name = "service.request"
    _description = 'Service Request'
    _order = "name desc"
    
    _columns = {
	    'name':fields.char('Reference', size=64, required=False, select=True, readonly=True  , help="unique number of the service request"),
	    'date' :fields.date('Date of request',readonly=True),
	    'department_id':fields.many2one('hr.department', 'Department',readonly=True,states={'draft':[('readonly',False)],'approved_sc':[('readonly',False)],}, ),
	    'date_of_execution':fields.date('Date of Execution',readonly=True,states={'draft':[('readonly',False)],'approved_sc':[('readonly',False)],},help="The Request must be befor 48 hours"),
	    'partner_id': fields.many2one('res.partner','Executing Agency',readonly=True,states={'approved_sc':[('readonly',False)]}),
	    'cost':fields.float('Cost', digits=(16,2),states={'done':[('readonly',True)]}),
	    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
	    'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',states={'done':[('readonly',True)]}, select=True),
	    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
	    'notes': fields.text('Notes', size=256 ,states={'done':[('readonly',True)]}),
	    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    	    'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True),
	    'service_category':fields.many2one('service.request.category','service category',readonly=True,states={'draft':[('readonly',False)],'approved_sc':[('readonly',False)],},help="The Request must be befor 48 hours"),
	    'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'approved_sc':[('readonly',False)]}),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Service Request Reference must be unique !'), 
                        
        ]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'user_id': lambda self, cr, uid, context: uid,
                'date': time.strftime('%Y-%m-%d'),
		#'voucher_no':'/',
                #'date_of_execution': time.strftime('%Y-%m-%d'),
                'state': 'draft',
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'service.request', context=c),

                }
    """ Workflow Functions"""
    
    def confirmed_d(self, cr, uid, ids,alarm='',context=None):
        """
	Workflow method changes the state to 'confirmed_d'.
	@return: Boolean True
        """  
        self.write(cr, uid, ids, {'state':'confirmed_d'})
        return True

    def confirmed(self, cr, uid, ids,context=None):  
        """
	Workflow method changes the state to 'confirmed'.
	@return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True 

    def approved_gn(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'approved_gn'.
	@return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'approved_gn'},context=context)
        return True

    def approved_sc(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'approved_sc'.
	@return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'approved_sc'},context=context)
        return True

    def is_hq(self, cr, uid, ids, context=None):  
        """
	Mehtod that checks if the company code is 'HQ' or not.
	@return: Boolean True or False
        """           
        for record in self.browse(cr, uid, ids):
            if record.company_id.code != "HQ":
                return False
        return True

    def done(self,cr,uid,ids,context=None):
       """
	Workflow method changes the state to 'done' and transfer the amount to the voucher.
	@return: Boolean True
       """
       account_journal_obj = self.pool.get('account.journal')   
       account_obj = self.pool.get('account.account')
       voucher_obj = self.pool.get('account.voucher')
       voucher_line_obj = self.pool.get('account.voucher.line')
       affairs_account_obj = self.pool.get('admin_affairs.account')
       affairs_model_obj = self.pool.get('admin.affairs.model')
       account_period_obj = self.pool.get('account.period')
       payment_enrich_obj = self.pool.get('payment.enrich')
       payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')
       details = ''
       paid = 0.0
       residual = 0.0
       for record in self.browse(cr,uid,ids,context=context):
	   		if record.cost < 1 : 
				raise osv.except_osv(_('Error'), _("Please enter the Right Cost "))
			if record.payment_selection == 'enrich':
				paid = (record.enrich_category.paid_amount + record.cost)
				residual = (record.enrich_category.residual_amount - record.cost)
				enrich_payment_id = cr.execute("""update payment_enrich set paid_amount=%s , residual_amount=%s where id =%s""",(paid,residual,record.enrich_category.id))
				#details = smart_str('Service Request No:'+record.name+'\n'+record.service_category.name)
				details = 'Service Request No:'+record.name
				enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					'enrich_id':record.enrich_category.id,
                        		'cost': record.cost,
					'date':record.date,
                        		'name':details,
					'department_id':record.department_id.id,

                            				}, context=context)
			else :
                                period= account_period_obj.find(cr, uid, dt=record.date_of_execution,context=context)[0]
			#Account Configuartion for service request
           			affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','service.request')], context=context)
           			affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','in',affairs_model_ids)], context=context)
           			if not affairs_account_ids:
                			raise osv.except_osv(_('Error'), _("Please enter service request accounting configuration"))
           			affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids, context=context)
           			accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','service.request')], context=context)
           			account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account[0].code))], context=context)
           			journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account[0].name_type.name)], context=context)
           			journal_id = journal_ids and journal_ids[0] or affairs_account[0].journal_id.id
           		        account_id = account_ids and account_ids[0] or affairs_account[0].account_id.id
           			analytic_id = affairs_account[0].analytic_id
			        #Account Configuartion per service request category
        			category_accounts_ids = account_obj.search(cr, uid, [('company_id','=',record.service_category.company_id.id),('code','=',str(record.service_category.code))], context=context)
				if not category_accounts_ids : 
                			raise osv.except_osv(_('Error'), _("Please enter service request category accounting configuration")) 
				cat_account_id = category_accounts_ids[0]
				analytic_account = record.service_category.analytic_id.id
        # Creating Voucher
				if record.service_category.company_id.code =="HQ":  
           				voucher_id = voucher_obj.create(cr, uid, {
                        		'amount': record.cost,
                        		'type': 'ratification',
                        		'date': time.strftime('%Y-%m-%d'),
                        		'partner_id': record.partner_id.id, 
                        		'department_id': record.department_id.id ,
                        		'state': 'draft',
					'company_id' : record.company_id.id ,
                        		'journal_id':journal_id , 
                        		'narration': 'Service Request no :'+record.name,
                        		'amount_in_word':amount_to_text_ar(record.cost),
                            				}, context={})
           				voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context) 
        #Creating voucher lines
           				voucher_line_dict={
                     			'name': record.name,
                     			'voucher_id':voucher_id,
		     			'account_id':cat_account_id ,
                     			'account_analytic_id':analytic_account,
                     			'amount':record.cost,
                     			'type':'dr',
                               			}
           				voucher_line=voucher_line_obj.create(cr,uid,voucher_line_dict)
				else : 
           				voucher_id = voucher_obj.create(cr, uid, {
                 			'company_id':record.service_category.company_id.id,
                			'journal_id':journal_id,
                			'account_id':cat_account_id,
                			'period_id': period,
					'amount':record.cost,
					'partner_id':record.partner_id.id,
                			'name': record.name,
					'currency_id':43,
                			'type':'purchase',
                			'date': record.date_of_execution,
                			'reference':'Service Request' + record.name + '  /  ' + record.service_category.company_id.name + '  /  ' + record.date_of_execution,
	 				'narration': 'Service Request No:'+record.name,
                            				}, context={})
           				voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context) 
        #Creating voucher lines
           				voucher_line_dict={
                     			'name': record.name,
                     			'voucher_id':voucher_id,
		     			'account_id':cat_account_id ,
                     			'account_analytic_id':analytic_account,
                     			'amount':record.cost,
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
       	   			copy_attachments(self,cr,uid,[record.id],'service.request',voucher_id,'account.voucher', context)        
           			self.write(cr, uid, ids, {'voucher_no':voucher_id},context=context)
       self.write(cr, uid, ids, {'state':'done'},context=context)
       return True

    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """
	Method resets the  record to 'cancel'.
	@return: Boolean True       
        """
        # Cancel the Hospitality services 
        #if not notes:
        #notes = ""      
        #u = self.pool.get('res.users').browse(cr, uid,uid).name
        #notes = notes +'\n'+'Hospitality services Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        #self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """
	Method resets the  record to 'draft' , deletes the old workflow and creates a new one.
	@return: Boolean True       
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'service.request', s_id, cr)            
            wf_service.trg_create(uid, 'service.request', s_id, cr)
        return True

