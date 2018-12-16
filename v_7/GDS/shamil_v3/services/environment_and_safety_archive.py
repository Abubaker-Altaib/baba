# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields
import time
import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import netsvc
from admin_affairs.copy_attachments import copy_attachments as copy_attachments


#----------------------------------------
# Class environment & Safety allowances archive
#----------------------------------------
class env_and_safety_allowances_archive(osv.Model):

    def create(self, cr, user, vals, context=None):
        """
	Mehtod overwrites creates method to creates a  new entry sequence for every environment & Safety allowances archive.
	@param vals: Dictionary contains the entered data
	@return: Super create method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'services.contracts.archive')
        return super(env_and_safety_allowances_archive, self).create(cr, user, vals, context)


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
            'name': self.pool.get('ir.sequence').get(cr, uid, 'services.contracts.archive'),
            
        })
        return super(env_and_safety_allowances_archive, self).copy(cr, uid, id, default, context)  
    

    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """ 
	Method calculates the untaxed amount, taxed amount and total amount of the services.contracts.archive record.
	@return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = { 'amount_untaxed': 0.0, 'amount_tax': 0.0, 'amount_total': 0.0}
            amount_untaxed = 0.0
            amount_tax = 0.0
            amount_total = 0.0
	    if not record.allowances_lines_after and record.allowances_lines_before:
            	for line in record.allowances_lines_before:
                	amount_untaxed += line.amount_untaxed
                	amount_tax += line.amount_tax
                	amount_total += line.amount_total
            	res[record.id]['amount_untaxed'] = amount_untaxed 
            	res[record.id]['amount_tax'] = amount_tax 
            	res[record.id]['amount_total'] = amount_total 

	    elif record.allowances_lines_after and record.allowances_lines_before :
            	for line in record.allowances_lines_after:
                	amount_untaxed += line.amount_untaxed
                	amount_tax += line.amount_tax
                	amount_total += line.amount_total
            	res[record.id]['amount_untaxed'] = amount_untaxed 
            	res[record.id]['amount_tax'] = amount_tax 
            	res[record.id]['amount_total'] = amount_total 
        return res

    def _get_months(self, cr, uid, context):
       """
	Method that returns months of year as numbers.
	@return: List Of tuple
       """
       months=[(str(n),str(n)) for n in range(1,13)]
       return months

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Waiting For Creating Ratification'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ]

    _name = "services.contracts.archive"
    _description = 'Service Allowances Archive'
    _columns = {
 	'name':fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the environment & Safety allowances archive"),
        'month': fields.selection(_get_months,'Month', select=True,readonly=True),
        'year': fields.integer('Year', size=64,readonly=True),
	'partner_id':fields.many2one('res.partner', 'Partner',readonly=True),
        'date' :fields.date('Archive date',readonly=True),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Untaxed amount', multi='all'),
	    'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Taxes', multi='all'),
        'amount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Total', multi='all'),
        'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
        'transfer': fields.boolean('Transfer',readonly=True),
  	'allowances_lines_before': fields.one2many('services.contracts.allowances.lines', 'env_allow_id_before_rate' , 'Archive line Before Rate ',states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)],'done':[('readonly',True)]}),
  	'allowances_lines_after': fields.one2many('services.contracts.allowances.lines', 'env_allow_id_after_rate' , 'Archive line After Rate',readonly=True ),
    	'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True), 
    	'notes': fields.text('Notes', size=256 ,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)],'done':[('readonly',True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ), 
    'voucher_no': fields.char('Account voucher', size=64,readonly=True),      
               }
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'date': time.strftime('%Y-%m-%d'),
                'user_id': lambda self, cr, uid, context: uid,                
    		'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'services.contracts.archive', context=c),
                'state': 'draft',
                
                }


