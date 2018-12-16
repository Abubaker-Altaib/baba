# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,osv
import time
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from base_custom import amount_to_text_ar

#----------------------------------------
# Class stock insurance
#----------------------------------------
class stock_insurance(osv.Model):
    _name = "stock.insurance"
    _description = 'Stock Insurance'

    def create(self, cr, user, vals, context=None):
        """
           Creates new entry sequence for every new stock Insurance Record
           @param vals: Dictionary contains entered data
           @return: Super create method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'stock.insurance'
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name) 
        return super(stock_insurance, self).create(cr, user, vals, context)


    def copy(self, cr, uid, id, default=None, context=None):
        """
           Method dublicates the stock Insurance record and generate sequence to the new record
           @param default: dict that contains some fields default value and used in the copy method
           @return res: Super copy method
        """
        if default is None:
            default = {}
        default = default.copy()
        insurance_obj = self.browse(cr, uid, id, context=context)
        if ('name' not in default) or (insurance_obj.name == '/'):
            seq_obj_name = 'stock.insurance'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            default['state'] = 'draft'
        res = super(stock_insurance, self).copy(cr, uid, id, default, context)
        return res
 
    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """ 
           Functional Field Function to calculates the value of total prices of insurance lines.
           @param field_name: List contains name of fields that call this method
           @param arg: Extra arguement
           @return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in record.insurance_lines:
                val += line.cost
            res[record.id] = val 
        return res
 
    
    STATE_SELECTION = [
        ('draft', 'Draft'),
	('confirmed', 'Waiting For Supply Manager to confirm'),
	('insurance_confirm', 'Waiting For Insurance Section to Process'),
        ('admin_affaris_confirm', 'Waiting For Admin Affaris Manager to confirm'),
	('gm_aprrove', 'Waiting for Gm to approved'),
	('insurance_service', 'Waiting For Final Process and Create Voucher'),
	('done', 'done'),
        ('cancel', 'Cancel'), ]   

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the stock insurance"),
    'date' : fields.date('Request Date',required=True, readonly=True,),
    'begin_date' : fields.date('Begin date',help="Begin date of Insurance",states={'done': [('readonly', True)]}),
    'end_date' : fields.date('End Date', help="End date of Insurance",states={'done': [('readonly', True)]}),
    'department_id': fields.many2one('hr.department','Department',required=True,states={'done': [('readonly', True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True  ),
    'partner_id':  fields.many2one('res.partner', 'Partner',states={'done': [('readonly', True)]}),
    'total_amount': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string=' Total Amount' , store = True , readonly=True),    
    'total_insurance_cost':fields.float('Total Insurance cost', digits_compute=dp.get_precision('Account'),states={'done': [('readonly', True)]}),
    'insurance_lines':fields.one2many('stock.insurance.line', 'insurance_id' , 'Items',states={'done': [('readonly', True)]}),
    'voucher_no': fields.many2one('account.voucher', 'Account Voucher',readonly=True), 
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'notes': fields.text('Notes', size=256 ,states={'done': [('readonly', True)]}),
    'desc': fields.char('Description', size=64, required=True,states={'done': [('readonly', True)]}),
    'operation_type': fields.selection([('main', 'Main'),('extension', 'Extension')], 'Operation Type', required=True,readonly=True,states={'draft':[('readonly',False)],'insurance_confirm':[('readonly',False)]}), 
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Stock insurance reference must be unique !'),
        ]
    
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'date': time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.insurance', context=c),
                'user_id': lambda self, cr, uid, context: uid,
		#'voucher_no':lambda self, cr, uid, context: '/',
		'operation_type':'main',
                'state': 'draft',
                }

    def confirmed(self, cr, uid, ids, context=None):
        """
           Workflow method changes the state of To 'confirmed' and checks if no lines then raises an exception 
           or if the quantity or the cost of an item is zero it raises an exception. 
           @param cr: Cursor to database
           @param user: Id of current user
           @param ids: List of record ids to be process
           @param context: Context arguments, like lang, time zone
           @return: Boolean True       
        """
        for record in self.browse(cr, uid, ids):
                if not record.insurance_lines:
                    raise osv.except_osv(_('No Stock Insurance Detaill  !'), _('Please fill the Stock Insurance lines list first ..'))
		for line in record.insurance_lines :
			if line.product_qty <=0.0 or line.cost <=0.0 :
				raise osv.except_osv(_('Error In product Cost or Qty !'), _('Please insert the right insurance product cost or qty  ..'))                
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def insurance_confirm(self,cr,uid,ids,context=None):  
        """
           Workflow method changes the state of To 'insurance_confirm'.
           @return: Boolean True       
        """
        self.write(cr, uid, ids, {'state':'insurance_confirm'},context=context)
        return True

    def admin_affaris_confirm(self,cr,uid,ids,context=None):
        """
           Workflow method changes the state To 'admin_affaris_confirm' and 
           checks if insurance cost is less than zero it raises an exception.
           @return: Boolean True       
        """
        for record in self.browse(cr, uid, ids):
               if record.total_insurance_cost <= 0.0:
                    raise osv.except_osv(_('Error In Cost!'), _('Please insert the right insurance Cost ..'))              
        self.write(cr, uid, ids, {'state':'admin_affaris_confirm'},context=context)
        return True

    def gm_aprrove(self,cr,uid,ids,context=None):
        """
           Workflow method changes the state of To 'gm_aprrove'.
           @return: Boolean True       
        """
        self.write(cr, uid, ids, {'state':'gm_aprrove'},context=context)
        return True

    def insurance_service(self,cr,uid,ids,context=None):
        """
           Workflow method changes the state of To 'insurance_service'.
           @return: Boolean True       
        """
        self.write(cr, uid, ids, {'state':'insurance_service'},context=context)
        return True

    def done(self,cr,uid,ids,context=None):
        """
           Workflow method changes the state of To 'done' and transfers the insurance cost to voucher.
           @return: Boolean True       
        """
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model') 
        for record in self.browse(cr, uid, ids, context=context):
            ar_mount_manag=0.00
            ar_mount_proj=0.00
            sum_list=0.00
            ar_total=0.00
            ar_total_pro=0.00
            list1=[]
            list2=[]
            affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','stock.insurance')], context=context)
            affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
            if not affairs_account_ids:
                raise osv.except_osv(_('Error'), _("Please enter the stock insurance accounting configuration"))
            affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
            accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','stock.insurance')], context=context)
            account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
            journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
            journal_id = journal_ids and journal_ids[0] or affairs_account.journal_id.id
            account_id = account_ids and account_ids[0] or affairs_account.account_id.id
            analytic_id = affairs_account.analytic_id 
            # Creating Voucher / Ratitication
            voucher_id = voucher_obj.create(cr, uid, {
                 'amount': record.total_insurance_cost,
                 'journal_id':journal_id , 
                 'type': 'ratification',
                 'date': time.strftime('%Y-%m-%d'),
                 'partner_id': record.partner_id.id, 
                 'department_id': record.department_id.id,
                 'state': 'draft',
                 #'amount_in_word':amount_to_text_ar(record.total_insurance_cost),
                 'notes': record.notes,
                 'narration': 'Stock Insurance record No:'+record.name,
                                    }, context={})
            voucher_line_dict = {
                             'voucher_id':voucher_id,
                             'account_analytic_id': analytic_id and analytic_id.id or record.department_id.analytic_account_id.id,
                             'amount':record.total_insurance_cost,
                             'type':'dr',
                             'name': record.name,
                               }
            if account_id:
                voucher_line_dict.update({'account_id':account_id })
            voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
            #################### update workflow state###############
            voucher_state = 'draft'
            if record.company_id.affairs_voucher_state : 
                voucher_state = record.company_id.affairs_voucher_state 
            if voucher_id:
           	wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
		voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
            # Selecting Voucher Number / Refernece 
            #voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context).number
            self.write(cr, uid, record.id,{'state': 'done','voucher_no':voucher_id},context=context)
            copy_attachments(self,cr,uid,ids,'stock.insurance',voucher_id,'account.voucher', context)
        return True


    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """
           Method changes the state of To 'cancel'  write notes about the the cancellation.
           @param notes: Note for the cancellation reason
           @return: Boolean True       
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Stock Insurance at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None): 
        """
           Method resets the Insurance record to 'draft', delete the old workflow and create a new one.
           @return: Boolean True       
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
		    self.write(cr, uid, s_id, {'state':'draft'})
		    wf_service.trg_delete(uid, 'stock.insurance', s_id, cr)            
		    wf_service.trg_create(uid, 'stock.insurance', s_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
           Method that overwrites unlink method to prevent the the deletion of stock insurance record 
           if not in 'draft' or 'cancel' state, and create log message to the deleted record.
           @return: Boolean True       
        """
        insurance_request = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for record in insurance_request:
            if record['state'] in ['draft', 'cancel']:
                unlink_ids.append(record['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry in order to delete a sea insurance record(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'stock.insurance', id, 'request_cancel', cr)
            record_name = self.browse(cr, uid, id, context=context).name
            message = _("Stock Insurance  '%s' has been deleted.") % record_name
            self.log(cr, uid, id, message)
        return super(stock_insurance, self).unlink(cr, uid, unlink_ids, context=context)

stock_insurance ()

#----------------------------------------
# Class stock insurance line
#----------------------------------------
class stock_insurance_line(osv.Model):
    
    _name = "stock.insurance.line"
    _description = 'Stock Insurance Line'

    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """Method calculates the cost of the insurance line by multiplying price and quantity .
           @return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            val = abs(record.product_qty * record.unit_price) 
            res[record.id] = val 
        return res

    _columns = { 
       'insurance_id':  fields.many2one('stock.insurance', 'Stock insurance',),
       'location_id': fields.many2one('stock.location', 'Location', required=True),
       'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
       'product_uom': fields.many2one('product.uom', 'Product UOM'),
       'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
       'unit_price':fields.float('Unit Price', digits_compute=dp.get_precision('Product UoM')),
       'cost': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='cost', 			store = True , readonly=True),   
       'name': fields.char('Notes', size=256, ),                       
               }
stock_insurance_line()
