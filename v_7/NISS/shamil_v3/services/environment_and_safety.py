# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv
import time
import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import netsvc
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar


#----------------------------------------
# Class contract_category
#----------------------------------------
class contract_category(osv.Model):

    def _check_recursion(self, cr, uid, ids, context=None):
        """
        Method that checks if the given ids still has a parent or not.
        @return: Boolean True or False      
        """
        if context is None:
            context = {}
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from contract_category where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True


    _name = 'contract.category'
    _description = 'Contract Category'
    _columns = {
        'name':fields.char('Name', size=64, required=True, select=True),
        'parent_id': fields.many2one('contract.category','Parent Category', select=True, ondelete='cascade'),
        'templet_id': fields.many2one('account.account.template','Account Templet'),
        'code': fields.related('templet_id','code',type='char',relation='account.account.template',string='Code', store=True, readonly=True),
        'name_type': fields.many2one('account.account.type','Account_type'),
        'journal_id': fields.property('account.journal',
            relation='account.journal', type='many2one',
            string='Journal', view_load=True,
            help="When create account ratification, this is the Accounting Journal in which ratification will be post."),
        
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



#----------------------------------------
# Class environment and safety
#----------------------------------------
class environment_and_safety(osv.Model):
    
    def create(self, cr, user, vals, context=None):
        """
        Method that overwrites create method to set a new sequence for every environment and safety record as a name.
        @param vals: Dictionary that contains the entered data
        @return: Super create method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'environment.and.safety')
        return super(environment_and_safety, self).create(cr, user, vals, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        Method that overwrites copy method to duplicate the current record and updates name (sequence) field with a new value .
        @param default: Dictionary of data
        @return: Super copy method
        """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'environment.and.safety'),
            
        })
        return super(environment_and_safety, self).copy(cr, uid, id, default, context)    

        
    STATE_SELECTION = [
    ('draft', 'Department Section Manger'),
    ('confirmed', 'Managment Manger'),
    ('confirmed_m', 'General Department Manger'),
    ('approv_gm', 'Aprove General Department Manger'),
    ('head', 'Head Manger'),
    ('admin_affair', 'Admin affair manger'),
    ('service_section', 'Service Section Manger'),
    ('execute', 'Officer Excute'),
    ('cancel', 'cansal'), 
    ]
    
    
    _name = "environment.and.safety"
    _description = 'Environment And Safety'
    _columns = {
    'name':fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the environment and safety"),
    'date' :fields.date('Date of request',readonly=True),
    'partner_id':fields.many2one('res.partner', 'Partner',states={'execute':[('required',True)],'cancel':[('readonly',True)]}),
    'category_id':fields.many2one('contract.category', 'Category',states={'execute':[('required',True)],'cancel':[('readonly',True)]}),
    'date_of_rent':fields.date('Date of Rent',required=True,states={'confirmed_d':[('readonly',True)],'cancel':[('readonly',True)]} ),
    'date_of_return':fields.date('Date of Retrieved',required=True,states={'confirmed_d':[('readonly',True)],'cancel':[('readonly',True)]} ),
    'cost_of_contract': fields.float('Cost of Rent',digits=(16, 4),states={'execute':[('required',True)],'cancel':[('readonly',True)]}), 
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),    
    'notes': fields.text('Notes', size=256 ,states={'confirmed_d':[('readonly',True)],'cancel':[('readonly',True)]}),
    'company_id': fields.many2one('res.company','Company',readonly=True),
    'department_id': fields.many2one('hr.department','Departmen Name',states={'cancel':[('readonly',True)]}),
    'contract_fees_ids':fields.one2many('contract.fees', 'contract_id' , 'Fees',states={'execute':[('required',True)],'cancel':[('readonly',True)]}), 
    'fees_total_amount': fields.float('Fees Total Amount', digits=(16,2)),
    'type_contract': fields.selection([('rent','Rented Buliding'),('contract','Contract')],'Contract Type', required=True, select=True,states={'confirmed_d':[('readonly',True)],'cancel':[('readonly',True)]}),    
    'building_rent':fields.char('Building Name', size=64,states={'cancel':[('readonly',True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),   
    'taxes_id': fields.many2many('account.tax', 'environment_and_safety_tax', 'environment_and_safety_id', 'tax_id', 'Taxes',states={'confirmed_d':[('readonly',True)],'cancel':[('readonly',True)]}), 
    
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'environment and safety Reference must be unique !'), 
                        
        ]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'user_id': lambda self, cr, uid, context: uid,                
                'date': time.strftime('%Y-%m-%d'),
                'date_of_rent': time.strftime('%Y-%m-%d'),
                'date_of_return': time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'environment.and.safety', context=c),
                'cost_of_contract':0.0,
                'state': 'draft',
                
                }

