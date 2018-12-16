# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,osv
import time
from datetime import date,datetime
import netsvc
from tools.translate import _
import decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
#from tools.amount_to_text_en import amount_to_text
#from common_tools.amount_to_text_ar import amount_to_text as amount_to_text_ar

#----------------------------------------
# Class car operation
#----------------------------------------
class car_operation(osv.Model):

    _name = "car.operation"
    _description = 'Car Operation'

    def _partners_amount(self, cr, uid, ids, field_name, arg, context=None):
        """
           Functional Field Function that calculates the total amount that will be paid to partenrs as a reward for their services.
           @return: Dictionary of value     
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = { 'partners_cost': 0.0}
            val = 0.0
            for partner in order.partners:
                val += partner.cost
            res[order.id]['partners_cost'] = val        
        return res

    def create(self, cr, user, vals, context=None):
        """
           Method creates new entry sequence for the new car operation Record.
           @param vals: Dictionary of the entered data
           @return: Super create method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'car.operation.' + vals['operation_type']
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name) 
        return super(car_operation, self).create(cr, user, vals, context) 
 
    def get_type(self, cr, uid,context=None):
        """
           Method returns the type of the oparation (license or insurance).
           @return: Tuple
        """
        if context:
            if context.has_key('operation_type'): operation_type = context['operation_type']
        return operation_type

    LICENSE_TYPE_SELECTION = [
    ('main', 'Main'),
    ('extension', 'Extension'),
 ]
    
    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed_d', 'Waiting For admin affaris Manager To confirm'),
    ('gm','Waiting For GM of finical and Human Resource Manager To confirm'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), ]    

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the car operation "),
    'date' : fields.date('Request Date',required=True, readonly=True,),
    'operation_date' : fields.date('Operation Date', readonly=True, states={'draft':[('required',True),('readonly',False)]}),
    'end_date' : fields.date('End Date', readonly=True, states={'draft':[('required',True),('readonly',False)]}),
    'type': fields.selection(LICENSE_TYPE_SELECTION, 'Type', required=True, readonly=True,states={'draft':[('readonly',False)]}), 
    'operation_type': fields.selection([('license', 'License'),('insurance', 'Insurance')], 'Operation Type', required=False,), 
    'notes': fields.text('Notes', size=256 , readonly=True,states={'draft':[('readonly',False)]}), 
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'department_id': fields.many2one('hr.department','Department',required=True,states={'done':[('readonly',True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True  ),
    'partner_id':  fields.many2one('res.partner', 'Partner',states={'done':[('readonly',True)]}),    
    'partners':fields.one2many('car.partner.lines', 'line_id' , 'Partners', readonly=True,states={'confirmed_d':[('readonly',False)],'gm':[('readonly',False)]}),
    'total_cost':fields.float('Total cost',digits_compute=dp.get_precision('Account'),redonly=True,states={'draft':[('readonly',False)]}),
    'partners_cost': fields.function(_partners_amount, method=True, string='Partners cost', digits_compute=dp.get_precision('Account')),
    'car_ids': fields.many2many('fleet.vehicle', 'license_cars', 'license_id', 'car_id', 'Cars', readonly=True, states={'draft':[('readonly',False)]}),
    'operation_lines':fields.one2many('car.operation.line', 'operation_id' , 'Cars', readonly=True, states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)]}),
    'transfer': fields.boolean('Transfer',readonly=True),
    'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True),
    'insurance_type_id': fields.many2one('car.insurance.type','Insurance Type',states={'done':[('readonly',True)]}), 
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'cars operation reference must be unique !'),
        ]
    
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'date': time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'car.operation', context=c),
                'state': 'draft',
                'user_id': lambda self, cr, uid, context: uid,
                'type':'main',
                'operation_type': get_type
                }
    
    def onchange_operation_date(self, cr, uid, ids, operation_date):
        """
           Method calculates operation's end date from its start date by adding one year to the start date.
           @param operation_date: Date of operation
           @return: Boolean True
        """
        operation_date = datetime.strptime(operation_date,'%Y-%m-%d').date()
        end_date = date(operation_date.year + 1, operation_date.month, operation_date.day)
        return True

    def onchange_end_date(self, cr, uid, ids, operation_date):
        """
           Method calculates operation's end date from its start date by adding one year to the start date.
           @param operation_date: Date of operation
           @return: Boolean True
        """
        operation_date = datetime.strptime(operation_date,'%Y-%m-%d').date()
        end_date = date(operation_date.year + 1, operation_date.month, operation_date.day)
        return True


    def confirmed_d(self, cr, uid, ids, context=None): 
        """
           Workflow method changes the state to 'confirmed_d' and checks that the required data has been entered and 
           cost is greater than zero or it will raise an exception.
           @return: Boolean True
        """                 
        for order in self.browse(cr, uid, ids, context=context):
            if (order.operation_type == 'insurance' and not order.operation_lines) or (order.operation_type == 'license' and not order.car_ids):
                raise osv.except_osv(_('Error !'), _('You can not confirm the order without cars.'))
            if order.total_cost < 1:
                raise osv.except_osv(_('Error !'), _('You can not confirm the order without right cost.'))

        self.write(cr, uid, ids, {'state':'confirmed_d'})
        return True

    def gm(self, cr, uid, ids, context=None): 
        """
           Workflow method changes the state to 'gm'.
           @return: Boolean True
        """                   
        self.write(cr, uid, ids, {'state':'gm'})
        return True


    def done(self,cr,uid,ids,context=None):
        """
           Workflow method changes the state to 'done' and checks that cost is greater than zero and its correct or raise an exception
           and update car's last insuring date/licensing date based on operation type.
           @return: Boolean True
        """ 
        vehicles_obj = self.pool.get('fleet.vehicle')
        for record in self.browse(cr, uid, ids):
            if record.total_cost <= 0.0:
                raise osv.except_osv(_('No Price !'), _('Please make sure you enter total cost')) 
            elif record.operation_type == 'license':
                total = 0.0
                for line in record.partners:
                    total += line.cost
                if record.total_cost != total:
                    raise osv.except_osv(_('Different prices !'), _('Total cost should equal the partners cost'))  
        if record.operation_type == 'license':    
            for car in record.car_ids:
                vehicles_obj.write(cr, uid,[car.id],{'last_license_id':record.id})       
        elif record.operation_type == 'insurance':
            for line in record.operation_lines:
                vehicles_obj.write(cr, uid,[line.car_id.id],{'last_insurance_id':record.id})       

        self.write(cr, uid, ids, {'state':'done'},context=context) 
        return True

    def cancel(self, cr, uid, ids, notes='', context=None):
        """
           Workflow method changes state of To 'cancel' and write notes about the the cancellation.
           @return: Boolean True
        """
        user_obj = self.pool.get('res.users')
        for record in self.browse(cr, uid, ids,context=context):
            notes = record.notes or ""
            user_name = user_obj.browse(cr, uid, uid).name
            notes +=  '\n'+'car ' + record.operation_type + ' Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ user_name
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """
           Method resets the operation record to 'draft' , deletes the old workflow and creates a new one.
           @return: Boolean True       
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'car.operation', s_id, cr)
            wf_service.trg_create(uid, 'car.operation', s_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
           Method that overwrites unlink method to prevent the the deletion of operations record not in 'draft' state.
           @return: Boolean True       
        """
        stat = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in stat:
            if t['state'] in ('draft'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a car operation, you must first cancel and set to draft.'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True
    
    def _prepare_account_voucher_line(self, cr, uid, voucher_id, operation_record, affairs_account, partner_line = None, context=None):
        """
           Method Prepare dictionaries to create the new account voucher line for specific account voucher (ratification).
           @param voucher_id: Id of voucher 
           @param operation_record: Browse record of car.operation 
           @param affairs_account: Id of admin affairs acount
           @param partner_line: Ids of partners
           @return: Dictionary of values
        """
        account_obj = self.pool.get('account.account')
        account_ids = account_obj.search(cr, uid, [('company_id','=',operation_record.company_id.id),('code','=',str(affairs_account.code))], context=context)
        account_id = account_ids and account_ids[0] or affairs_account.account_id.id
        analytic_id = affairs_account.analytic_id  
        cost = partner_line and partner_line.cost or operation_record.total_cost
        if not account_id:
           raise osv.except_osv(_('Error'), _("Please enter the Car %s accounting configuration")% (operation_record.operation_type,))
        voucher_line_dict = {
                'voucher_id':voucher_id,
                'account_id':account_id,
                'account_analytic_id': analytic_id and analytic_id.id or operation_record.department_id.analytic_account_id.id,
                'amount':cost,
                #'amount_in_word':amount_to_text_ar(cost),
                'type':'dr',
                'name':operation_record.department_id.name,
                           }
        wf_service = netsvc.LocalService("workflow")
        res = wf_service.trg_validate(uid, 'account.voucher',voucher_id, 'preresource', cr)
        
        return voucher_line_dict
    
    def _prepare_account_voucher(self, cr, uid, operation_record, affairs_account, partner = None, context=None):
        """
           Method Prepare dictionaries to create the new account voucher line for specific account voucher (ratification).
           @param operation_record: Browse record of car.operation 
           @param affairs_account: Id of admin affairs acount
           @param partner: Id of partners
           @return: Dictionary of values
        """

        account_journal_obj = self.pool.get('account.journal')
        journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',operation_record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)   
        journal_id = journal_ids and journal_ids[0] or affairs_account.journal_id.id
        partner_id = partner and partner.partner_id.id or operation_record.partner_id.id
        cost = partner and partner.cost or operation_record.total_cost
        return {
            'company_id':   operation_record.company_id.id,
            'journal_id':   journal_id, 
            'department_id':operation_record.department_id.id,
            'name':         operation_record.operation_type  + ' - ' + operation_record.name,
            'type':         'ratification',
            'reference':    operation_record.name ,
            'partner_id' :  partner_id,
            'amount':       cost,
            #'amount_in_word':amount_to_text_ar(cost),
            'narration' :   'Car ' + str(operation_record.operation_type)  + ' No: ' + operation_record.name
        }
    def _create_ratification(self,cr,uid,record, partner=None, context={}):
        """
           Method creates account ratification
           @param record: Browse car.operation record
           @param partner: Id of partner
        """
        car_operation_obj = self.pool.get('car.operation')
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model') 
        if record.operation_type=='insurance':
           model='car.insurance'
        else:
           model='car.license'
        affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=',model)], context=context)
        affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
        if not affairs_account_ids:
           raise osv.except_osv(_('Error'), _("Please enter the Car %s accounting configuration")% (record.operation_type,))
        affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
       
        #Prepare account voucher
        voucher_dict= self._prepare_account_voucher(cr, uid, record, affairs_account, partner, context=context)
        voucher_id = voucher_obj.create(cr, uid, voucher_dict, context=context)
        #################### update workflow state###############
        voucher_state = 'draft'
        if record.company_id.affairs_voucher_state : 
                voucher_state = record.company_id.affairs_voucher_state 
        if voucher_id:
           	wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
		voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
        #prepare account voucher line
        voucher_line_dict = self._prepare_account_voucher_line(cr,uid,voucher_id,record, affairs_account, partner, context=context)
        voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
        
        voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context).number
        car_operation_obj.write(cr, uid, [record.id],{'notes':record.notes or '' + str(voucher_number),} ,context=context)             
        copy_attachments(self,cr,uid,[record.id],'car.operation',voucher_id,'account.voucher', context)

    def action_create_ratification(self,cr,uid,ids,context={}):
        """
           Method that creates ratification for car license or car operation
           @return: Dictionary 
        """
        car_operation_obj = self.pool.get('car.operation')
        for record in self.browse(cr,uid,ids,context=context):
            if record.transfer:
                raise osv.except_osv(_('Warning'), _("This operation already transfered to the accounting"))
            
            if record.operation_type == 'insurance':
                self._create_ratification(cr, uid, record, context=context)
           
            elif record.operation_type == 'license':
                for partner in record.partners:
                    self._create_ratification(cr, uid, record, partner, context=context)
            car_operation_obj.write(cr, uid, record.id,{'transfer':True,} ,context=context)             
        return True



