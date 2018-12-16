# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


#********************************************************
# This class To Manage The bankers Insurance operations 
#********************************************************

from openerp.osv import fields,osv
import netsvc
import time
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from base_custom import amount_to_text_ar

# Class bankers_insurance

class bankers_insurance(osv.Model):

    def create(self, cr, user, vals, context=None):
        """
        Creates new entry sequence for every new bankers insurance Record
        @param cr: cursor to database
        @param user: id of current user
        @param vals: list of record to be process
        @param context: context arguments, like lang, time zone
        @return: Super create method
      	"""
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'bankers.insurance')
        return super(bankers_insurance, self).create(cr, user, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        """Method that dublicates the bankers insurance record and generate sequence to the new record
        @param default: Dict that contains some fields default value and used in the copy method
        @return: Id of the new record
        """
        if default is None:
            default = {}
        default = default.copy()
        insurance_obj = self.browse(cr, uid, id, context=context)
        if ('name' not in default) or (insurance_obj.name == '/'):
            seq_obj_name = 'bankers.insurance'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            #default['state'] = 'draft'
        res = super(bankers_insurance, self).copy(cr, uid, id, default, context)
        return res
    

    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """Functional Field Function to Finds the value of total prices of Goods.
           @param field_name: List contains name of fields that call this method
           @param arg: Extra arguement
           @return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = { 'total_amount': 0.0, 'total_cash_saved': 0.0, 'total_cash_carry': 0.0}
            total_amount = 0.0
            total_cash_saved = 0.0
            total_cash_carry = 0.0
            for line in record.bankers_insurance_lines:
                	total_amount += line.amount
                	total_cash_saved += line.cash_saved_cost
                	total_cash_carry += line.cash_carry_cost
            res[record.id]['total_amount'] = total_amount 
            res[record.id]['total_cash_saved'] = total_cash_saved 
            res[record.id]['total_cash_carry'] = total_cash_carry 
        return res

    STATE_SELECTION = [
        ('draft', 'Draft'),
	('confirmed', 'Waiting For Insurance Section to Process'),
	('insurance_confirm', 'Waiting For Admin Affaris Manager to confirm'),
        ('gm_aprrove', 'Waiting for Gm to approved'),
	('done', 'done'),
        ('cancel', 'Cancel'), ]
   

    """SHIPPING_SELECTION = [
        ('khartoum', 'Khartoum-Port'),
	('port_sudan', 'Port Sudan-Port '), ]"""

    
    _name = "bankers.insurance"
    _description = "Bank Insurance"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the bankers insurance,computed automatically when the banker insurance record is created"),
    'date' : fields.date('Date',readonly=True),
    'begin_date' : fields.date('Begin date',help="Begin date of Insurance",states={'done': [('readonly', True)]}),
    'end_date' : fields.date('End Date', help="End date of Insurance",states={'done': [('readonly', True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'total_amount': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string=' Total Amount' , store = True , multi='all', readonly=True,),
    'total_cash_saved': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string=' Total cash saved' , store = True , multi='all' , readonly=True),
    'total_cash_carry': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Total cash carry' , store = True , multi='all' , readonly=True),
    'total_insurance_cost':fields.float('Total Insurance', digits_compute=dp.get_precision('Account'),help="Total Insurance Cost",states={'done':[('readonly',True)]},),
    'department_id':  fields.many2one('hr.department', 'Department', required=True , states={'done':[('readonly',True)]},), 
    'partner_id':  fields.many2one('res.partner', 'Partner',states={'done':[('readonly',True)]},),     
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'company_id': fields.many2one('res.company','Company',readonly=True),
    'notes': fields.text('Notes', size=256,states={'done':[('readonly',True)]},),
    'bankers_insurance_lines':fields.one2many('bankers.insurance.lines', 'lines_id' , 'Bankers Details',states={'done':[('readonly',True)]},),
    'voucher_no': fields.many2one('account.voucher', 'Account Voucher',readonly=True),
    'desc': fields.char('Description', size=256,states={'done':[('readonly',True)]},),
    'operation_type': fields.selection([('main', 'Main'),('extension', 'Extension')], 'Operation Type', required=True,readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}), 

    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Bankers Insurance Reference must be unique !'),
		]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
        	'user_id': lambda self, cr, uid, context: uid,
                'state': 'draft',
		'operation_type':'main',
                #'voucher_no': lambda self, cr, uid, context: '/',
                'date': lambda *a: time.strftime('%Y-%m-%d'),
		'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'bankers.insurance', context=c),
                }



    def confirmed(self, cr, uid, ids, context=None):
        
        """
           Workflow function that changes state of bankers Insurance  To 'confirmed'. 
           @param cr: cursor to database
           @param user: id of current user
           @param ids: list of record ids to be process
           @param context: context arguments, like lang, time zone
           @return: return a result       
        """
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def insurance_confirm(self,cr,uid,ids,context=None):  
        """Workflow function that changes state of bankers Insurance  To 'insurance_confirm'.
           @return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'insurance_confirm'},context=context)
        return True

    def gm_aprrove(self,cr,uid,ids,context=None):
        """Workflow function that changes state of bankers Insurance  To 'gm_aprrove'.
           @return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'gm_aprrove'},context=context)
        return True

    def done(self,cr,uid,ids,context=None):
        """
           Workflow function that creates transfer Insurance amount to voucher and changes state To 'done'.
           @return: True
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
            affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','bankers.insurance')], context=context)
            if not affairs_model_ids:
                raise osv.except_osv(_('Error'), _("Please enter the banker insurance accounting configuration"))
            affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
            if not affairs_account_ids:
                raise osv.except_osv(_('Error'), _("Please enter the banker insurance accounting configuration"))
            affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
            accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','bankers.insurance')], context=context)
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
                 #'amount_in_word':amount_to_text_ar(record.total_insurance_cost),
                 'state': 'draft',
                 'notes': record.notes,
                 'narration': 'Bankers Insurance record No:'+record.name,
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
            copy_attachments(self,cr,uid,ids,'bankers.insurance',voucher_id,'account.voucher', context)
        return True


    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """
           Workflow function changes state To 'cancel' and write notes about the cancellation (Cancel the Bankers Insurance).
           @param notes: Note for the cancellation reason
           @return: True
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Bankers Insurance at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """
           Method that resets the Bankers Insurance to 'draft' state and delete the old workflow and create a new one.
           @return: True
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
		    self.write(cr, uid, s_id, {'state':'draft'})
		    wf_service.trg_delete(uid, 'bankers.insurance', s_id, cr)            
		    wf_service.trg_create(uid, 'bankers.insurance', s_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
           Method that deletes the bankers insurance record if record in 'draft' or 'cancel' state,
           and create log message to the deleted record
           @return: Super unlink method,
        """
        insurance_request = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for record in insurance_request:
            if record['state'] in ['draft', 'cancel']:
                unlink_ids.append(record['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry in order to delete a Bankers insurance record(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'bankers.insurance', id, 'request_cancel', cr)
            record_name = self.browse(cr, uid, id, context=context).name
            message = _("Bankers Insurance  '%s' has been deleted.") % record_name
            self.log(cr, uid, id, message)
        return super(bankers_insurance, self).unlink(cr, uid, unlink_ids, context=context)

# bankers insurance Lines

class bankers_insurance_lines(osv.Model):
    
    _name = "bankers.insurance.lines"
    _description = 'Lines of Bankers Insurance'
   
    _columns = {
    		'name': fields.text('Specification', size=256),
                'company_id':  fields.many2one('res.company', 'Company', required=True), 
                'department_id':  fields.many2one('hr.department', 'Department', required=True), 
                'employee_id':  fields.many2one('hr.employee', 'Employee', required=True),
		'amount':fields.float('Amount', digits=(18,2),required=True), 
		'cash_saved_cost':fields.float('Cash Saved', digits=(18,2),required=True),
		'cash_carry_cost':fields.float('Cash Carry', digits=(18,2),required=True),
                'lines_id': fields.many2one('bankers.insurance', 'Bankers Insurance', ondelete='cascade'),

               }



