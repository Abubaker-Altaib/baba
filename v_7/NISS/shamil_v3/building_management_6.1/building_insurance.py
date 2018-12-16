# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from osv import fields,osv
import time
from tools.translate import _
import netsvc
import decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from common_tools.amount_to_text_ar import amount_to_text as amount_to_text_ar

#----------------------------------------
# Class building insurance
#----------------------------------------
class building_insurance(osv.osv):
    _name = "building.insurance"
    _description = 'building insurance'

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every new building insurance Record
        @param vals: record to be created
        @return: return a result that create a new record in the database
          """
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'building.insurance'
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name) 
        return super(building_insurance, self).create(cr, user, vals, context) 
 
    
    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Waiting For Section Manager'),
    ('section', 'Waiting For Adim Affairs Dept Manager'),
    ('dept', 'Waiting For Genral Adim Affairs Dept Manager'),
    ('gm', 'Done'),
    ('cancel', 'Cancel'), ]    

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the building insurance"),
    'date' : fields.date('Request Date',required=True, readonly=True,),
    'begin_date' : fields.date('Insurance date', required=True , states={'confirmed':[('readonly',True)],'section':[('readonly',True)],'dept':[('readonly',True)],'gm':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'end_date' : fields.date('End Date', required=True , states={'confirmed':[('readonly',True)],'section':[('readonly',True)],'dept':[('readonly',True)],'gm':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'department_id': fields.many2one('hr.department','Department',required=True,states={'confirmed':[('readonly',True)],'section':[('readonly',True)],'dept':[('readonly',True)],'gm':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True  ),
    'partner_id':  fields.many2one('res.partner', 'Partner',required=True,states={'confirmed':[('readonly',True)],'section':[('readonly',True)],'dept':[('readonly',True)],'gm':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),    
    'total_cost':fields.float('Total cost', digits_compute=dp.get_precision('Account'),states={'confirmed':[('readonly',True)],'section':[('readonly',True)],'dept':[('readonly',True)],'gm':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'insurance_lines':fields.one2many('building.insurance.line', 'insurance_id' , 'Items', readonly=True, states={'draft':[('readonly',False)]}),
    'insurance_cost_lines':fields.one2many('building.insurance.cost.line','line_id','Cost',readonly=True, states={'draft':[('readonly',False)]}),
    'transfer': fields.boolean('Transfer',readonly=True),
    'voucher_no': fields.char('Voucher No', size=125, readonly=True), 
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'notes': fields.text('Notes', size=256 , readonly=True,states={'draft':[('readonly',False)]}),
    'desc': fields.char('Description', size=64, required=True,states={'done': [('readonly', True)]}),
    'operation_type': fields.selection([('main', 'Main'),('extension', 'Extension')], 'Operation Type', required=True,readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}), 
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Building insurance reference must be unique !'),
        ]
    
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'date': time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'building.insurance', context=c),
                'state': 'draft',
		'operation_type':'main',
                'user_id': lambda self, cr, uid, context: uid,
		'voucher_no':lambda self, cr, uid, context: '/',
                }
    
    """ Workflow Functions"""   
    def confirmed(self, cr, uid, ids, context=None):                   
        for order in self.browse(cr, uid, ids, context=context):
            if not order.insurance_lines:
                raise osv.except_osv(_('Error !'), _('You can not confirm the order without insurance lines.'))
            if not order.insurance_cost_lines:
                raise osv.except_osv(_('Error !'), _('You can not confirm the order without cost lines.'))              
            for line in order.insurance_cost_lines:              
                if line.cost <=0:
                    raise osv.except_osv(_('Error !'), _('Please Enter The cost.'))
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def section(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'section'},context=context) 
        return True


    def dept(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'dept'},context=context) 
        return True

    def gm(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'gm'},context=context) 
        return True

    def cancel(self, cr, uid, ids, notes='', context=None):
        """ Cancel building insurance record"""
        user_obj = self.pool.get('res.users')
        for record in self.browse(cr, uid, ids,context=context):
            notes = record.notes or ""
            user_name = user_obj.browse(cr, uid, uid).name
            notes += 'This record cancelled at : ' + time.strftime('%Y-%m-%d') + ' by '+ user_name + '\n'
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ convert the record from cancel state to draft state"""
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for record_id in ids:
            self.write(cr, uid, record_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'building.insurance', record_id, cr)
            wf_service.trg_create(uid, 'building.insurance', record_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """Delete the building insurance record"""
        states = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for state in states:
            if state['state'] in ('draft','cancel'):
                unlink_ids.append(state['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a building insurance order, you must first cancel it or set to draft.'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True
    def action_create_ratification(self,cr,uid,ids,context={}):
        """create ratification for Building insurance
        @return: Dictionary 
        """
        '''wf_service = netsvc.LocalService("workflow")
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
                	raise osv.except_osv(_('Error'), _("Please enter the Building Insurance accounting configuration"))
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
                                 'amount_in_word':amount_to_text_ar(line.cost),
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
                self.write(cr, uid, ids, {'voucher_no':voucher_number.number,'transfer':True,},context=context)'''
        return True                  
                     
building_insurance()

#----------------------------------------
# Class building insurance line
#----------------------------------------
class building_insurance_line(osv.osv):
    
    _name = "building.insurance.line"
    _description = 'Building insurance line'

    _columns = { 
       'insurance_id':  fields.many2one('building.insurance', 'Building insurance',),
       'item_id': fields.many2one('building.item', 'Item',required = True,),
       'building_id':fields.related('item_id','building_id', type='many2one', relation='building.manager', string = 'Building', readonly=True , store=True),
       'department_id':fields.related('building_id','department_id', type='many2one', relation='hr.department', string = 'Department', readonly=True , store=True),
       'company_id':fields.related('building_id','company_id', type='many2one', relation='res.company', string = 'Company', readonly=True , store=True),
       'price':fields.related('item_id','price', type='float', string = 'Price', readonly=True , store=True),
       'qty':fields.related('item_id','qty', type='float', string = 'Qty', readonly=True , store=True),
       'cost': fields.float('Insurance cost', digits_compute=dp.get_precision('Account')),   
       'name': fields.char('Notes', size=256, ),                       
               }
        
    _sql_constraints = [
        ('item_uniq', 'unique(insurance_id,item_id)', 'Item must be unique!'),
            ] 

building_insurance_line()


#----------------------------------------
# Class building insurance cost lines
#----------------------------------------
class building_insurance_cost_line(osv.osv):
    
    _name = "building.insurance.cost.line"
    _description = 'Building insurance cost line'

    _columns = { 
       'line_id':  fields.many2one('building.insurance', 'Building insurance',),
       'partner_id':fields.related('line_id','partner_id', type='many2one', relation='res.partner', string = 'Partner', readonly=True , store=True),
       'cost': fields.float('Insurance cost', digits_compute=dp.get_precision('Account')),   
       'name': fields.char('Notes', size=256, ),  
       'currency': fields.many2one('res.currency','Currancy',select=1),   
       'payment_term': fields.many2one('account.payment.term', 'Payment Term',readonly=True, states={'draft':[('readonly',False)]},
            help="If you use payment terms, the due date will be computed automatically at the generation "\
                "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "\
                "The payment term may compute several due dates, for example 50% now, 50% in one month."),        
           }

building_insurance_cost_line()
