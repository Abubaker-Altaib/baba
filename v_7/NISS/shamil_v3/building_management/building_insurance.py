# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,orm
import time
from openerp.tools.translate import _
import netsvc
import decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments

#----------------------------------------
# Class building insurance
#----------------------------------------
class building_insurance(orm.Model):
    """
    To manage building insurance """

    _name = "building.insurance"
    _description = 'building insurance'

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every new building insurance Record.

        @param vals: record to be created
        @return: super create() method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'building.insurance'
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name) 
        return super(building_insurance, self).create(cr, user, vals, context) 
 
    def _total_cost(self, cr, uid, ids, field_name, arg, context={}):
        """ 
        Functional field function to finds the the total of insurance cost.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in record.insurance_lines:
                val += line.cost
            res[record.id] = val 
        return res
    
    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), ]    

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the building insurance"),
    'date' : fields.date('Date',required=True, readonly=True,),
    'begin_date' : fields.date('Insurance date', required=True , states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'end_date' : fields.date('End Date', required=True , states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True  ),
    'partner_id':  fields.many2one('res.partner', 'Partner',required=True,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),    
    'total_cost':fields.float('Total cost',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'insurance_lines':fields.one2many('building.insurance.line', 'insurance_id' , 'Items', readonly=True, states={'draft':[('readonly',False)],'confirmed':[('readonly','False')]}),
    'insurance_cost_lines':fields.one2many('building.insurance.cost.line','line_id','Cost',readonly=True, states={'draft':[('readonly',False)]}),
    'company_id': fields.many2one('res.company','Company',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'total_cost': fields.function(_total_cost, string='Total cost', readonly=True),    
    'notes': fields.text('Notes', size=256 , readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly','False')]}), 
    'transfer': fields.boolean('Transfer',readonly=True),
    'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True), 
}
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Building insurance reference must be unique !'),
        ('date_check', 'CHECK (begin_date <= end_date)', "The start date must be anterior to the end date."),
        ]
    
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'date': time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'building.insurance', context=c),
                'state': 'draft',
                'user_id': lambda self, cr, uid, context: uid,
		        #'voucher_no':lambda self, cr, uid, context: '/',
                }
    
    def confirmed(self, cr, uid, ids, context=None): 
        """
        Workflow function to change the state to confirmed and 
        check insurance lines.

        @return: Boolean True 
        """                  
        for order in self.browse(cr, uid, ids, context=context):
            if not order.insurance_lines:
                raise orm.except_orm(_('Error !'), _('You can not confirm this order without insurance lines.'))
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def done(self,cr,uid,ids,context=None):
        """
        Workflow function to change the state to done and 
        create ratification for Building insurance.

        @return: Boolean True 
        """
        wf_service = netsvc.LocalService("workflow")
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model')
        for record in self.browse(cr,uid,ids,context=context):
            affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','building.insurance')], context=context)
            affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
            if not affairs_account_ids:
                	raise orm.except_orm(_('Error'), _("Please enter the Building Insurance accounting configuration"))
            affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
            accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','building.insurance')], context=context)
            account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
            journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
            journal_id = affairs_account.journal_id.id
            account_id = affairs_account.account_id.id
            analytic_id = affairs_account.analytic_id.id
            build_dict={'state':'done'}
            for line in record.insurance_cost_lines:
                voucher_id = voucher_obj.create(cr, uid, {                                 
                                 'company_id':record.company_id.id,
                                 'journal_id':journal_id and journal_id, 
                                 'name': 'Building/Insurance/' + ' - ' + str(record.date),
                                 'type':'ratification',
                                 'reference':'Building/Insurance/' ,
                                 #'department_id': record.department_id.id,
                                 'partner_id' : record.partner_id.id,
                                 'amount':line.cost,
                                 'payment_term':line.payment_term.id,
                                 'payment_rate_currency_id':line.currency.id,
                                 'narration' : 'Building insurance No:  ' + record.name + 'Currancy: ' + line.currency.name,
                                         })  
                  
                  
                # Creating Voucher / Ratitication Lines
                voucher_line_obj.create(cr, uid, {
                                        'amount': line.cost,
                                        'account_id':account_id,
                                        'account_analytic_id':analytic_id,
                                        'voucher_id': voucher_id,
                                        'type': 'dr',
                                        'name':'Building Insurance order: ' + record.name,
                                         })
                #voucher_number = self.pool.get('account.voucher').browse(cr,uid,voucher_id)
                #################### update workflow state###############
                voucher_state = 'draft'
                if record.company_id.affairs_voucher_state : 
                    voucher_state = record.company_id.affairs_voucher_state 
                if voucher_id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
                    voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
                copy_attachments(self,cr,uid,[record.id],'building.insurance',voucher_id,'account.voucher', context)
                build_dict.update({'voucher_no':voucher_id,'transfer':True,})
            self.write(cr, uid, ids, build_dict ,context=context)
        return True

    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes order state to cancel and writes note
	    which contains Date and username who do cancellation.

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        user_obj = self.pool.get('res.users')
        for record in self.browse(cr, uid, ids,context=context):
            notes = record.notes or ""
            user_name = user_obj.browse(cr, uid, uid).name
            notes += 'This record cancelled at : ' + time.strftime('%Y-%m-%d') + ' by '+ user_name + '\n'
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes order state to Draft and reset the workflow.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for record_id in ids:
            self.write(cr, uid, record_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'building.insurance', record_id, cr)            
            wf_service.trg_create(uid, 'building.insurance', record_id, cr)
        return True

    def copy(self, cr, uid, ids, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict 
        @return: super copy() method  
        """
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, ids, context=context)
        if ('name' not in default) or (picking_obj.name == '/'):
            seq_obj_name = 'building.insurance'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        return super(building_insurance, self).copy(cr, uid, ids, default, context)

    def unlink(self, cr, uid, ids, context=None):
        """ 
        Ovrride to add constain on deleting the records. 

        @return: super unlink method
        """
        states = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for state in states:
            if state['state'] in ('draft','cancel'):
                unlink_ids.append(state['id'])
            else:
                raise orm.except_orm(_('Invalid action !'), _('In order to delete a building insurance order, you must first cancel it or set to draft.'))
        orm.orm.unlink(self, cr, uid, unlink_ids, context=context)
        return True
    def action_create_ratification(self,cr,uid,ids,context={}):
        """
        Create ratification for Building insurance.
  
        @return: Dictionary 
        """
        wf_service = netsvc.LocalService("workflow")
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model')
        for record in self.browse(cr,uid,ids,context=context):
            affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','building.insurance')], context=context)
            affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
            if not affairs_account_ids:
                	raise orm.except_orm(_('Error'), _("Please enter the Building Insurance accounting configuration"))
            affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
            accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','building.insurance')], context=context)
            account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
            journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
            journal_id = journal_ids[0]
            account_id = account_ids[0]
            analytic_id = affairs_account.analytic_id
            for line in record.insurance_cost_lines:
                voucher_id = voucher_obj.create(cr, uid, {                                 
                                 'company_id':record.company_id.id,
                                 'journal_id':journal_id and journal_id, 
                                 'name': 'Building/Insurance/' + ' - ' + str(record.date),
                                 'type':'ratification',
                                 'reference':'Building/Insurance/' ,
                                 'department_id': record.department_id.id,
                                 'partner_id' : record.partner_id.id,
                                 'amount':line.cost,
                                 'payment_term':line.payment_term.id,
                                 #'amount_in_word':amount_to_text_ar(line.cost),
                                 'payment_rate_currency_id':line.currency.id,
                                 'narration' : 'Building insurance No:  ' + record.name + 'Currancy: ' + line.currency.name,
                                         })  
                  
                  
                # Creating Voucher / Ratitication Lines
                voucher_line_obj.create(cr, uid, {
                                        'amount': line.cost,
                                        'account_id':account_id,
                                        'account_analytic_id':analytic_id or  record.department_id.analytic_account_id.id ,
                                        'voucher_id': voucher_id,
                                        'type': 'dr',
                                        'name':'Building Insurance order: ' + record.name,
                                         })
                voucher_number = self.pool.get('account.voucher').browse(cr,uid,voucher_id)

            
                copy_attachments(self,cr,uid,[record.id],'building.insurance',voucher_id,'account.voucher', context)
                self.write(cr, uid, ids, {'voucher_no':voucher_number.number,'transfer':True,},context=context)
        return True                  
                     