#workflow function
    def rented(self, cr, uid, ids, context=None):  
        """
        Method that checks wether the type is contract or not.
        @return: Boolean True or False
        """           
        for record in self.browse(cr, uid, ids):
            if record.type_contract== "contract":
                return False
        return True
    
    def confirmed(self, cr, uid, ids, context=None): 
        """
        Workflow method that changes the state to 'confirmed'.
        @return: Boolean True 
        """ 
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True
    
    def confirmed_m(self, cr, uid, ids, context=None): 
        """
        Workflow method that changes the state to 'confirmed_m'.
        @return: Boolean True 
        """             
        self.write(cr, uid, ids, {'state':'confirmed_m'})
        return True
    
    def confirmed_gm(self, cr, uid, ids, context=None):
        """
        Workflow method that changes the state to 'confirmed_gm'.
        @return: Boolean True 
        """                
        self.write(cr, uid, ids, {'state':'confirmed_gm'})
        return True
    
    def head(self, cr, uid, ids, context=None):      
        """
        Workflow method that changes the state to 'head'.
        @return: Boolean True 
        """          
        self.write(cr, uid, ids, {'state':'head'})
        return True

    def approv_gm(self, cr, uid, ids, context=None): 
        """
        Workflow method that changes the state to 'admin_affair'.
        @return: Boolean True 
        """              
        self.write(cr, uid, ids, {'state':'approv_gm'})
        return True
    
    def admin_affair(self, cr, uid, ids, context=None):   
        """
        Workflow method that changes the state to 'admin_affair'.
        @return: Boolean True 
        """            
        self.write(cr, uid, ids, {'state':'admin_affair'})
        return True
    
    def service_section(self, cr, uid, ids, context=None):
        """
        Workflow method that changes the state to 'service_section'.
        @return: Boolean True 
        """               
        self.write(cr, uid, ids, {'state':'service_section'})
        return True
    
    def execute(self, cr, uid, ids, context=None): 
        """
        Workflow method that changes the state to 'execute'.
        @return: Boolean True 
        """              
        self.write(cr, uid, ids, {'state':'execute'})
        return True

   
    def cancel(self, cr, uid, ids, notes='', context=None):
        """
        Method changes state of To 'cancel' and writes notes about the the cancellation.
        @return: Boolean True
        """ 
        # Cancel the environment and safety 
        notes = ""
        u = self.browse(cr, uid, ids)[0].user_id.name
        notes = notes +'\n'+'environment and safety Request Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u       
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """
        Method resets the environment and safety record to 'draft' , deletes the old workflow and creates a new one.
        @return: Boolean True       
        """
        # Reset the Monitoring Press to draft 
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'environment.and.safety', s_id, cr)            
            wf_service.trg_create(uid, 'environment.and.safety', s_id, cr)
        return True

    def create_fees(self,cr,uid,ids,context={}):
        """
        Method creates a contract.fees and depat.cost records.
        @return: Id of the created fees     
        """
        fees_obj = self.pool.get('contract.fees')
        depart_obj = self.pool.get('depat.cost')
        for contract in self.browse(cr,uid,ids):
            fees_id = fees_obj.create(cr,uid,{'contract_id' : contract.id})  
            dep_id=depart_obj.create(cr,uid,{'dep_name':fees_id})
            if  contract.type_contract=='rent':
                 depart_obj.write(cr,uid,dep_id,{'department_id': contract.department_id.id})
            
        return fees_id
    



