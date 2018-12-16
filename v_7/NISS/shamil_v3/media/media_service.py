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
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom import amount_to_text_ar as amount_to_text_ar


class media_service_category(osv.osv):
    """
    To manage media service category """

    _name = "media.service.category"
    _description = 'Media services category'
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
                'department_id': fields.many2one('hr.department', 'Department',),
               }
    _defaults = {
               'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'media.service.category', context=c),
		}
       

class media_service_type(osv.osv):
    """
    To manage media service type """

    _name = "media.service.type"
    _description = 'media services type'
    _columns = {
                'name': fields.char('Name', size=64, required=True ),
                'category_id': fields.many2one('media.service.category', 'Service category', required=True), 
                'active': fields.boolean('Active', help="By unchecking the active field, you may hide service type without deleting it."),
                'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
               }
    _defaults = {
        'active': True,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'media.service.type', context=c),
                }  
       
class media_order(osv.osv):
    """
    To manage media order and it's operations"""
    
    def create(self, cr, uid, vals, context=None):
        """
        Create new entry sequence for every new Media service Record.

        @param vals: record to be created
        @return: return a result that create a new record in the database
          """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'media.order')
        return super(media_order, self).create(cr, uid, vals, context)
    
    def changes_state(self, cr, uid, ids, vals,context=None):
        """ 
        Workflow method to Changes media service state.
 
        @vals: dict that will be used in write method
        @return: Boolean True
        """        
        for order in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [order.id], vals)
        return True
    
    def confirmed(self, cr, uid, ids, context=None):
        """
        Workflow method that Check if there any service type and then change state of media service order from draft To confirmed.
 
        @return: Boolean True      
        """
        for media in self.browse(cr, uid, ids,context):
                if not media.order_lines:
                    raise osv.except_osv(_('No service type !'), _('Please fill the service types list first ..'))                
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def is_hq(self, cr, uid, ids, context=None): 
        """ 
        Workflow method to check Head Quarter company.
        
        @return: Boolean True or False
        """            
        for record in self.browse(cr, uid, ids):
            if record.category_id.company_id.code != "HQ":
                return False
        return True
    
    def done(self, cr, uid, ids, context=None):
       """ 
       Workflow method to changes media service order state to done and 
       create account voucher.
       
       @return: Boolean True 
       """
       account_journal_obj = self.pool.get('account.journal')   
       account_obj = self.pool.get('account.account')
       voucher_obj = self.pool.get('account.voucher')
       voucher_line_obj = self.pool.get('account.voucher.line')
       affairs_account_obj = self.pool.get('admin_affairs.account')
       affairs_model_obj = self.pool.get('admin.affairs.model')
       for record in self.browse(cr,uid,ids,context=context):
		if record.execution_type == 'external':
	   		if record.total_cost < 1 : 
				raise osv.except_osv(_('Error'), _("Please enter the Right Cost "))
			#Account Configuartion for all media order
           		affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','media.order')], context=context)
           		affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
           		if not affairs_account_ids:
                		raise osv.except_osv(_('Error'), _("Please enter Media Order accounting configuration"))
           		affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
           		accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','media.order')], context=context)
           		account_ids = account_obj.search(cr, uid, [('company_id','=',record.category_id.company_id.id),('code','=',str(affairs_account.code))], context=context)
           		journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.category_id.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
           		journal_id = journal_ids and journal_ids[0] or affairs_account.journal_id.id
           		account_id = account_ids and account_ids[0] or affairs_account.account_id.id
           		analytic_id = affairs_account.analytic_id
			#Define Department & company & analytic account for normal case
			dept = record.department_id.id
			analytic_account = record.category_id.analytic_id
			company = record.company_id.id
			#Account Configuartion per media order category
        		category_accounts_ids = account_obj.search(cr, uid, [('company_id','=',record.category_id.company_id.id),('code','=',str(record.category_id.code))], context=context)
			if not category_accounts_ids : 
                		raise osv.except_osv(_('Error'), _("Please enter Media category accounting configuration")) 
			cat_account_id = category_accounts_ids[0]
			if record.category_id.company_id.code == "HQ" and  record.company_id.code != "HQ":
				dept = record.category_id.department_id.id 
				analytic_account = record.category_id.department_id.analytic_account_id.id
				company = record.category_id.company_id.id
        # Creating Voucher 
           		voucher_id = voucher_obj.create(cr, uid, {
                        	'amount': record.total_cost,
                        	'type': 'ratification',
                        	'date': time.strftime('%Y-%m-%d'),
                        	'partner_id': record.partner_id.id, 
                        	'department_id': dept ,
                        	'state': 'draft',
				'company_id' : company ,
                        	'journal_id':journal_id , 
                        	'narration': 'Media order no :'+record.name,
                        	#'amount_in_word':amount_to_text_ar(record.total_cost),
                            }, context={})
           		voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context) 
        #Creating voucher lines
           		voucher_line_dict={
                     		'name': record.name,
                     		'voucher_id':voucher_id,
		     		'account_id':cat_account_id ,
                     		'account_analytic_id':analytic_account,
                     		'amount':record.total_cost,
                     		'type':'dr',
                               }
           		voucher_line=voucher_line_obj.create(cr,uid,voucher_line_dict)
       	   		copy_attachments(self,cr,uid,[record.id],'media.order',voucher_id,'account.voucher', context)        
           		self.write(cr, uid, ids, {'voucher_no':voucher_number.number},context=context)
       self.write(cr, uid, ids, {'state':'done'},context=context)
       return True
        
    def action_cancel_draft(self, cr, uid, ids,context=None):
        """ 
        Method resets the media service order record to 'draft' , deletes the old workflow and creates a new one.
         
        @return: Boolean True
        """   
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for order_id in ids:
            # Deleting the existing instance of workflow for order
            wf_service.trg_delete(uid, 'media.order', order_id, cr)
            wf_service.trg_create(uid, 'media.order', order_id, cr)
        self.changes_state(cr, uid, ids,{'state': 'draft'},context=context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Dublicate the media service record and generate sequence to the new record.

        @param default: dict that contains fields default value
        @return res: Id of the new record
        """
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, id, context=context)
        if ('name' not in default) or (picking_obj.name == '/'):
            seq_obj_name = 'media.order'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            default['state'] = 'draft'
            default['voucher_no'] = ''
        res = super(media_order, self).copy(cr, uid, id, default, context)
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        """
        Delete the media service record if record in draft or cancel state,
        and create log message to the deleted record.

        @return: super unlink() method
        """
        media_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in media_orders:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a media service order(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'media.order', id, 'media_cancel', cr)
            media_order_name = self.browse(cr, uid, id, context=context).name
            message = _("media service order '%s' has been deleted.") % media_order_name
            self.log(cr, uid, id, message)
        return super(media_order, self).unlink(cr, uid, unlink_ids, context=context)
    
    
    STATE_SELECTION = [
        ('draft', 'Draft'),
	('confirmed', 'department manager'),
        ('confirmed1', 'general department manager'),
        ('confirmed2', 'GM approve'),
        ('approve', 'PRM section manager'),
        ('approve1', 'PRM office '),
        ('done', 'Done'),
        ('cancel', 'Cancel'), ]


    _name = "media.order"
    _rec_name = 'type_id' 
    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the media service,computed automatically when the media service order is created"),
    'create_date': fields.datetime('Order Date', readonly=True),
    'date' : fields.date('Service date',required=True, readonly=True, states={'draft': [('readonly', False)]}),
    'category_id':  fields.many2one('media.service.category', 'Service category',required=True, readonly=True, states={'draft': [('readonly', False)]}),
    'order_lines':fields.one2many('media.order.line', 'order_id' , 'Media lines', readonly=True, states={'draft': [('readonly', False)]}),
    'type_id': fields.related('order_lines', 'type_id', type='many2one', relation='media.order.line', string='Media service type', readonly=True),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'department_id': fields.many2one('hr.department', 'Department',required=True,readonly=True, states={'draft': [('readonly', False)]}),
    'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
    'execution_type': fields.selection([('internal','Internal'),('external','External')],'Execution Type'),
    'notes': fields.text('Notes', size=512 ,),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'partner_id':fields.many2one('res.partner','Partner',readonly=True,states={'approve1':[('readonly',False)]}),
    'total_cost':fields.float('Total cost',digits=(18,2),readonly=True,states={'approve1':[('readonly',False)]}),
    'voucher_no': fields.char('Voucher', size=64,readonly=True),
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'media service order reference must be unique !'),
		]
    
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'state': 'draft',
    		'voucher_no':'/',
		'execution_type':'internal',
                'user_id': lambda self, cr, uid, context: uid,
                'date': lambda *a: time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'exchange.order', context=c),
                }


class media_order_line(osv.osv):
    """
    To manage media service order line"""

    _name = "media.order.line"
    _description = 'media service order line'
    _columns = {
                'type_id':  fields.many2one('media.service.type', 'Service type',required=True,),
                'order_id': fields.many2one('media.order', 'Media service order'),
                'name': fields.text('Note', size=256),
               }
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