#----------------------------------------
# Class building insurance line
#----------------------------------------
class building_insurance_line(orm.Model):
    """
    To manage building insurance line"""

    _name = "building.insurance.line"
    _description = 'Building insurance line'

    def check_qty(self, cr, uid,ids,context=None):
        """
        Constraints function to check products quantity.

        @return: Boolean True or False
        """
        for line in self.browse(cr,uid,ids,context=context):
           if line.building_id:
              item_qty = sum(item.qty for item in line.building_id.item_ids if item.item_id.id == line.item_id.id)
              if line.qty > item_qty:
                 raise orm.except_orm(_('Error !'),_('sorry you can not exceed item quantity of the selected building %s' % (item_qty)))
        return True

    _columns = { 
       'insurance_id':  fields.many2one('building.insurance', 'Building insurance',),
       'item_id': fields.many2one('item.item', 'Item',required = True,),
       'building_id':fields.many2one('building.building','Building', required = True,),
       'price': fields.float('Item Price', required=True),
       'qty': fields.float('Quantity', required=True),        
       'cost': fields.float('Insurance cost',),   
       'name': fields.char('Notes', size=256, ),                       
               }
    
    _defaults = {
         'price' : 1.0, 
         'qty' : 1.0, 
         'cost' : 1.0,     
            }
        
    _constraints = [
        (check_qty, 'sorry you can not exceed item quantity of the selected building', ['qty']),
           ]

    _sql_constraints = [
        ('item_uniq', 'unique(insurance_id,item_id)', 'Item must be unique!'),
            ] 


        
    def onchange_qty_price(self, cr, uid, ids, qty, price):
        """
        On change quantity function to calculate cost.

        @param qty: line quantity
        @param price: line price 
        @return: cost value
        """
        result = {'cost':qty * price}
        return {'value': result}
    
    def onchange_building_id(self,cr,uid,ids,building_id,context=None):
       """
       On change building function to add domain.

       @param building_id: building ID
       @return: Dictionary of values and aomain
       """
       domain= {}
       if building_id:
            building = self.pool.get('building.building').browse(cr,uid,building_id,context=context)
            domain={'item_id':[('id','in',[item.item_id.id for item in building.item_ids])]}
       return {'value':{'item_id':False},'domain': domain}

#----------------------------------------
# Class building insurance cost lines
#----------------------------------------
class building_insurance_cost_line(orm.Model):
    """
    To manage building insurance cost lines"""

    _name = "building.insurance.cost.line"
    _description = 'Building insurance cost line'

    _columns = { 
       'line_id':  fields.many2one('building.insurance', 'Building insurance',),
       'partner_id':fields.related('line_id','partner_id', type='many2one', relation='res.partner', string = 'Partner', readonly=True , store=True),
       'cost': fields.float('Insurance cost', digits_compute=dp.get_precision('Account')),   
       'name': fields.char('Notes', size=256, ),  
       'currency': fields.many2one('res.currency','Currancy',select=1),   
       'payment_term': fields.many2one('account.payment.term', 'Payment Term',readonly=True,
            help="If you use payment terms, the due date will be computed automatically at the generation "\
                "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "\
                "The payment term may compute several due dates, for example 50% now, 50% in one month."),        
           }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
