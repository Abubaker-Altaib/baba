# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields,osv
import time
import netsvc
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar



class mission_dest(osv.Model):
    """
    To add mission type to the mission object """

    _inherit = 'hr.employee.mission'
    _columns = {
        'rec_by_categ':fields.char('Mission type',size=32), 
    }
   

class service_cat(osv.Model):
    """
    To manage service category"""
    #TODO change splling mestake in object name service.catgory
    _name = 'service.catgory'
    _columns = {
        'name':fields.char('Category name',size=32,required=True), 
        'parent_id': fields.many2one('contract.category','Parent Category', select=True, ondelete='cascade'),
        'templet_id': fields.many2one('account.account.template','Account Templet',required=True),
        'code': fields.related('templet_id','code',type='char',relation='account.account.template',string='Code', store=True, readonly=True),
        'name_type': fields.many2one('account.account.type','Account_type',required=True),
        'analytic_id': fields.property('account.analytic.account',
            type='many2one', relation='account.analytic.account',
            string='Analytic account', view_load=True,
            help="When create account ratification, this account journal will used in that ratification."),

          }


class service_type(osv.Model):
    """
    To manage service type """

    _name= 'service.type'
    _columns = {
        'ser_name':fields.char('Service name',size=32), 
        'name': fields.selection([('hotel','Hotel reservation'),('meal','Order a meal'),('other','Other')],'Service type', required=True),
        'hotel_order':fields.many2one('hotel.service','Hotel Order'),
        'catg_id':fields.many2one('service.catgory','Category Name'),
        'hotel_lines':fields.one2many('hotel.service.line', 'hotel_id' , 'Employee information'),#, states={'draft': [('readonly', False)]}
        'hotel_lines_meal':fields.one2many('hotel.service.line.meals', 'meal_hotel_id' , 'Meal information'),#, states={'draft': [('readonly', False)]}
        'meal_type': fields.selection([('breakfast','Breakfast'),('lunch','Lunch'),('dinner','Dinner')],'Meal type', readonly=True),#, states={'draft': [('readonly', False)]}
        'meal_description': fields.char('Meal description', size=128 , readonly=True),#, states={'draft': [('readonly', False)]}
        'cost_service': fields.float('Cost', digits_compute= dp.get_precision('Account'),),
        'notes': fields.text('Notes', size=512),

    }
   

class hotel_service_extra(osv.Model):
    _name = "hotel.service.extra"
    _description = 'Hotel service extra'
    _columns = {
                'name': fields.char('Name', size=64,required=True ),
                'active': fields.boolean('Active', help="By unchecking the active field, you may hide this record without deleting it."),
               }
    
    _defaults = {
        'active': True,
                }  