class contract_fees(osv.Model):
    
    
    _name = 'contract.fees'
    _description = "Contract Fees"
    _columns = { 
        'fees_date':fields.date('Fees Date',states={'done':[('readonly',True)]}),
        'contract_id': fields.many2one('environment.and.safety', 'Contract',),
        'fees_amount': fields.float('Fees Amount', digits=(16,2),readonly=True), 
        'dep_fees':fields.one2many('depat.cost','dep_name','Department Cost',states={'done':[('readonly',True)]}),               
        'year': fields.char('Year',size=32,readonly=True ),
        'month': fields.char('Month',size=32,readonly=True ),
        'visible_month': fields.char('Month',size=32,readonly=True ),      
        'no_month': fields.integer('No of Month calculate',size=32,states={'done':[('readonly',True)]}),
        'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True),
        'state' : fields.selection([('draft','Draft'),('confirm','Confirmed'),('section_depart','Section Department'),('done','Done'),('cancel','Cancel')],'State'), 
       'final_total': fields.float('Final Total',digits=(16, 4),readonly=True),
      
    } 
               
                
    _defaults = {
                 'fees_amount': 0.0,
                 'state' : 'draft',
                 'no_month':1,

      }        
    
           
    def section_depart(self,cr, uid, ids, context=None):                  
        self.write(cr, uid, ids, {'state':'section_depart'})
        return True    
    def confirm(self,cr,uid,ids,context={}):
        """
        Method that computs the fees amount.
        @return: Boolean True 
        """ 
        new_amount = 0.0
        all_amount=0.0
        amo_tax=0.0
        i=0
        month=''
        visible_month=''
        wak=0.0
        mont_list=[]
        list_month=[]
        year_list=[]
        depart_obj = self.pool.get('depat.cost')
        contract_obj = self.pool.get('environment.and.safety')
        for fees in self.browse(cr, uid, ids): 
            month_pre= time.strptime(fees.fees_date, '%Y-%m-%d').tm_mon
            year= time.strptime(fees.fees_date, '%Y-%m-%d').tm_year
            while i <fees.no_month:
                month+=str(i+month_pre)
                visible_month+=str(i+month_pre)+'_'
                i+=1         
            contract = fees.contract_id
            dep_cost=fees.dep_fees    
            for dep in dep_cost:
                detct_day=round((dep.cost/30)*dep.deduct_days,2)
                detct_mount=round(dep.deduct_amount,2)
                if dep.rate_need == '1':
                    rate=round(dep.percentage_rating/100,2)
                else:
                    rate=0.0
                rate_dectu=detct_day+detct_mount+rate
                if rate_dectu>dep.cost:
                    raise osv.except_osv(_('Detuction mount  !'),_('The total of Dectuction mount of more than Department Cost ..')) 
                all_amount +=dep.cost
                fees_dict={'amount_with_tax':(dep.cost*fees.no_month)+dep.amount_total-rate_dectu,'mount_afer_detcut_rat' :rate_dectu}
                depart_obj.write(cr,uid,dep.id,fees_dict)
                wak=(dep.cost*fees.no_month)+dep.amount_total-rate_dectu
                amo_tax+=wak
            if all_amount > contract.cost_of_contract :
                    raise osv.except_osv(_('Amount exceed  !'), _('The total fees amount well be more than the contract amount ..'))               
            cr.execute('''SELECT distinct 
  contract_fees.month as month,
  contract_fees.year as year
FROM 
  public.contract_fees, 
  public.environment_and_safety
WHERE 
  environment_and_safety.id = contract_fees.contract_id and contract_fees.contract_id=%s'''%contract.id)
            month_dic =  cr.dictfetchall()
            for m in  month_dic:
                mont_list.append(m['month']) 
            for n in mont_list:
                 list_month.append(n)
            for l in month :
               if l in list_month and int(time.strftime('%Y'))==year:
                   raise osv.except_osv(_('month transfer !'),_('This Month Already Calculate ..'))         
        add_mount=(all_amount*fees.no_month)
        self.write(cr,uid,ids,{'state' : 'confirm','fees_amount':add_mount,'month':month,'year':year,'visible_month':visible_month,'final_total':amo_tax}), 
        new_amount=(contract.fees_total_amount+add_mount)
        globals()['mou']=new_amount
        if contract.cost_of_contract<new_amount:
            raise osv.except_osv(_('Amount exceed  !'),_('The total Amount of  more than Contract mount is Finsh ..'))  
        if contract.cost_of_contract==new_amount:
            contract.write({'state':'cancel'})
        return True

    
    def create_invoice(self,cr,uid,ids,context={}):

        """ create a financial voucher Contract
        @return: True
        """
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        account_period_obj = self.pool.get('account.period')
        account_budget_obj=self.pool.get('account.budget.confirmation')
        affairs_account_obj = self.pool.get('admin_affairs.account')
        admin_affairs_model_obj = self.pool.get('admin.affairs.model')
        #model_id = admin_affairs_model_obj.search(cr, uid, [('model','=','environment.and.safety')], context=context)[0]          
        #affairs_account = affairs_account_obj.search(cr, uid, [('model_id','=',model_id)], context=context)
        #if not affairs_account:
        #   raise osv.except_osv(_('Warning !'), _('Please insert Journal For Enviroment and safety'))
        #affairs_account_id = affairs_account[0]                        
        #affairs_account_record = affairs_account_obj.browse(cr, uid, affairs_account_id,context=context)
        for cont in self.browse(cr, uid, ids, context=context):
            contract=cont.contract_id
            #period= account_period_obj.find(cr, uid, dt=contract.date,context=context)[0]
            #account_ids = account_obj.search(cr, uid, [('code','=',str(contract.category_id.code))], context=context)
            #journal_ids =  account_journal_obj.search(cr, uid, [('name','=',contract.category_id.name_type.name)], context=context)
            #journal_id = affairs_account_record.journal_id.id
            #analytic_id = affairs_account_record.analytic_id.id
            #account_id = affairs_account_record.account_id.id
	    if not contract.category_id.account_id:
            	raise osv.except_osv(_('Warning !'), _('Please insert Category Account Configuration For Enviroment and safety'))
            journal_id = contract.category_id.journal_id.id
            analytic_id = contract.category_id.analytic_id.id
            account_id = contract.category_id.account_id.id
            #account_id = account_ids[0]
            #account_analytic_id=account_analytic_ids[0]
            voucher_id_dict={}
            voucher_line_dict={}
            # Creating Voucher / Ratitication
            voucher_id_dict={
                 'amount':cont.final_total,
                 'journal_id':journal_id , 
                 'type': 'ratification',
                 'date': time.strftime('%Y-%m-%d'),
                 'partner_id': contract.partner_id.id,
                 'account_id' : contract.partner_id.property_account_payable.id, 
                 'department_id': contract.department_id.id,
                 'state': 'draft',
                 'notes': contract.notes,
                 'narration': 'Contract or rent No: '+contract.name ,
                'amount_in_word':amount_to_text_ar(cont.final_total),}
            voucher_line_dict = {
                             
                             'account_id': account_id,
                             'type':'dr',
                             'name': contract.name,
                               }
            cr.execute('''SELECT distinct
  a.id,
  sum(amount_with_tax) as dep_cost
FROM 
  public.environment_and_safety as en, 
  public.depat_cost as dep_cost, 
  public.hr_department as hr, 
  public.contract_fees as fes, 
  public.account_analytic_account as a
WHERE 
  en.id = fes.contract_id AND
  dep_cost.department_id = hr.id AND
  hr.analytic_account_id = a.id AND
  fes.id = dep_cost.dep_name and fes.id=%s
 group by a.id '''%cont.id)
            res =  cr.dictfetchall()
            #if contract.company_id.code =="HQ":
            voucher_id_dict=voucher_id_dict 
            voucher_id = voucher_obj.create(cr, uid,voucher_id_dict,context=context)            
            for line in res:
                   voucher_line_dict.update({'account_analytic_id': line['id'] ,'amount':line['dep_cost'],'voucher_id':voucher_id,})
                   voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)      
            """else: 
               voucher_id_dict.update({
                			'period_id': period,
                            'name': contract.name,
					        'currency_id':43,
                			'type':'purchase',})
            		voucher_id = voucher_obj.create(cr, uid,voucher_id_dict,context=context)            
            		voucher_line_dict.update({'amount':cont.final_total,'voucher_id':voucher_id,})              
            		voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)"""
            voucher_state = 'draft'
            if contract.company_id.affairs_voucher_state : 
                voucher_state = contract.company_id.affairs_voucher_state 
            if voucher_id:
           	wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
		voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)    
            voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context).number
            #copy_attachments(self,cr,uid,ids,'fuel.plan',voucher_id,'account.voucher', context)
        self.write(cr,uid,ids,{'state' : 'done','voucher_no':voucher_id}),
        #contract.write({'fees_total_amount':globals()['mou']}) 
        return True
       

    def cancel(self,cr,uid,ids,context={}):
        """
        Method changes state of To 'cancel'.
        @return: Boolean True
        """
        self.write(cr,uid,ids,{'state' : 'cancel'}),
        return True
    
    def action_cancel_draft(self, cr, uid, ids, *args):
        """
        Method resets the record to 'draft' , deletes the old workflow and creates a new one.
        @return: Boolean True       
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'contract.fees', s_id, cr)            
            wf_service.trg_create(uid, 'contract.fees', s_id, cr)
        return True 
    



class department_and_cost(osv.Model):

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        Method computes the amount of line's tax . 
        @return: Dictionary of value
        """
        fees_obj = self.pool.get('contract.fees')
        contract_obj = self.pool.get('environment.and.safety')
        res = {}
        total_with_tax= 0.0
        for cont in self.browse(cr, uid, ids, context=context):
                fees_id=fees_obj.browse(cr, uid, cont.dep_name.id, context=context)     
                contract=contract_obj.browse(cr, uid,fees_id.contract_id.id, context=context)   
                res[cont.id] = {
                'amount_total': 0.0, 
                }        
                for tax in self.pool.get('account.tax').compute_all(cr, uid,contract.taxes_id, cont.cost,1)['taxes']:
                    unit_tax= tax.get('amount', 0.0)
                    total_with_tax += unit_tax     
                res[cont.id] = {
                'amount_total':total_with_tax
            }
        return res
    
    
        
    _name = 'depat.cost'
    _description = "Department Cost"
    _columns = { 
        'department_id': fields.many2one('hr.department', 'Department',), 
        'cost':fields.float('Department Cost', digits=(16,2)),
        'dep_name':fields.many2one('contract.fees','Dep'),
        'amount_total': fields.function(_amount_all, method=True, string='Tax',
        store={
               'depat.cost': (lambda self, cr, uid, ids, c={}: ids, ['taxes_id','cost'], 10), 
            }, multi="sums"), 
        'amount_with_tax': fields.float('Fees Amount and Tax mount', digits=(16,2),readonly=True),  
       'deduct_days':fields.integer('Deduct days',size=32,),
       'deduct_amount':fields.float('Deduct amount',digits=(18,2),),
       'percentage_rating':fields.float('Percentage Rating',digits=(18,0),),  
       'mount_afer_detcut_rat':fields.float('Mount After Detcution',digits=(18,0),readonly=True),  
       'rate_need':fields.selection([('1','Cal_Rate'),('2','No_Need_Cal')],'Rate and Evaluation'),

         }
    _defaults = {
                'percentage_rating': 100,
                'rate_need':'2'
      }        