#----------------------------------------
# Class car operation lines
#----------------------------------------

class car_lines(osv.Model):
    
    def unlink(self, cr, uid, ids, context=None):
        """
           Method that overwrites unlink method to prevent the the deletion of  insurance record 
           @return: Boolean True       
        """
        raise osv.except_osv(_('Invalid action !'), _('You cannot delete car lines directly.'))
        return True
    
    _name = "car.operation.line"
    _description = 'Car Operation Line'

    _columns = { 
       'operation_id':  fields.many2one('car.operation', 'Car operation',),
       'car_id': fields.many2one('fleet.vehicle', 'Car',required = True,),
       'department_id': fields.related('car_id', 'department_id', type='many2one', relation='hr.department', string='Department', readonly=True,store=True), 
       'company_id': fields.related('car_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True,), 
       'car_number': fields.related('car_id', 'license_plate', type='char', relation='fleet.vehicle', string='Car Number', readonly=True,),   
       'chassi_no': fields.related('car_id', 'vin_sn', type='char', relation='fleet.vehicle', string='chasiss Number', readonly=True,),     
       'car_cost':fields.float('Car Cost', digits_compute=dp.get_precision('Account')),
       'document': fields.char('Document No', size=128),    
       'cost': fields.float('Cost', digits_compute=dp.get_precision('Account')),   
       'date':fields.related('operation_id','date', type='date',string = 'Date', store=True, readonly=True),
       'last_license_date': fields.related('car_id', 'last_license_date', type='date', relation='fleet.vehicle', string='Last license date', readonly = True),
       'last_insurance_date': fields.related('car_id', 'last_insurance_date', type='date', relation='fleet.vehicle', string='Last insurance date', readonly = True),
       'machine_capacity': fields.related('car_id', 'machine_capacity', type='char', relation='fleet.vehicle', string='Machine Capacity', readonly = True),
       'name': fields.char('Note', size=256 ),                       
               }
        
    _sql_constraints = [
        ('partner_uniq', 'unique(operation_id,car_id)', 'Car must be unique!'),
            ] 


#----------------------------------------
# Class partner lines
#----------------------------------------
class partner_lines(osv.Model):
    
    _name = "car.partner.lines"
    _description = "Partners Of License Record"

    _columns = { 
       'name': fields.char('Name', size=64 ,select=True,),                       
       'partner_id':  fields.many2one('res.partner', 'Partner Name', required=True,),
       'line_id': fields.many2one('car.operation', 'Partner Line ', ondelete='cascade'),    
       'cost': fields.float('Cost', digits_compute=dp.get_precision('Account')),   
               }
    _sql_constraints = [
        ('partner_uniq', 'unique(line_id,partner_id)', 'Partner must be unique!'),
            ] 


#----------------------------------------
# Class fleet vehicles
#----------------------------------------
class fleet_vehicle(osv.Model):
    """
       Inherits fleet.vehicle to add fields related to car operation
    """
    _inherit = "fleet.vehicle"
    _columns = {   
                'licenses_id': fields.many2many('car.operation', 'license_cars', 'car_id','license_id',relation='fleet.vehicle', readonly = True),
                'last_license_id': fields.many2one('car.operation', 'Last license',readonly=True),    
                'last_license_date':fields.related('last_license_id','operation_date', type='date',string = 'Last licenses date', readonly=True),
                'insurance_ids': fields.one2many('car.operation.line', 'car_id','Last insurances', readonly = True),
                'last_insurance_id': fields.many2one('car.operation', 'Last insurance',readonly = True),    
                'last_insurance_date':fields.related('last_insurance_id','operation_date', type='date',string = 'Last insurance date', readonly=True),
                 }



#----------------------------------------
# Class Car Insurance Type
#----------------------------------------
class car_insurance_type(osv.Model):
    
    _name = "car.insurance.type"
    _description = 'Car Insurance Type'
    
    _columns = {
                'name': fields.char('Insurance Name', size=64 ,required=True),
                'code': fields.integer('Code',size=5), 
               }
    _sql_constraints = [
        ('car_insurance_uniq', 'unique(name)', 'Insurance Type must be unique!'),
            ] 
       