class hotel_service(osv.Model):
    """
    To manage hotel service order """

    def create(self, cr, uid, vals, context=None):
        """
        Override to add new entry sequence for every new Hotel service Record.

        @param vals: record to be created
        @return: super create() method
          """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hotel.service')
        return super(hotel_service, self).create(cr, uid, vals, context)
    
    def changes_state(self, cr, uid, ids, vals,context=None):
        """ 
        To changes hotel service state to the state in vals.

        @vals: Dictionary that will be used in write method
        @return: Boolean True
        """        
        for order in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [order.id], vals)
        return True
    
    
    def confirmed(self, cr, uid, ids, context=None):
        """
        Workflow function to check if the service type is hotel and employee 
        information is found and then change state of hotel service order 
        to confirmed.
 
        @return: Boolean True      
        """
        for hotel_service in self.browse(cr, uid, ids,context):
                if hotel_service.service_type == 'hotel' and not hotel_service.hotel_lines:
                     raise osv.except_osv(_('No employee information !'), _('Please fill the employee information list first ..'))                

        self.write(cr, uid, ids, {'state':'confirmed'})
        return True
    
    def approve1(self, cr, uid, ids, context=None):
        """
        Workflow function to change destnation state to approve1
        and update company_id.

        @return: Boolean True       
        """
        for dest in self.browse(cr, uid, ids,context):
            self.write(cr, uid, ids, {'state':'approve1','company_id':dest.mission_id.company_id and dest.mission_id.company_id.id or dest.company_id.id})
        return True
    
    def action_cancel_draft(self, cr, uid, ids,context=None):
        """
        Changes hotel service state to draft and reset the workflow
        and create log message about this reset.
 
        @return: Boolean True
        """   
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for order_id in ids:
            # Deleting the existing instance of workflow for order
            wf_service.trg_delete(uid, 'hotel.service', order_id, cr)
            wf_service.trg_create(uid, 'hotel.service', order_id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("Hotel service order '%s' has been set in draft state.") % name
            self.log(cr, uid, id, message)
        self.changes_state(cr, uid, ids,{'state': 'draft'},context={})
        return True
    
    def approve3(self, cr, uid, ids,context=None):
        """
        Workflow function to calculate service cost and change 
        state of hotel service order to approve3.
 
        @return: Boolean True      
        """
        cost=0.0
        cat_jou = ''
        for hotel_service in self.browse(cr, uid, ids,context):
                #if hotel_service.cost <= 0:
                 #   raise osv.except_osv(_('Cost!'), _('The cost of order must be greater than zero')) 
                order=hotel_service.service_type
                if not order: 
                    raise osv.except_osv(_('Lines!'), _('Please Insert Hotel Service Lines')) 
                for order_record in order:
                    if not order_record.catg_id :
                        raise osv.except_osv(_('Category!'), _('please Insert Gategory of Your Service'))
                    if order_record.cost_service < 1 :
                       raise osv.except_osv(_('Cost!'), _('The cost of service must be greater than zero')) 
                    cost+=order_record.cost_service  
                    cat_jou=order_record.catg_id.name_type.name  
        self.write(cr, uid, ids, {'state':'approve3','cost':cost,'jou_cat':cat_jou})
        return True
    def create_financial_claim(self,cr,uid,ids,context=None):
        """ 
        Workflow function to create a financial claim and change 
        state to done.
 
        @return: Boolean True
        """   
        cost=0.0
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model')
        for hotel_record in self.browse(cr, uid, ids, context=context):
            affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','hotel.service')], context=context)
            affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
            if not affairs_account_ids:
               	raise osv.except_osv(_('Error'), _("Please enter the hotel service accounting configuration"))
            affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
            journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',hotel_record.company_id.id),('name','=',hotel_record.jou_cat)], context=context)
            journal_id = journal_ids and journal_ids[0] or affairs_account.journal_id.id
            order=hotel_record.service_type
             # Creating Voucher / Ratitication
            voucher_id = voucher_obj.create(cr, uid, {
                 'amount': hotel_record.cost,
                 #'amount_in_word':amount_to_text_ar(hotel_record.cost),
                 'type': 'ratification',
                 'date': time.strftime('%Y-%m-%d'),
                 'partner_id': hotel_record.partner_id.id,
                 'account_id' : hotel_record.partner_id.property_account_payable.id, 
                 'journal_id':journal_id, 
                 'department_id': hotel_record.department_id.id,
                 'state': 'draft',
                 'notes': hotel_record.notes,
                 'narration': 'Hotel service No : ' 
                                    }, context={})
            for order_record in order:
                account_ids = account_obj.search(cr, uid, [('company_id','=',hotel_record.company_id.id),('code','=',str(order_record.catg_id.code))], context=context)
                account_id = account_ids[0]
                # Creating Voucher / Ratitication  
                voucher_line_dict = {
                             'voucher_id':voucher_id,
                             'account_analytic_id':hotel_record.department_id.analytic_account_id.id,
                             'amount':order_record.cost_service,
                             'type':'dr',
                             'journal_id':journal_id, 
                             'name': order_record.name,
                               }
                if account_id:
                	voucher_line_dict.update({'account_id':account_id })
                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
            #################### update workflow state###############
            voucher_state = 'draft'
            if hotel_record.company_id.affairs_voucher_state : 
                voucher_state = hotel_record.company_id.affairs_voucher_state 
            if voucher_id:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
                voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
            # Selecting Voucher Number / Refernece 
                #voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context).number
            self.write(cr, uid, hotel_record.id,{'state': 'done','voucher_no':voucher_id},context=context)
            copy_attachments(self,cr,uid,[hotel_record.id],'hotel.service',voucher_id,'account.voucher', context)
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        Dublicate the hotel service record and generate sequence to the new record.

        @param default: Dictionary of fields default value
        @return: Id of the new record
        """
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, id, context=context)
        if ('name' not in default) or (picking_obj.name == '/'):
            seq_obj_name = 'hotel.service'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            default['state'] = 'draft'
            default['voucher_no'] = ''
        res = super(hotel_service, self).copy(cr, uid, id, default, context)
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        """
        Delete the hotel service record if record in draft or cancel state,
        and create log message to the deleted record.

        @return: Super unlink() method
        """
        hotel_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in hotel_orders:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a hotel service order(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'hotel.service', id, 'hotel_cancel', cr)
            hotel_order_name = self.browse(cr, uid, id, context=context).name
            message = _("Hotel service order '%s' has been deleted.") % hotel_order_name
            self.log(cr, uid, id, message)
        return super(hotel_service, self).unlink(cr, uid, unlink_ids, context=context)

    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """ Finds the the total of service cost.
        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = { 'cost': 0.0 ,
				'amount_tax': 0.0 ,
				'amount_total': 0.0}
            total_cost = 0.0
            for line in record.service_type:
                	total_cost += line.cost_service

            total_with_tax = total_without_taxes = 0.0
            total_without_taxes += total_cost

            for tax in self.pool.get('account.tax').compute_all(cr, uid, record.taxes_id, total_cost,1)['taxes']:
                    unit_tax= tax.get('amount', 0.0)
                    total_with_tax += unit_tax                
            res[record.id] = {
                'amount_tax':total_with_tax, 
                'amount_untaxed':total_without_taxes, 
                'cost':total_with_tax + total_without_taxes }
        return res
    
            
        
    STATE_SELECTION = [
        ('draft', 'Draft'),
	('confirmed', 'Waiting for department manager'),
        ('confirmed1', 'Waiting for general department manager'),
        ('approve1', 'Waiting for PRM section manager'),
        ('approve2', 'Waiting for PRM office to execution'),
        ('approve3', 'Execution is done & Waiting for create financial ratification'),
        ('done', 'Done'),
        ('cancel', 'Cancel'), ]

    _name = "hotel.service"
    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the hotel service,computed automatically when the hotel service order is created"),
    'create_date': fields.datetime('Order Date', readonly=True),
    'date' : fields.date('Service date',required=True, readonly=True, states={'draft': [('readonly', False)]}),
    'service_type': fields.one2many('service.type','hotel_order','Service type',required=True, ),
    'extra_service_id': fields.many2one('hotel.service.extra', 'Service', readonly=True, states={'draft': [('readonly', False)]}),
    'service_description': fields.char('Service description', size=128 , readonly=True, states={'draft': [('readonly', False)]}),
	'cost':fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Total Cost', multi='all',store=True),
	'amount_untaxed':fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Untax Cost', multi='all',store=True),
	'amount_tax':fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Tax', multi='all',store=True),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
    'department_id': fields.many2one('hr.department', 'Department',required=True,readonly=True, states={'draft': [('readonly', False)]}),
    'partner_id': fields.many2one('res.partner', 'Partner', states={'done': [('readonly', True)]}),
    'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True),
    'notes': fields.text('Notes', size=512),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'mission_id': fields.many2one('hr.mission.category', "Destination", size=4, required=True),
    'jou_cat': fields.char('Journal Catgory', size=64),
    'taxes_id': fields.many2many('account.tax', 'hotel_tax', 'hotel_id', 'tax_id', 'Taxes',readonly=True,states={'approve2':[('readonly',False)]}),
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'hotel service order reference must be unique !'),
		]
    
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'state': 'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'exchange.order', context=c),
        'user_id': lambda self, cr, uid, context: uid,
                }
    

