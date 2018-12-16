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
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom import amount_to_text_ar

#
# Model definition
#
SERVICE_TYPE = [
    ('breakfast', 'Breakfast'),
    ('lunch', 'Lunch'),
    ('dinner', 'Dinner'),
    ]
Hosplity_TYPE = [
    ('meeting', 'Meeting'),
    ('hospitality', 'Hospitality'),
    ('conferences', 'Conferences'),
    ]
MULI_SERVICE = [
    ('local_hospitality_service', 'Local Hospitality Service'),
    ('extrnal_hospitality_service', 'External Hospitality Service'),
    ('no_need_hospitality', 'No Need Hospitality'),
    ]
STATE_SELECTION = [
    
    ('draft', 'Draft'),
    ('confirmed_d', 'Waiting for general department manager To confirm'),
    ('confirmed', 'Waiting admin General affairs manager to approve '),
    ('approved_gn', 'Waiting for admin  affairs  manager to approve'),
    ('approved_sc', 'Waiting for admin affairs officer'),
    ('approved', 'Waiting for admin  affairs  manager to approve' ),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ('cansal_lock', 'Cansal_lock'),
    ('change_lock','Chane Lock hall')
    ]

PAYMENT_SELECTION = [
    		('voucher', 'Voucher'),
    		('enrich', 'Enrich'), 
    			]  
  
