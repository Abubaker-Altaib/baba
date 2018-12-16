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
import openerp.addons.decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom import amount_to_text_ar


class occasion_services(osv.Model):
    """
    To manage Occasion Services Request & Data """

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every occasion services Record
        @param vals: record to be created
        @return: super create method
      	"""
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'occasion.services')
        return super(occasion_services, self).create(cr, user, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict 
        @return: super copy() method
        """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'occasion.services'),
            
        })
        return super(occasion_services, self).copy(cr, uid, id, default, context) 

    STATE_SELECTION = [
        ('draft', 'Draft'),
	('dept_manager', 'Waiting for Department Manager To confirm'),
	('genral_dept', 'Waiting for Department Genral Manager To confirm'),
	('gm', 'Waiting for GM to confirm'),
	('process', 'Waiting for Admin Affairs Genral Manager To process'),
	('confirmed', 'Waiting for Admin Affairs Manager To process'),
        ('service', 'Waiting for Service Manager To Process'),
        ('officer', 'Waiting for Officer To Process'),
        ('admin_outside', 'Waiting for Department of financial and administrative affairs-state'),
	('dept_manager_outside', 'Waiting for Department Manager To confirm-state'),
        ('admin_outside_process', 'Waiting for Department of financial and administrative affairs to Process-state'),
	('done', 'done'),
        ('cancel', 'Cancel'), ]

    MULI_SERVICE = [
    ('need_hospitality', 'Need Hospitality Service'),
    ('no_need_hospitality', 'No Need Hospitality'),
    ]

    def _partners_amount(self, cr, uid, ids, field_name, arg, context=None):
        """
        Functional field function to calculate occasion cost.

        @return: Dictionary of partners_cost valus       
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = { 'partners_cost': 0.0}
            val = 0.0
            for partner in order.occasion_partners:
                val += partner.cost
            res[order.id]['partners_cost'] = val        
        return res

    _name = "occasion.services"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the Occasion Services,computed automatically when occasion services record is created"),
    'date_of_request' : fields.date('Date of the Request',readonly=True),
    'execute_date' : fields.date('Execute Date',required=True , states={'confirmed':[('readonly',True)],'process':[('readonly',True)],'done':[('readonly',True)]}),
    'department_id': fields.many2one('hr.department','Department',required=True,states={'confirmed':[('readonly',True)],'process':[('readonly',True)],'done':[('readonly',True)]}),
    'occasion_type_id': fields.many2one('occasion.services.type','Occasion Services Type',required=True , states={'confirmed':[('readonly',True)],'process':[('readonly',True)],'done':[('readonly',True)]}),
#    'executing_agency_id': fields.many2one('res.partner','Executing Agency',required=True,states={'confirmed':[('readonly',True)],'process':[('readonly',True)],'done':[('readonly',True)]}),
#    'total_amount': fields.integer('Total Amount',size=10,required=True , states={'confirmed':[('readonly',True)],'process':[('readonly',True)],'done':[('readonly',True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'notes': fields.text('Notes', size=256 ,states={'done':[('readonly',True)]}),
    'account_voucher_ids': fields.many2many('account.voucher', 'occasion_service_voucher', 'occasion_id', 'voucher_id', 'Account voucher',readonly=True),
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'multi_service': fields.selection(MULI_SERVICE,'Hospitality Service', states={'confirmed':[('readonly',True)],'process':[('readonly',True)],'done':[('readonly',True)]}),
    'occasion_service_order_lines':fields.one2many('occasion.service.lines', 'line_id' , 'Service Types and Quantaties',readonly=True,states={'draft':[('readonly',False)],'dept_manager':[('readonly',False)],'genral_dept':[('readonly',False)],'gm':[('readonly',False)]}),
    'occasion_partners':fields.one2many('partner.lines', 'line_id' , 'Partners',states={'done':[('readonly',True)]}),
    'partners_cost': fields.function(_partners_amount, method=True, string='Partners cost', digits_compute=dp.get_precision('Account'),store = True , multi='all'),
    #'desc': fields.char('Description', size=128 ,select=True,readonly=True,states={'draft':[('readonly',False)]}),
    'desc': fields.text('Description', size=256 ,readonly=True,states={'draft':[('readonly',False)]}),
    'hosptality_no': fields.char('Hospitality Service', size=64,readonly=True),
    'no_day':fields.integer('Number Day',readonly=True,states={'draft':[('readonly',False)],'dept_manager':[('readonly',False)],'genral_dept':[('readonly',False)],'gm':[('readonly',False)]}),                       

    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Occasion Services Reference must be unique !'),
		]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
        	'user_id': lambda self, cr, uid, context: uid,
                'date_of_request': lambda *a: time.strftime('%Y-%m-%d'),
                'state': 'draft',
		'no_day' : 1,
                'execute_date': lambda *a: time.strftime('%Y-%m-%d'),
                'hosptality_no': lambda self, cr, uid, context: '/',
		'multi_service':'no_need_hospitality',
  		'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'occasion.services', context=c),
                }

    def dept_manager(self,cr,uid,ids,context=None):
        """
        Workflow function to change state of Occasion Service to dept_manager
        and check occasion service lines and number of days.

        @return: Boolean True       
        """
        for record in self.browse(cr, uid, ids, context=context):
		if record.multi_service == 'need_hospitality': 
			if not record.occasion_service_order_lines or record.no_day < 1:
				raise osv.except_osv(_('Error'), _("Please enter the Right Number of day OR Hospitality Service Line"))

        self.write(cr, uid, ids, {'state':'dept_manager'},context=context)
        return True

    def genral_dept(self,cr,uid,ids,context=None):
        """
        Workflow function to change state of Occasion Service to genral_dept 

        @return: Boolean True       
        """
        self.write(cr, uid, ids, {'state':'genral_dept'},context=context)
        return True

    def gm(self,cr,uid,ids,context=None):
        """
        Workflow function to change state of Occasion Service to gm 

        @return: Boolean True       
        """
        self.write(cr, uid, ids, {'state':'gm'},context=context)
        return True

    def process(self,cr,uid,ids,context=None):        
        """
        Workflow function to change state of Occasion Service to process 

        @return: Boolean True       
        """
        self.write(cr, uid, ids, {'state':'process'},context=context)
        return True


    def confirmed(self, cr, uid, ids, context=None):
        """
        Workflow function to change state of Occasion Service to confirmed 

        @return: Boolean True       
        """
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def service(self,cr,uid,ids,context=None):
        """
        Workflow function to change state of Occasion Service to service 

        @return: Boolean True       
        """
        self.write(cr, uid, ids, {'state':'service'},context=context)
        return True

    def is_hq(self, cr, uid, ids, context=None): 
        """ 
        Workflow function to check if the company is 
        head quarter company .

	    @return: Boolean True 
        """            
        for record in self.browse(cr, uid, ids):
            if record.company_id.code != "HQ":
                return False
        return True

    def admin_outside(self,cr,uid,ids,context=None):
        """ 
        Workflow function change state to admin_outside.

	    @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'admin_outside'},context=context)
        return True

    def dept_manager_outside(self,cr,uid,ids,context=None):
        """ 
        Workflow function change state to dept_manager_outside.

	    @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'dept_manager_outside'},context=context)
        return True

    def admin_outside_process(self,cr,uid,ids,context=None):
        """ 
        Workflow function change state to admin_outside_process.

	    @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'admin_outside_process'},context=context)
        return True

    def officer(self,cr,uid,ids,context=None):
        """ 
        Workflow function change state to officer.

	    @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'officer'},context=context)
        return True

    def done(self,cr,uid,ids,context=None):
        """ 
        Workflow function create hospitality service if need, 
        create account voucher with service cost and change 
        state to done.

	    @return: Boolean True 
        """
        wf_service = netsvc.LocalService("workflow")
        hospitality_service_obj=self.pool.get('hospitality.service')
        order_line_obj=self.pool.get('order.lines')
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model')
	occasion_category_obj = self.pool.get('occasion.category') 
        for record in self.browse(cr, uid, ids, context=context):
		# Hospitality Service Creation
		if record.multi_service == 'need_hospitality' : 
            		hospitality_id = hospitality_service_obj.create(cr, uid, {               
                 		'date': time.strftime('%Y-%m-%d'),
                 		'date_of_execution': record.execute_date,
                 		'company_id': record.company_id.id, 
                 		'department_id': record.department_id.id,
                 		'state': 'approved_sc',
				'no_day':record.no_day,
                 		'notes': "This is hospitality service record created From Occasion Service no:"+record.name,

                                    }, context={})
                 	for line in record.occasion_service_order_lines:
                    		order_id_dic = order_line_obj.create(cr,uid,{
                       			'service_sort':line.occasion_service_sort,
                       			'service_type':line.occasion_service_type.id,
                       			'service_qty':line.occasion_service_qty,  
                       			'order_id':hospitality_id,               
                       			 },context=context)
        		hospitality_number = hospitality_service_obj.browse(cr,uid,hospitality_id)
        		self.write(cr, uid, ids, {'hosptality_no':hospitality_number.name})
		# Account Creation & Configuration
		if not record.occasion_partners :
                	raise osv.except_osv(_('Error'), _("Please enter the Occasion Service Partners"))
        	#affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','occasion.services')], context=context)
        	#affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
        	#if not affairs_account_ids:
            #    		raise osv.except_osv(_('Error'), _("Please enter the Occasion Service accounting configuration"))
        	#affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
        	#accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','occasion.services')], context=context)
        	#account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
        	#journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
        for line in record.occasion_partners :
            if not line.occasion_category.account_id:
            	raise osv.except_osv(_('Warning !'), _('Please insert Category Account Configuration For Enviroment and safety'))
            journal_id = line.occasion_category.journal_id.id
            analytic_id = line.occasion_category.analytic_id.id
            account_id = line.occasion_category.account_id.id
        occasion_voucher = [] 
        occasion_voucher_line=[]
        cr.execute("""SELECT distinct partners_id as partner_id from partner_lines where line_id =%s """%record.id)
        partner_res=cr.dictfetchall()
        for partner in partner_res:
            cost = 0.0
            cr.execute(""" SELECT sum(cost) as total from partner_lines where line_id=%s and partners_id=%s""",(record.id,partner['partner_id']))
			#cr.execute(""" SELECT sum(cost) as total from partner_lines where line_id = %s and partners_id = %s""",(record.id,partner['partner_id']))
            res_cost=cr.dictfetchall()
            for record_cost in res_cost :
				#cost = record_cost['total']
                voucher_dict = {
                                        'type': 'ratification',
                                        'date': time.strftime('%Y-%m-%d'),
                                        'partner_id': partner['partner_id'], 
                                        'department_id': record.department_id.id,
                                        'state': 'draft',
					                    'note':record.name ,
					                    'journal_id':journal_id,
					                    'narration':'Occasion Service record No:'+record.name,
					                    'amount':record_cost['total'],
					#'amount_in_word':amount_to_text_ar(cost),
                                         }
            voucher_id = voucher_obj.create(cr, uid, voucher_dict, context={})
            occasion_voucher.append(voucher_id)
            cr.execute(""" SELECT occasion_category as occasion_category , cost as cost from partner_lines where line_id=%s and partners_id =%s""",(record.id,partner['partner_id']))
            res=cr.dictfetchall()
            for res_account in res :
				#affairs_ids = occasion_category_obj.search(cr,uid,[('id','=',res_account['occasion_category'])],context=context)
				#category_affairs_account = occasion_category_obj.browse(cr, uid, affairs_ids[0], context=context)
        			#accounts_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(category_affairs_account.code))], context=context)
        			#journals_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',category_affairs_account.name_type.name)], context=context)
        			#cate_journal_id = journals_ids and journals_ids[0]
        			#cate_account_id = accounts_ids and accounts_ids[0]
        			#cate_analytic_id = category_affairs_account.analytic_id
               			voucher_line_dict = {
                  		'account_analytic_id':analytic_id,
                  		'account_id':account_id, 
                  		'amount':res_account['cost'],
                  		'type':'dr',
                  		'name':record.name,
                  
                               }
                        	voucher_line_dict.update({'voucher_id':voucher_id})
                        	voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
            #################### update workflow state###############
            voucher_state = 'draft'
            if record.company_id.affairs_voucher_state : 
                voucher_state = record.company_id.affairs_voucher_state 
            if voucher_id:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
                voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
            copy_attachments(self,cr,uid,[record.id],'occasion.services',voucher_id,'account.voucher', context)    
        self.write(cr, uid, ids, {'state':'done','account_voucher_ids':[(6,0,occasion_voucher)]}) 
        return True
    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes order state to cancel and writes note
	    which contains Date and username who do cancellation.

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Occasion Services Record Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
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
		    wf_service.trg_delete(uid, 'occasion.services', s_id, cr)            
		    wf_service.trg_create(uid, 'occasion.services', s_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
        Delete Occasion Services record if record in draft or cancel state,
        and create log message to the deleted record.

        @return: super unlink() method
        """
        occasion_request = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in occasion_request:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry in order to delete a occasion service request(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'occasion.services', id, 'request_cancel', cr)
            record_name = self.browse(cr, uid, id, context=context).name
            message = _("occasion services '%s' has been deleted.") % record_name
            self.log(cr, uid, id, message)
        return super(occasion_services, self).unlink(cr, uid, unlink_ids, context=context)