class hotel_service_line(osv.Model):
    """
    To manage hotel service line"""

    _name = "hotel.service.line"
    _description = 'hotel service line'
    _columns = {
                'employee_type': fields.selection([('in_company','In company'),('out_company','Out company'),('foreigner','Foreigner')],'Employee type',required=True,),
                'employee_id': fields.many2one('hr.employee', 'Employee'),
                'degree_id': fields.related('employee_id', 'degree_id', type='many2one', relation='hr.salary.degree', string='Degree', readonly=True,store=True),
                'employee_name': fields.char('Employee Name', size=128),
                'employee_company_id': fields.many2one('res.partner','Company'),
                'foreigner_id': fields.many2one('public.relation.foreigners','Foreigner'),
                'foreigners_degree_id': fields.many2one('foreigners.degree','Degree'),
                'hotel_id': fields.many2one('service.type', 'Hotel service order'),
                'name': fields.text('Note', size=256),
               }

class hotel_service_line(osv.Model):
    """
    To manage hotel service line meals"""

    _name = "hotel.service.line.meals"
    _description = 'hotel service line meals'
    _columns = {
       'meal_hotel_id': fields.many2one('service.type', 'Hotel service order'),
       'meal_type': fields.selection([('breakfast','Breakfast'),('lunch','Lunch'),('dinner','Dinner')],'Meal type'),#, states={'draft': [('readonly', False)]}
        'meal_description': fields.char('Meal description', size=128),#, states={'draft': [('readonly', False)]}
               }
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