class  hospitality_service(osv.Model):

    def create(self, cr, user, vals, context=None):
        """
        Method overwrites create method to creates new entry sequence for every Hospitality service.
        @return: Super create method
        """
          
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'hospitality.service')
        return super(hospitality_service, self).create(cr, user, vals, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        """ 
	Mehtod overwrites copy method duplicates the value of the given id and updates the value of name fields (sequence).
	@param default: Dictionary of data    
	@return: Super copy method
        """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'hospitality.service'),
            
        })
        return super(hospitality_service, self).copy(cr, uid, id, default, context)    
    
    def unlink(self, cr, uid, ids, context=None):
        """
	Method that overwrites unlink method to prevent the the deletion of record not in 'draft' or 'cancel' state
	and creates log message for the deleted record.
	@return: Super unlink method       
        """
        hospitality_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in hospitality_orders:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a hospitality service order(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'hospitality.service', id, 'cancel', cr)
            hospitality_order_name = self.browse(cr, uid, id, context=context).name
            message = _("hospitality service order '%s' has been deleted.") % hospitality_order_name
            self.log(cr, uid, id, message)
        return super(hospitality_service, self).unlink(cr, uid, unlink_ids, context=context)

    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """ 
	Method calculates total cost amount of the service.
	@return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = { 'cost': 0.0}
            total_cost = 0.0
            for line in record.order_lines:
                	total_cost += line.service_cost

            res[record.id]['cost'] = total_cost 
        return res
    
   

    _name = "hospitality.service"
    _description = 'Hospitality Service'
    _order = "name desc"
    
    _columns = {
        'alarm':fields.char('Alarm', size=10 ,),
	    'name':fields.char('Reference', size=64, required=False, select=True, readonly=True  , help="unique number of the Hospitality Service"),
	    'date' :fields.date('Date of request',readonly=True),
	    'department_id':fields.many2one('hr.department', 'Department',readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly',False)],}, ),
	    'date_of_execution':fields.date('Date of Execution',required=True ,readonly=False, states={'done':[('readonly',True)],'approved_sc':[('readonly',True)]},help="The Request must be befor 48 hours"),
	    'partner_id': fields.many2one('res.partner','Executing Agency'),
	    'cost':fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Cost', multi='all',store=True),
	    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
	    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
	    'notes': fields.text('Notes',states={'done':[('readonly',True)]},required=True),
	    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
        'order_lines':fields.one2many('order.lines', 'order_id' , 'Service Types and Quantaties',),
        'allowance_computed': fields.boolean('Allowance Computed' ,),
        'hospilty_place': fields.char('Hosptlity Place', size=64 ),
        'no_day':fields.integer('Number Day',digits_compute= dp.get_precision('Account'),required=True),
        'hosplity_type':fields.selection(Hosplity_TYPE,'Hosptiality type', select=True),
        'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',readonly=True,states={'approved_sc':[('readonly',False)]}, select=True),
        'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'approved_sc':[('readonly',False)]}),




    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Hospitality Service Reference must be unique !'), 
                        
        ]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'user_id': lambda self, cr, uid, context: uid,
                'date': time.strftime('%Y-%m-%d'),
                #'date_of_execution': time.strftime('%Y-%m-%d'),
                'state': 'draft',
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hospitality.service', context=c),
                'allowance_computed' : lambda *a: 0,
                'hosplity_type':'hospitality',
                'no_day':1

                }
    """ Workflow Functions"""
    
    def confirmed_d(self, cr, uid, ids,alarm='',context=None): 
        """
	Workflow method changes the state to 'confirmed_d' and checks if the service requested 
	late then alarm the user.
	@param alarm: String contains a massage
	@return: Boolean True
        """ 
        alarm = ""
        ex_date=self.pool.get('hospitality.service').browse(cr, uid,ids)[0].date_of_execution
        req_date=self.pool.get('hospitality.service').browse(cr, uid,ids)[0].date
        ex_date1=datetime.strptime(ex_date,'%Y-%m-%d').date()
        req_date1=datetime.strptime(req_date,'%Y-%m-%d').date()
        diff_day=(ex_date1-req_date1).days
        if  diff_day<2:
            alarm =alarm +'\n'+'Hospitality services Cancelled Reson for Request Later : '+ex_date
            self.write(cr, uid, ids, {'state':'confirmed_d','alarm':alarm})  
        else:      
            self.write(cr, uid, ids, {'state':'confirmed_d'})
        return True

    def confirmed(self, cr, uid, ids,context=None): 
        """ 
	Workflow method changes the state to 'confirmed'.
	@return: Boolean True
        """ 
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def approved(self,cr,uid,ids,context=None):
        """ 
	Workflow method changes the state to 'approved'.
	@return: Boolean True
        """ 
        self.write(cr, uid, ids, {'state':'approved'},context=context)
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

    def is_roof(self, cr, uid, ids, context=None):  
        """
           Workflow method that checks wether the amount of maintenance request has a financial roof  or not .
           @return: Boolean True Or False
        """
        affairs_model_obj = self.pool.get('admin.affairs.model')
        payment_roof_obj = self.pool.get('admin.affaris.payment.roof')            
        for record in self.browse(cr, uid, ids):
            affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','hospitality.service')], context=context)
            if not affairs_model_ids :
                return True
            if affairs_model_ids :
                payment_roof_ids = payment_roof_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0]),('name','=','service')], context=context)
                if not payment_roof_ids : 
                    return True
                affairs_payment = payment_roof_obj.browse(cr, uid, payment_roof_ids[0], context=context)
                if record.cost > affairs_payment.cost_to :
                    return False
        return True

    def done(self,cr,uid,ids,context=None):
        """ 
	Workflow method checks the cost is greater than zero or it raises an exception and it changes the state to 'approved_sc'.
	@return: Boolean True
        """
        payment_enrich_obj = self.pool.get('payment.enrich')
        payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')   
        for record in self.browse(cr, uid, ids):
        	if record.cost < 1 :
            		raise osv.except_osv(_('No cost !'), _('You have to insert cost.'))
        	else:
	    		if record.payment_selection == 'enrich':
				paid = (record.enrich_category.paid_amount + record.cost)
				residual = (record.enrich_category.residual_amount - record.cost)
				#enrich_payment_id = cr.execute("""update payment_enrich set paid_amount=%s , residual_amount=%s where id =%s""",(paid,residual,record.enrich_category.id))
				#details = smart_str('Service Request No:'+record.name+'\n'+record.service_category.name)
				details = 'Hospitality Service No:'+record.name
				enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					'enrich_id':record.enrich_category.id,
                        		'cost': record.cost,
					'date':record.date,
                        		'name':details,
					'department_id':record.department_id.id,

                            				}, context=context)
				self.write(cr, uid, ids, {'allowance_computed':True},context=context)
	    		#elif record.payment_selection == 'voucher':
			#	self.write(cr, uid, ids, {'allowance_computed':False},context=context)     
            	self.write(cr, uid, ids, {'state':'done'}) 
        return True

    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
	Workflow method changes the state to 'cancel'.
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
	Method resets the hospitality request record to 'draft' , deletes the old workflow and creates a new one.
	@return: Boolean True       
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'hospitality.service', s_id, cr)            
            wf_service.trg_create(uid, 'hospitality.service', s_id, cr)
        return True
    




class order_lines(osv.Model):

    _name = "order.lines"
    _description = "Order Lines"
    _columns = {
                'service_type': fields.many2one('hospitality.service.type','Service Type',),
                'order_id': fields.many2one('hospitality.service', 'Request Ref', ondelete='cascade'),
                'hall_id': fields.many2one('halls.lock', 'Hall_req', ondelete='cascade'),
                'service_qty': fields.float('Quantity', digits=(16,2),),   
                'service_sort':fields.selection(SERVICE_TYPE,'Service Sort', select=True),             
                'name': fields.text('Note', size=256),
		        'service_cost':fields.integer('Service Cost',digits_compute= dp.get_precision('Account'),),
		
               }
    #_sql_constraints = [
     #   ('service_uniq', 'unique(order_id,order_lines)', 'Sorry You Entered Service Two Time You are not Allow to do this.... Please delete The Duplicts!'),
      #      ]
    _defaults = {
                'service_qty': 1.0,
		'service_cost':0.0
                }


# Class Hospitality Services Type 
class hospitality_service_type(osv.Model):

    def _check_recursion(self, cr, uid, ids, context=None):
        """
	Method that checks if the given ids still has a parent or not.
	@return: Boolean True or False      
        """
        if context is None:
            context = {}
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from hospitality_service_type where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _name = "hospitality.service.type"
    _description = "Hospitality Service Type"
    _columns = {
    'code': fields.integer('Code',size=10,),
    'name': fields.char('Hospitality Service Name', size=64,),
    'parent_id': fields.many2one('hospitality.service.type','Parent Category', select=True, ondelete='cascade'),
    'hospitality_account_id': fields.property('account.account',
            type='many2one', relation='account.account',
            string='Account', view_load=True,
            help="When create account ratification, this account will used in that ratification."),      
    'hospitality_analytic_id': fields.property('account.analytic.account',
            type='many2one', relation='account.analytic.account',
            string='Analytic account', view_load=True,
            help="When create account ratification, this account journal will used in that ratification."),      
    'hospitality_journal_id': fields.property('account.journal',
            relation='account.journal', type='many2one',
            string='Journal', view_load=True,
            help="When create account ratification, this is the Accounting Journal in which ratification will be post."), 
}
    _constraints = [
        (_check_recursion, 'Error! You can not create recursive Service Type.', ['Parent Category'])
    ]

    

class hospitality_allowances_archive(osv.Model):
    _name = "hospitality.allowances.archive"
    _description = 'Hospitality Allowances Archive'
    _order = "name desc"
    
    def _total_amount(self, cr, uid, ids, field_name, arg, context={}):
        """ 
	Method calculates the the total of cost of hospitality request.
	@param field_name: list contains name of fields that call this method
	@param arg: extra arguement
	@return: Dictionary of values
        """
        res = {}
        for hospitality_record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in hospitality_record.allowances_lines:
                val += line.amount
            res[hospitality_record.id] = val 
        return res
     
    def _get_archive_ids(self, cr, uid, ids, context=None):
        """  
	Method return tha ids of associated hospitality.allowances.lines record that have 
	that have been changed in order to re-calculate the cost.
	@param field_name: List contains name of fields that call this method
	@param arg: Extra arguement
	@return: List of ids
        """
        result = {}
        allowances_lines_obj=self.pool.get('hospitality.allowances.lines')
        for line in allowances_lines_obj.browse(cr, uid, ids, context=context):
            result[line.hospitality_allow_id.id] = True
        return result.keys()
        
    _columns = {
        
       'name':fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the hospitality allowances archive"),
	    'date_from' :fields.date('Date From',readonly=True),
	    'date_to' :fields.date('Date To',readonly=True),
        'partner_id':fields.many2one('res.partner', 'Partner',readonly=True),
        'departments':fields.many2one('hr.department', 'Department',readonly=True),
	    'department_id': fields.related('allowances_lines', 'department_id', type='many2one', relation='hr.department', string='Department',store = True),
        'amount': fields.function(_total_amount, method=True, digits_compute=dp.get_precision('Account'), string='Amount',
             store ={
                'hospitality.allowances.archive': (lambda self, cr, uid, ids, c={}: ids, ['allowances_lines'], 10),
                'hospitality.allowances.lines': (_get_archive_ids, ['amount'], 10),  
                    }),
	    'date' :fields.date('Archive date',readonly=True),
        'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
	    'allowances_lines': fields.one2many('hospitality.allowances.lines', 'hospitality_allow_id' , 'Service Types and Quantaties' ,readonly=True),
        'transfer': fields.boolean('Transfer'),
        'account_voucher_ids': fields.many2many('account.voucher', 'hosptial_voucher', 'hospital_id', 'voucher_id', 'Account voucher',readonly=True),
               }
    
    _defaults = {
                'name': '/',
                }
    
    def unlink(self, cr, uid, ids, context=None):
        """
	Method that overwrites unlink method to prevent the the deletion of transfered record
	and creates log message for the deleted record.
	@return: Super unlink method       
        """
        hospitality_service_obj = self.pool.get('hospitality.service')       
        unlink_ids = []
        update_ids = []
        for record in self.browse(cr,uid,ids,context):
            if record.transfer == False:
                unlink_ids.append(record.id)
            else:
                raise osv.except_osv(_('Invalid action !'), _('You cannot remove hospitality allowances archive that are transfered to the accounting'))
            for line in record.allowances_lines:
                if line.hospitality_service_id:
                    update_ids.append(line.hospitality_service_id.id)
        hospitality_service_obj.write(cr,uid,update_ids,{'allowance_computed':False},context=context)
        for id in unlink_ids:
            allowances_archive_name = self.browse(cr, uid, id, context=context).name
            message = _("Hospitality allowances archive '%s' has been deleted.") % allowances_archive_name
            self.log(cr, uid, id, message)
        return super(hospitality_allowances_archive, self).unlink(cr, uid, unlink_ids, context=context)
   
    def action_create_ratification(self,cr,uid,ids,context={}):
       """
	Method transfers the hospitality amount and creates ratification for hospitality service allowances archive.
	@return: Boolean True 
       """
       hospitality_obj = self.pool.get('hospitality.service')
       hospitality_allowances_obj = self.pool.get('hospitality.allowances.archive')
       account_journal_obj = self.pool.get('account.journal')   
       account_obj = self.pool.get('account.account')
       voucher_obj = self.pool.get('account.voucher')
       voucher_line_obj = self.pool.get('account.voucher.line')
       affairs_account_obj = self.pool.get('admin_affairs.account') 
       affairs_model_obj = self.pool.get('admin.affairs.model') 
       for record in self.browse(cr, uid, ids, context=context):
           affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','hospitality.service')], context=context)
           affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
           if not affairs_account_ids:
                raise osv.except_osv(_('Error'), _("Please enter the hospitality service accounting configuration"))
           affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
           accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','hospitality.service')], context=context)
           account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
           journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
           journal_id = journal_ids and journal_ids[0] or affairs_account.journal_id.id
           account_id = account_ids and account_ids[0] or affairs_account.account_id.id
           analytic_id = affairs_account.analytic_id 
           cr.execute('''SELECT distinct
  sum(all_line.amount)+(sum(all_line.amount)*17)/100 as hos_sum, 
  a.id
FROM 
  public.hospitality_allowances_archive as hos_allow, 
  public.hospitality_allowances_lines as all_line, 
  public.hr_department as hr, 
  public.account_analytic_account as a
WHERE 
  hos_allow.id = all_line.hospitality_allow_id AND
  hr.id = all_line.department_id AND
  a.id = hr.analytic_account_id   and hos_allow.id=%s
GROUP BY a.id''' %record.id)
           res =  cr.dictfetchall()
           voucher_dict={
                                 'company_id':record.company_id.id,
                                 'department_id':record.departments.id,
                                 'journal_id':journal_id , 
                                 'name': 'Services/HA/'  + ' - ' + record.date_from + ' - ' + record.date_to,
                                 'type':'ratification',
                                 'reference':'Services/HA/' ,
                                 'partner_id' : record.partner_id.id,
                                 'amount':int(record.amount),
                                 'narration' : 'Hospitality service No:  ' + record.name  + '\nThe period between    :  ' + record.date_from + ' and ' + record.date_to,
                                 #'amount_in_word':amount_to_text_ar(record.amount),

                     }
           voucher_id = voucher_obj.create(cr, uid, voucher_dict, context=context)
           
           for line in res:
               
              voucher_line_dict = {
                   'voucher_id':voucher_id,
                   'account_analytic_id':line['id'],
                   'amount':line['hos_sum'],
                   'type':'dr',
                   'name':record.name,
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
           hospitality_allowances_obj.write(cr, uid, record.id,{'transfer':True,} ,context=context)
           cr.execute('insert into hosptial_voucher (hospital_id,voucher_id) values(%s,%s)',(record.id,voucher_id))             
           copy_attachments(self,cr,uid,[record.id],'hospitality.allowances.archive',voucher_id,'account.voucher', context)
       return True
   


class hospitality_allowances_lines(osv.Model):
    _name = "hospitality.allowances.lines"
    _description = 'Hospitality Allowances Lines'
    _rec_name = 'hospitality_allow_id'     
    _columns = {
	    'hospitality_allow_id':fields.many2one('hospitality.allowances.archive', 'Allowances archive',readonly=True),
	    'department_id': fields.many2one('hr.department', 'Department',readonly=True),
        'partner_id':  fields.related('hospitality_allow_id', 'partner_id', type='many2one', relation='res.partner',readonly=True, string='Partner', store=True),
	    'amount':fields.float('Amount',digits=(18,2)),
        'hospitality_service_type': fields.many2one('hospitality.service.type','Hospitality service',readonly=True),
        'name': fields.text('Note', size=256),
                }


class halls_names(osv.Model):
    _name = "halls.names"
    _description = 'Halls Names Data'
    _columns = {
        'name':fields.char('Hall Name', size=180,required=True,),
        'code': fields.char('Code', size=64),
        'used':  fields.boolean('Halls In Service',required=False,),
        'lock_begin_date':fields.datetime('Lock Begin Date',readonly=True,),
        'lock_end_date': fields.datetime('Lock End Date', readonly=True,),
       'hall_detalis':fields.one2many('halls.names.detalis', 'detail_id' , 'Halls Detalis',),
                }
    _defaults = {
                
                'used': False,
                }
    
class halls_names_detalis(osv.Model):
    _name = "halls.names.detalis"
    _description = 'Halls Name Detalies'
    _columns = {
        'name':fields.char('Hall_Detail', size=180,required=True,),
        'request':  fields.boolean('Detailes Need',required=True,),
        'detail_id': fields.many2one('halls.names', 'Request Ref', ondelete='cascade'),
                }
    _defaults = {
                
                'request': False,
                }
    





class halls_lock(osv.Model):
    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for hall lock
       """     
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'halls.lock')
        return super(halls_lock, self).create(cr, user, vals, context)

    def date_excution_check(self, cr, uid, ids, context=None):
        from_date=self.browse(cr,uid,ids)[0].date_from
        today=self.browse(cr,uid,ids)[0].date_to
        if today < from_date:
            return False
        return True

    PAYMENT_SELECTION = [
    		('none', 'Nothing'),
    		('enrich', 'Enrich'), 
    			] 

    _name = "halls.lock"
    _description = 'Halls Lock And Services'
    _columns = {
        'name':fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the Lock hall In this time"),
        'alarm':fields.text('Alarm', size=10 ,),
        'date' :fields.date('Date of request',readonly=True),
        'department_id':fields.many2one('hr.department', 'Department',states={'done':[('readonly',True)],'cansal_lock':[('readonly',True)]},required=True ),
        'hall_id':fields.many2one('halls.names', 'Halls_name',states={'confirmed_d':[('required',True)],'done':[('readonly',True)],'cansal_lock':[('readonly',True)]} ),
        'date_from':fields.datetime('Date From',states={'done':[('readonly',True)]},required=True ),
        'date_to':fields.datetime('Date To',states={'done':[('readonly',True)]},required=True  ),
        'multi_service': fields.selection(MULI_SERVICE,'required_service', states={'draft':[('required',True)],'done':[('readonly',True)],'cansal_lock':[('readonly',True)]}),
        'user_id':  fields.many2one('res.users', 'Responsible', readonly=True ,),
        'Purpose': fields.char('Purpose', size=128 ,states={'draft':[('required',True)],'cansal_lock':[('readonly',True)],'done':[('readonly',True)]}),
        'company_id': fields.many2one('res.company','Company',states={'confirmed_d':[('required',True)],'done':[('readonly',True)],'cansal_lock':[('readonly',True)]}),
        'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
        'service_order':fields.one2many('order.lines', 'hall_id' , 'Service Types',states={'done':[('readonly',True)],'cansal_lock':[('readonly',True)]}),
        'all_service': fields.text('Hall Service '),
        'no_day':fields.integer('Number Day',digits_compute= dp.get_precision('Account'),required=True,states={'done':[('readonly',True)],'cansal_lock':[('readonly',True)]}),
        'emp_cordnate':fields.many2one('hr.employee','Cordnate Name',states={'done':[('readonly',True)],'cansal_lock':[('readonly',True)]}),
        'tel_cordnate':fields.char('Cordnate Tele',size=128,states={'done':[('readonly',True)],'cansal_lock':[('readonly',True)]}),
        'member': fields.many2many( 'hr.employee','mem_emplo_rep','emp_id','hall_id', 'Member in subject',states={'done':[('readonly',True)],'cansal_lock':[('readonly',True)]}),
    'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',states={'done':[('readonly',True)]}, select=True),
    'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'approved_sc':[('readonly',False)]}),
    'cost':fields.integer('Cost',digits_compute= dp.get_precision('Account'),readonly=True, states={'approved_sc':[('readonly',False)]}),

        

                }
    _defaults = {
                'name':'/',
                'user_id': lambda self, cr, uid, context: uid,
                #'date':datetime.date()..strftime("%y-%m-%d-%H-%M"),
                #'state': 'draft',
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'halls.lock', context=c),
                }
    _constraints = [
        (date_excution_check, 'date of reservision must more than date request. ', ['date_from']),]
    
    def lock_hall(self, cr, uid,ids, context={}):
        """ 
        Finish the hall lock order and change the dates and check bool field in halls names. 
        @return: Boolean True
        """
        halls_names_obj=self.pool.get('halls.names')
        halls_detalies_obj=self.pool.get('halls.names.detalis')
        date_from=self.browse(cr,uid,ids,context=context)[0].date_from
        #now_date=datetime.strftime(date_from,'%Y-%m-%d %H:%M:%S')
        hall_name_ckeck = halls_names_obj.search(cr, uid, [('used','=',True),('lock_end_date','<=',date_from)],context=context)
        hall_name_id = halls_names_obj.write(cr, uid,hall_name_ckeck,{               
                'lock_begin_date':  None ,
                 'lock_end_date':  None ,
                 'used': False,
                                    }, context=context) 
        hall_name_detalies = halls_detalies_obj.search(cr, uid,[('detail_id','=',hall_name_ckeck)],context=context)
        for l in hall_name_detalies:   
                hall_name_id1 = halls_detalies_obj.write(cr, uid,l,{               
                 'request': False,
                                    }, context=context)   
        self.write(cr, uid, ids, {'state':'draft'})      
        return True 
    
    def onchange_hall_id(self, cr, uid, ids,hall_id,context=None):
        """
	Method Onchage in all_service field from the hall name form
	@param hall_id: Id of the hall
	@return: Dictionary of value 
        """
        string=''
        halls_names_obj=self.pool.get('halls.names')
        halls_detalies_obj=self.pool.get('halls.names.detalis')
        hall_name_detalies = halls_detalies_obj.search(cr, uid,[('detail_id','=',hall_id)],context=context)
        for l in hall_name_detalies:   
            deta_list=halls_detalies_obj.browse(cr,uid,l,context=context).name
            string+=(deta_list+'\n')
        return {'value': {'all_service':string}}
                
    
    
    def _create_hospitaly_order(self, cr, uid,id, context={}):
        """ Finish the hall lock order  and create hospitaly service order in state excute hosplity service
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        hospitality_service_obj=self.pool.get('hospitality.service')
        order_line_obj=self.pool.get('order.lines')
        halls_names_obj=self.pool.get('halls.names')
        for hall in self.browse(cr, uid, id, context=context):
            hospitality_id = hospitality_service_obj.create(cr, uid, {               
                 'date': time.strftime('%Y-%m-%d'),
                 'date_of_execution': hall.date_from,
                 'company_id': hall.company_id.id, 
                 'department_id': hall.department_id.id,
                 'state': 'approved_sc',
                 'notes': hall.Purpose,
                'hospilty_place': hall.hall_id.name,
                'no_day':hall.no_day,

                                    }, context=context)
            #wf_service.trg_validate(uid, 'halls.lock', id, 'approved_sc', cr)
            hospitlaty_no = hospitality_service_obj.browse(cr,uid,hospitality_id,context=context).id
            if len(hall.service_order)>0:
                 for l in hall.service_order:
                    order_id_dic =order_line_obj.create(cr,uid,{
                       'service_sort':order_line_obj.browse(cr, uid,l.id,context=context).service_sort,
                       'service_type':order_line_obj.browse(cr, uid,l.id,context=context).service_type.id,
                       'service_qty':order_line_obj.browse(cr, uid,l.id,context=context).service_qty,  
                       'order_id':hospitlaty_no               
                        },context=context)
                    
            if halls_names_obj.browse(cr,uid,hall.hall_id.id,context=context).used==False:        
               hall_name_id = halls_names_obj.write(cr, uid,hall.hall_id.id,{               
                 'lock_begin_date': hall.date_from,
                 'lock_end_date': hall.date_to,
                 'used': True,
                                    }, context=context)    
   
        return True 
    
    
    
    """ Workflow Functions"""
    
    def confirmed_d(self, cr, uid, ids,context=None):  
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

    def approved(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'approved'.
	@return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'approved'},context=context)
        return True

    def approved_sc(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'approved_sc'.
	@return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'approved_sc'},context=context)
        return True


    def done(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'done' and creates hospitality request.
	@return: Boolean True
        """
        wf_service = netsvc.LocalService("workflow")
        payment_enrich_obj = self.pool.get('payment.enrich')
        payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')
        for record in self.browse(cr, uid, ids, context=context):
	    if record.multi_service == 'extrnal_hospitality_service' :
        	self._create_hospitaly_order(cr,uid,ids,context)
            if record.payment_selection == 'enrich':
				#details = smart_str('Public Relation Request No:'+record.name+'\nProcedure For:'+record.procedure_for+'\nprocedure:'+record.procedure_id.name+'\nPurpose:'+record.purpose.name)
				details = 'Halls Locks Request No:'+record.name+"\nPurpose:"+record.Purpose
				enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					'enrich_id':record.enrich_category.id,
                        		'cost': record.cost,
					'date':time.strftime('%Y-%m-%d'),
					'state':'draft',
                        		'name':details,
					'department_id':record.department_id.id,

                            				}, context=context)
        self.write(cr, uid, ids, {'state':'done'}) 
        return True

    def cansal_lock(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'cansal_lock' and cancelling the lock set hall as a free to be used.
	@return: Boolean True
        """
        halls_names_obj=self.pool.get('halls.names')
        hall_id=self.browse(cr,uid,ids,context=context)[0].hall_id.id
        hall_name_id = halls_names_obj.write(cr, uid,hall_id,{               
                'lock_begin_date':  None ,
                 'lock_end_date':  None ,
                 'used': False,}),
        self.write(cr, uid, ids, {'state':'cansal_lock'}) 
        return True
    
    def change_lock(self,cr,uid,ids,context=None):
        """
	Method updates halls.names where it set the hall as a free hall to be used by cancelling the lock .
	@return: Boolean True
        """
        halls_names_obj=self.pool.get('halls.names')
        hall_id=self.browse(cr,uid,ids,context=context)[0].hall_id.id
        hall_name_id = halls_names_obj.write(cr, uid,hall_id,{               
                'lock_begin_date':  None ,
                 'lock_end_date':  None ,
                 'used': False,}),
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            wf_service.trg_delete(uid, 'halls.lock', s_id, cr)            
            wf_service.trg_create(uid, 'halls.lock', s_id, cr)
            wf_service.trg_validate(uid,'halls.lock',s_id,'draft', cr)
            wf_service.trg_validate(uid,'halls.lock',s_id,'confirmed_d', cr)
            wf_service.trg_validate(uid,'halls.lock',s_id,'confirmed', cr)
            wf_service.trg_validate(uid,'halls.lock',s_id,' approved', cr)
            wf_service.trg_validate(uid,'halls.lock',s_id,' approved_sc', cr)


        #self.write(cr, uid, ids, {'state':'change_lock'}) 
        return True

    def cancel(self, cr, uid, ids, context=None):
        """
	Method changes state of To 'cancel'.
	@return: Boolean True
        """
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
            wf_service.trg_delete(uid, 'halls.lock', s_id, cr)            
            wf_service.trg_create(uid, 'halls.lock', s_id, cr)
        return True