class occasion_services_type(osv.Model):
    """
    To manage occasion services type """

    def _check_recursion(self, cr, uid, ids, context=None):

        """
        This function Checks the recursion of occasion services type parent 
        @return: True or False  
        """
        if context is None:
            context = {}
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from occasion_services_type where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _name = "occasion.services.type"
    _columns = {
    'code': fields.integer('Code',size=10,),
    'name': fields.char('Occasion Type Name', size=64,required=True),
    'parent_id': fields.many2one('occasion.services.type','Parent Occasion Service', select=True, ondelete='cascade'),
        
        'account_id': fields.property('account.account',
            type='many2one', relation='account.account',
            string='Account', view_load=True,
            help="When create account ratification, this account will used in that ratification."),
        
        'analytic_id': fields.property('account.analytic.account',
            type='many2one', relation='account.analytic.account',
            string='Analytic account', view_load=True,
            help="When create account ratification, this account journal will used in that ratification."),
          }
    _constraints = [
        (_check_recursion, 'Error! You can not create recursive Contract Category.', ['Parent Category'])
        ]


class services_lines(osv.Model):
    """
    To manage services lines """

    SERVICE_TYPE = [
    ('breakfast', 'Breakfast'),
    ('lunch', 'Lunch'),
    ('dinner', 'Dinner'),
    ]
    _name = "occasion.service.lines"
    _columns = {
                'occasion_service_type': fields.many2one('hospitality.service.type','Service Type',),
                'line_id': fields.many2one('occasion.services', 'Request Ref', ondelete='cascade'),
                'occasion_service_qty': fields.float('Quantity', digits=(16,2),),   
                'occasion_service_sort':fields.selection(SERVICE_TYPE,'Service Sort', select=True),             
                'name': fields.text('Note', size=256),
		
               }
    _defaults = {
                'occasion_service_qty': 1.0,
                }