#workflow function
    def confirmed(self, cr, uid, ids, context=None):
        """
	Workflow method changes the state to 'confirmed' and calculates contract Allowances lines based on the given rate.
	@return: Boolean True
        """
	allow_archive_line_obj = self.pool.get('services.contracts.allowances.lines')
        for record in self.browse(cr, uid, ids, context=context):
		if not record.allowances_lines_before :
                	raise osv.except_osv(_('Partner Lines !'), _('Sorry no partner Lines!'))

	 	lines_ids = [line.id for line in record.allowances_lines_after]
         	allow_archive_line_obj.unlink(cr,uid,lines_ids,context=context)

		for lines in record.allowances_lines_before:
			if lines.percentage_rating < 0 or lines.percentage_rating > 100 :
                		raise osv.except_osv(_('Rate Error !'), _('Sorry you insert wrong rate ... rate is between (0,100)!'))
           		amount_after_rate_id = allow_archive_line_obj.create(cr, uid, {
        				'cost_of_rent':lines.cost_of_rent,
        				'amount_untaxed':round (lines.amount_untaxed*lines.percentage_rating/100,2),
        				'amount_tax':round(lines.amount_tax*lines.percentage_rating/100,2),
        				'amount_total':round(lines.amount_total*lines.percentage_rating/100,2),
        				'deduct_days':lines.deduct_days,
        				'deduct_amount':lines.deduct_amount,
        				'contract_id':lines.contract_id.id,
					'env_allow_id_after_rate':record.id,
					'type': 'after',
                    'category_id':lines.category_id.id,
					'percentage_rating':lines.percentage_rating,

                                         })
		
             
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def done(self, cr, uid, ids, context=None):
        """
	Method that changes rhe state to 'done' and transfers the allowances of Contract to the voucher and creates a ratification for them .
	@return: Boolean True
        """
             
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        admin_affairs_model_obj = self.pool.get('admin.affairs.model')
        affairs_account_obj = self.pool.get('admin_affairs.account')        
        model_id = admin_affairs_model_obj.search(cr, uid, [('model','=','environment.and.safety')], context=context)[0] 
        affairs_account = affairs_account_obj.search(cr, uid, [('model_id','=',model_id)], context=context)
        if not affairs_account:
            raise osv.except_osv(_('Warning !'), _('Please insert account configuration For Environment and safety'))
        affairs_account_id = affairs_account[0]
         
        affairs_account_record = affairs_account_obj.browse(cr, uid, affairs_account_id,context=context)           
        for record in self.browse(cr, uid, ids, context=context):
            if not record.allowances_lines_after :
                raise osv.except_osv(_('Partner Amount !'), _('Sorry no partner Amount After Rate To Transfer!'))
            notes = _("Enviroment and Safety allowances Contract: %s")%(record.name)
            
            journal_id = affairs_account_record.journal_id
            analytic_id = affairs_account_record.analytic_id
            account_id = affairs_account_record.account_id

		# Creating Voucher / Ratitication
            voucher_id = voucher_obj.create(cr, uid, {
                                                      'amount': record.amount_total,
                                                      'type': 'ratification',
                                                      'date': time.strftime('%Y-%m-%d'),
                                                      'partner_id': record.partner_id.id,
                                                      'journal_id': journal_id and journal_id.id ,  
                                                      'state': 'draft',
					                                  'notes':record.notes,
					                                   'narration':notes ,
                                 	                   'company_id':record.company_id.id,
                                         })
            	# Creating Voucher / Ratitication Lines
            for line in record.allowances_lines_after:
               '''account_id =line.category_id.account_id
               if not account_id:
                   account_id = line.category_id.parent_id.account_id
                   
               if not account_id:
                   account_id = affairs_account_record.account_id   

               if not account_id:
                  raise osv.except_osv(_('Invalid action !'), _('Please insert Account configuration For Environment and safety Service')) '''                                  
                
               account_analytic_id =line.category_id.analytic_id
               if not account_analytic_id:
                   account_analytic_id = line.category_id.parent_id.analytic_id  
                                
               if not account_analytic_id:
                   account_analytic_id = affairs_account_record.analytic_id
                   
               vocher_line_id = voucher_line_obj.create(cr, uid, {
                                        'amount': record.amount_total,
                                        'voucher_id': voucher_id,
					                    'account_id':account_id and account_id.id,
					                    'account_analytic_id':account_analytic_id and account_analytic_id.id ,
                                        'type': 'dr',
                                        'name':'environment and Safety allowances :' + record.name,
                                         })
		
		# Selecting Voucher Number / Refernece 

        voucher_number = self.pool.get('account.voucher').browse(cr,uid,voucher_id)

        copy_attachments(self,cr,uid,[record.id],'services.contracts.archive',voucher_id,'account.voucher', context)
        self.write(cr, uid, ids, {'state':'done','transfer':True,'voucher_no':voucher_number.number}) 
        return True
    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """
	Method changes state of To 'cancel' and write notes about the the cancellation.
	@return: Boolean True
        """
        notes = ""
        u = self.browse(cr, uid, ids)[0].user_id.name
        notes = notes +'\n'+'Enviroment And Safety Archive Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u       
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """
	Method resets the Car conytract's allowances record to 'draft' , deletes the old workflow and creates a new one.
	@return: Boolean True       
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'services.contracts.archive', s_id, cr)            
            wf_service.trg_create(uid, 'services.contracts.archive', s_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
	Method that overwrites unlink method to prevent the the deletion of record not in 'draft' or 'cancel' state
	and creates log message for the deleted record.
	@return: Super unlink method       
        """
        allowances_archive = self.read(cr, uid, ids, ['transfer','state'], context=context)
        unlink_ids = []
        for record in allowances_archive:
            if record['transfer'] == False and record['state'] in ['draft','cancel']:
                unlink_ids.append(record['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry you can not Delete this record(s), Because The request is in Process , You have To cancelled Firest or It already Transtered To account Voucher!'))
        for id in unlink_ids:
            allowances_archive_name = self.browse(cr, uid, id, context=context).name
            message = _("Env and Safety allowances archive '%s' has been deleted.") % allowances_archive_name
            self.log(cr, uid, id, message)
        return super(env_and_safety_allowances_archive, self).unlink(cr, uid, unlink_ids, context=context)






#----------------------------------------
# enviroment and safety allowances archive lines
#----------------------------------------
class env_safety_allowances_lines(osv.Model):
    _name = "services.contracts.allowances.lines"
    _description = 'env safety Allowances Lines'
    _columns = {
	'category_id':fields.many2one('contract.category', 'Category',readonly=True,),
        'cost_of_rent':fields.float('Cost Of Rent',digits=(18,2),readonly=True),
        'amount_untaxed':fields.float('Untaxed Amount',digits=(18,2),readonly=True),
        'amount_tax':fields.float('Taxes',digits=(18,2),readonly=True),
        'amount_total':fields.float('Total',digits=(18,2),readonly=True),
        'deduct_days':fields.float('Deduct days',digits=(18,0),readonly=True),
        'deduct_amount':fields.float('Deduct amount',digits=(18,2),readonly=True),
        'contract_id': fields.many2one('environment.and.safety', 'Contract No',required=True,readonly=True),
	'env_allow_id_after_rate':fields.many2one('services.contracts.archive', 'Allowances archive',readonly=True),
	'env_allow_id_before_rate':fields.many2one('services.contracts.archive', 'Allowances archive',readonly=True),
	'type': fields.selection([('before', 'Before Rate'),('after', 'After Rate')],'Type',readonly=True),
	'percentage_rating':fields.float('Percentage Rating',digits=(18,0),),

                    }
    _defaults = {
                'percentage_rating': 100,
                }

env_safety_allowances_lines()