class partner_lines(osv.Model):
    """
    To manage Partners of occasion service record """

    _name = "partner.lines"
    _description = 'Partners of license record'

    _columns = { 
       'name': fields.char('Name', size=64 ,select=True,),                       
       'partners_id':  fields.many2one('res.partner', 'Partner Name', required=True,),
       'line_id': fields.many2one('occasion.services', 'Partner Line ', ondelete='cascade'),    
       'cost': fields.float('Cost', digits_compute=dp.get_precision('Account')),
       'occasion_category' :fields.many2one('occasion.category','Occasion Category'),  
               } 

class occasion_category(osv.Model): 
    """
    To manage occasion category"""  
    _name = "occasion.category"
    _description = 'Occasion Category'

    _columns = { 
       'name': fields.char('Name', size=64 ,select=True,required=True),                       
       'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
       'templet_id': fields.many2one('account.account.template','Account Templet'),
       'code': fields.related('templet_id','code',type='char',relation='account.account.template',string='Code', store=True, readonly=True),
       'name_type': fields.many2one('account.account.type','Account Type'),
       'analytic_id': fields.property('account.analytic.account',
            type='many2one', 
            relation='account.analytic.account',
            string='Analytic account', 
            method=True, 
            view_load=True),
       'journal_id': fields.property('account.journal',
            relation='account.journal', type='many2one',
            string='Journal', view_load=True,
            help="When create account ratification, this is the Accounting Journal in which ratification will be post."),
        
       'account_id': fields.property('account.account',
            type='many2one', relation='account.account',
            string='Account', view_load=True,
            help="When create account ratification, this account will used in that ratification."),
               }
    _defaults = {
  		'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'occasion.category', context=c),
                } 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
