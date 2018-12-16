# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm
import time
from datetime import datetime, date
from openerp.tools.translate import _
import decimal_precision as dp
from .copy_attachments import copy_attachments as copy_attachments
from .email_serivce import send_mail

class enrich_category(osv.osv):
    """ To manage enrich category """

    def create(self, cr, uid, vals, context=None):
        """
        create operation
        @return: super create() method
        """
        if 'type' in vals:
            if vals['type'] == 'sol_special':
                vals['current_amount'] = vals['amount']
        return super(enrich_category, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        """
        delete the enrich category record if record in draft state,
        and create log message to the deleted record.

        @return: super unlink() method
        """
        if len(self.pool.get('payment.enrich').search(cr, uid,[('enrich_category','in',ids),('state','!=','draft')], context=context)) > 0:
                raise osv.except_osv(_('Invalid Action Error'), _('Can not delete category(categories), Where there are some enrich with this category'))
        return super(enrich_category, self).unlink(cr, uid, ids, context=context)

    _name = "enrich.category"

    _description = 'enrich category'

    _columns = {
        'name': fields.char('Name', size=64,required=True ),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
        'renew':fields.boolean('Skip The General Manager In Renew'),
        'times': fields.integer('Times', size=32),
        'operation_type': fields.selection([('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'),],'Operation Type', select=True),
        'amount':fields.float('Total Amount', digits=(16,2)),
        'current_amount':fields.float('Current Amount', digits=(16,2)),
        'deposit_amount':fields.float('Deposit Amount', digits=(16,2)),
        'withdraw_amount':fields.float('Withdrawal Amount', digits=(16,2)),
        'type': fields.selection([('enrich', 'enrich'), ('solidarity', 'solidarity'),
         ('sol_special', 'special'),],'Type', select=True),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'enrich.category', context=c),
    }

    def deposit(self, cr, uid, ids, amount, context=None):
        """ 
        deposit in the box.
        param: amount:amount to deposit

        @return: Boolean of True or False
        """
        record = self.browse(cr, uid, ids, context=context)[0]
        current_amount = record.current_amount
        deposit_amount = record.deposit_amount
        record.write({'current_amount':current_amount + amount,
                      'deposit_amount':deposit_amount + amount })
        return True
    
    def withdraw(self, cr, uid, ids, amount, context=None):
        """ 
        withdraw from the box.
        param: amount:amount to withdraw

        @return: Boolean of True or False
        """
        record = self.browse(cr, uid, ids, context=context)[0]
        current_amount = record.current_amount
        withdraw_amount = record.withdraw_amount
        if amount > current_amount:
            raise osv.except_osv(_('Constraint Error'), _("The the amount is greater than the Current Money!"))

        record.write({'current_amount':current_amount - amount,
                      'withdraw_amount':withdraw_amount + amount })
        return True

    def _check_unique_insesitive(self, cr, uid, ids, context=None):
        """ 
        Check uniqueness of enrich category name.

        @return: Boolean of True or False
        """
        for category in self.browse(cr, uid, ids, context=context):
            if len(self.search(cr, uid, [('name','=ilike',category.name)],  context=context)) > 1:
                raise osv.except_osv(_('Constraint Error'), _("The Name Must Be Unique!"))
        return True

    _constraints = [
        (_check_unique_insesitive, '', ['name'])
    ]


class  payment_enrich(osv.osv):
    """ To manage enrich operations """
    def create(self, cr, uid, vals, context=None):
        """
        Create new entry sequence for every payment enrich.

        @param vals: list of record to be approved
        @param context: context arguments, like lang, time zone
        @return: super create() method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'payment.enrich')
        
        #for the case of the solidarity box request
        if 'amount' not in vals:
            vals['amount']=self.pool.get('enrich.category').read(cr, uid, vals['enrich_category'], ['amount'], context=context)['amount']

        return super(payment_enrich, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        """
        write vals in selected enrichs.
        @return :ids of enrich
        """
        #for the case of the solidarity box request
        if context:
            if 'default_type' in context and context['default_type'] == 'solidarity':
                if 'enrich_category' in vals:
                    vals['amount']=self.pool.get('enrich.category').read(cr, uid, vals['enrich_category'], ['amount'], context=context)['amount']
        return super(payment_enrich, self).write(cr, uid, ids, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy() method
        """
        if default is None:
            default = {}
        default.update({'name': self.pool.get('ir.sequence').get(cr, uid, 'payment.enrich'),'state':'draft','month':None,'enrich_lines':None,
            'expenditure_voucher_id':None,'voucher_id':None,'approved_date':None})
        return super(payment_enrich, self).copy(cr, uid, id, default, context)

    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """
        Functional field function to finds the value of total paid of enrich.

        @param field_name: list contains name of fields that call this method
        @param arg: extra argument
        @return: dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in record.enrich_lines:
                if line.state == 'done' :
                    val += line.cost
            res[record.id] = {
            'paid_amount':val,
            'residual_amount':record.amount - val,
            }
        return res

    def unlink(self, cr, uid, ids, context=None):
        """
        delete the enrich payment record if record in draft or cancel state,
        and create log message to the deleted record.

        @return: super unlink() method
        """
        payenrich = self.read(cr, uid, ids, ['state'], context=context)
        for s in payenrich:
            if s['state'] not in ['draft', 'cancel']:
                raise osv.except_osv(_('Invalid Action Error'), _('In Order To Delete A Service Request Order(s), It Must Be Cancelled First!'))
        return super(payment_enrich, self).unlink(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        """
        Making Analytic Account name appear like "code name".

        @return: dictionary,name of all analytic account
        """
        return [(r.id, (r.month and r.month+'-' or '')+"Month" +'-'+ (r.desc and r.desc+' ' or '') +'-'+ r.name) for r in self.browse(cr, uid, ids, context=context)]

    """STATE_SELECTION = [
                        ('draft', 'Draft'),
                        ('Requested', 'Requested'),
                        ('Admin_affairs_manager_confirmed', 'Admin Affair Manager Confirmed'),
                        ('Account_manager_approved', 'Account Manager Approved'),
                        ('done', 'Done'),
                        ('cancel', 'Cancel'),
                ]"""
    STATE_SELECTION = [
                        ('draft', 'Draft'),
                        ('confirm_so', 'Service Officer'),
                        ('confirm_ss', 'Service Section Manager'),
                        ('Admin_affairs_manager_confirmed', 'Admin Affair Manager Confirmed'),
                        #use in solidarety box view
                        ('request', 'Request'),
                        ('social_of', 'Social Officer'),
                        ('social_mg', 'Social Office Manager'),

                        ('confirm_hf', 'Human resources and Financial Manager'),
                        ('done', 'Done'),
                        ('cancel', 'Cancel'),
                        ('closed', 'Closed'),
                ]
    def _get_lines(self, cr, uid, ids, context=None):
        """
        Method that maps record ids of a trigger model to ids of the corresponding records 
        in the source model (whose field values need to be recomputed).
        
        @param: list of statement line ids
        @return:  list of statement ids
        """
        List=[]
        if ids:
            line = self.pool.get('payment.enrich.lines').browse(cr, uid, ids[0], context=context)
                
            record = line.enrich_id
            val = 0.0
            for line in record.enrich_lines:
                if line.state == 'done' :
                    val += line.cost
            res = {
            'paid_amount':val,
            'residual_amount':record.amount - val,
            }
            record.write(res)
        return List

    _name = "payment.enrich"

    _description = 'Payment Enrich'

    _order = "name desc"

    _columns = {
        'name':fields.char('Reference', size=64, required=False, select=True, readonly=True  , help="unique number of the Payment Enrich"),
        'date' :fields.date('Date',required=True),
        'month': fields.selection([(str(n),str(n)) for n in range(1,13)],'Month'),
        'year': fields.integer('Year',size=32),
        'amount':fields.float('Total Amount', digits=(16,2)),
        'residual_amount':fields.function(_amount_all,multi='amount', method=True, digits=(16,2), string='Residual Amount' , 
            store = {'payment.enrich': (lambda self, cr, uid, ids, c={}: ids, [],10),
                     'payment.enrich.lines': (_get_lines, ['amount','state'], 10),}, readonly=True),
        'paid_amount':fields.function(_amount_all,multi='amount', method=True, digits=(16,2), string='Paid Amount' ,store = {'payment.enrich':  (lambda self, cr, uid, ids, c={}: ids, [],10)}, readonly=True),
        'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
        'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
        'notes': fields.text('Notes', size=256 ,states={'done':[('readonly',True)]}),
        'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
        'enrich_category':fields.many2one('enrich.category','Enrich Category',readonly=True,states={'draft':[('readonly',False)]}),
        'department_id': fields.many2one('hr.department',string ='Department',required=False ),
        'enrich_lines': fields.one2many('payment.enrich.lines', 'enrich_id' , 'Enrich line',states={'closed':[('readonly',True)]}),
        'voucher_id': fields.many2one('account.voucher','Voucher'),
        'desc': fields.char('Description', size=256,readonly=True,states={'draft':[('readonly',False)]},),
        'expenditure_voucher_id':fields.many2one('account.voucher','Expenditure Voucher'),
        'renew':fields.boolean('Renew'),
        'approved_date' :fields.date('Approved Date'),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'type': fields.related('enrich_category', 'type', type='selection', selection=[('enrich', 'enrich'), ('solidarity', 'solidarity')], string='Type'),
        'renew_enrich_id': fields.many2one('payment.enrich', string ='Related Enrich'),
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('Enrich Payment Reference Must Be Unique!')),
        ('enrich_item_uniq', 'unique(month,year,enrich_category,department_id)', _('Month, Year, Enrich Category and Department Must Be Unique!')),

    ]

    def _check_cost(self, cr, uid, ids, context=None):
        """
        Check if cost is greater than zero.

        @return: boolean true of false
        """
        for enrich in self.browse(cr, uid, ids, context=context):
            if enrich.amount <= 0:
                raise osv.except_osv(_('ValidateError'), _('The Cost Must Be Greater Than Zero!'))
        return True

    _constraints = [
        #(_check_cost, '', ['']),
    ]

    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'user_id': lambda self, cr, uid, context: uid,
        'date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'year': int(time.strftime('%Y')),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'payment.enrich', context=c),
    }

    def on_category_change(self, cr, uid, ids, enrich_category, context=None):
        """
    	On change enrich_category field value function gets the amount  of enrich_category.
    	@return: amount of enrich_category
    	"""
    	enrich_category_obj=self.pool.get('enrich.category').browse(cr, uid, enrich_category, context=context)
    	amount=enrich_category_obj.amount

    	return {
    	'value': {
                'amount': amount,
                }
        }
    def on_change_renew(self, cr, uid, ids, enrich_id, context=None):
        """
        on change of renew enrich get the amount form related enrich to the new one
        @return the amount of related enrich
        """
        enrich = self.browse(cr, uid, enrich_id, context=context)
    	amount=enrich.amount

    	return {
    	'value': {
                'amount': amount,
                }
        }

    def confirm_so(self, cr, uid, ids,context=None):
        """
        Workflow function changes state Requested and check record amount.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'confirm_so'}, context=context)

    def confirm_ss(self, cr, uid, ids,context=None):
        """
        Workflow function changes state Requested and check record amount.

        @return: write state
        """
        send_mail(self, cr, uid, ids[0], 'admin_affairs.group_admin_affair_manager',unicode(' طلب نثرية', 'utf-8'), unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)
        return self.write(cr, uid, ids, {'state':'confirm_ss'}, context=context)

    def Admin_affairs_manager_confirmed(self, cr, uid, ids,context=None):
        """
        Workflow function changes state Admin_affairs_manager_confirmed.

        @return: write state
        """
        send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager',unicode(' طلب نثرية', 'utf-8'), unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)
        return self.write(cr, uid, ids, {'state':'Admin_affairs_manager_confirmed'}, context=context)


    def confirm_hf(self, cr, uid, ids,context=None):
        """
        Workflow function changes state Requested and check record amount.

        @return: write state
        """
        category = self.browse(cr,uid,ids[0],context=context).enrich_category.renew
        if context.get('renew') and category:
            send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager',unicode(' طلب نثرية', 'utf-8'), unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)
            return self.done(cr, uid, ids,context)
        else:
            send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager',unicode(' طلب نثرية', 'utf-8'), unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)
            return self.write(cr, uid, ids, {'state':'confirm_hf'}, context=context)


    def done(self, cr, uid, ids,context=None):
        partner_id = self.pool.get('res.users').read(cr, uid, uid,['partner_id'],context=context)['partner_id'][0]
        for enrich in self.browse(cr, uid, ids, context=context):
            for line in enrich.enrich_lines:
                if line.state == 'draft':
                    raise osv.except_osv(_('Invalid Action Error'), _('Please Close All Payment Lines Before Closing The Enrich!'))
            account_voucher=self.pool.get('account.voucher')
            sub_lines = []
            admin_affairs_account = self.pool.get('admin_affairs.account')
            account_id = admin_affairs_account.browse(cr, uid,admin_affairs_account.search(cr, uid, [('model_id','=','payment.enrich')]), context=context)
            if not account_id:
                    raise osv.except_osv(_("Configuration Error"),_('There Is No Configuration For Enrichs Accounting!'))
            account_id = account_id[0]


            datal = {
                        'amount': enrich.amount,
                        "account_id":account_id.account_id.id,
                        "account_analytic_id":(account_id.analytic_id and account_id.analytic_id.id) or (enrich.department_id and (enrich.department_id.analytic_account_id and enrich.department_id.analytic_account_id.id) or False),
                        'name': enrich.enrich_category.name + str(enrich.month)+ str(enrich.year),
                    }
            sub_lines.append((0,0,datal))
            vouch_id=account_voucher.create(cr, uid,{
                                                        "partner_id":partner_id,
                                                        "account_id":account_id.account_id.id,
                                                        "company_id":enrich.company_id.id,
                                                        "date":enrich.date,
                                                        "journal_id":account_id.journal_id and account_id.journal_id.id or False,
                                                        "reference":enrich.name,
                                                        "line_dr_ids":sub_lines,
                                                        "type":'purchase',
                                                        'amount': enrich.amount,
                                                    }, context=context)

            
            copy_attachments(self,cr,uid,ids,'payment.enrich',vouch_id,'account.voucher', context=context)
            self.write(cr, uid, enrich.id, {'state':'done', 'voucher_id':vouch_id, \
            'approved_date':date.today()},context=context)

            #send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager',unicode(' طلب نثرية', 'utf-8'), unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)
            
        return ids
        


    def request(self, cr, uid, ids,context=None):
        """
        Workflow function changes state Requested and check record amount.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'request'}, context=context)

    def social_of(self, cr, uid, ids,context=None):
        """
        Workflow function changes state social_of.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'social_of'}, context=context)

    def social_mg(self, cr, uid, ids,context=None):
        """
        Workflow function changes state social_mg.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'social_mg'}, context=context)


    def done_solidarity(self, cr, uid, ids,context=None):
        """
        write done state in solidarity request.

        @return: write state
        """
        record = self.browse(cr, uid, ids, context=context)[0]
        if record.type == 'solidarity':
            employee = record.employee_id.id
            amount = record.amount
            category_obj = self.pool.get('enrich.category')

            category = record.enrich_category
            max_amount = category.amount
            max_times = category.times

            rest_money = category_obj.search(cr, uid, [('type', '=', 'sol_special')], context=context)
            rest_money = category_obj.browse(cr, uid, rest_money, context=context)
            
            if not rest_money:
                raise osv.except_osv(_('Constraint Error'), _("The No Residual Money!"))

            if category.operation_type == 'deposit':
                #increese the rest_money
                rest_money[0].deposit(amount)
                #rest_money[0].write({'amount':rest_money[0].amount + amount})
            if category.operation_type == 'withdrawal':    
                #get the amount of the first record in the configuration
                rest_money_amount = rest_money[0].amount


                if amount > max_amount:
                    raise osv.except_osv(_('Constraint Error'), _("The the amount is greater than the amount in the category!"))
                
                #times when this employee get money from this category
                old_times = self.search(cr, uid, [('employee_id', '=', employee), ('type', '=', 'solidarity'), ('enrich_category', '=', category.id), ('state', '=', 'done')])
                times = 1
                if old_times:
                    times += len(old_times)
                if times > max_times:
                    raise osv.except_osv(_('Constraint Error'), _("This employee get all chances of this category!"))

                #rest_money[0].write({'amount':rest_money[0].amount - amount})
                rest_money[0].withdraw(amount)
        return self.write(cr, uid, ids, {'state':'done',}, context=context)

    def modify_enrich(self,cr,uid,ids,context=None):
        """
        Reset the workflow and changes state to confirmed.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'Admin_affairs_manager_confirmed'}, context=context)

    def transfer(self,cr,uid,ids,context=None):
        enrich = self.pool.get('payment.enrich').browse(cr, uid,ids, context=context)[0]
        admin_affairs_account = self.pool.get('admin_affairs.account')
        account_id = admin_affairs_account.browse(cr, uid,admin_affairs_account.search(cr, uid, [('model_id','=','payment.enrich')]), context=context)
        if not account_id:
                raise osv.except_osv(_("Configuration Error"),_('There Is No Configuration For Enrichs Accounting!'))
        account_id = account_id[0]

        partner_id = self.pool.get('res.users').read(cr, uid, uid,['partner_id'],context=context)['partner_id'][0]

        list_lines = []
        sum = 0.0
        for line in enrich.enrich_lines:
            service = line.__contains__("service_id") and line.service_id.id
            line_account_id = service and admin_affairs_account.browse(cr, uid,admin_affairs_account.search(cr, uid, [('model_id','=',line.model_id),('service_id','=',line.service_id.id)]), context=context) or\
            admin_affairs_account.browse(cr, uid,admin_affairs_account.search(cr, uid, [('model_id','=',line.model_id)]), context=context)
            if not line_account_id:
                raise osv.except_osv(_("Configuration Error"),_('There Is No Configuration For Enrichs Lines Accounting!'))
            line_account_id = line_account_id[0]
            datal = {
                "account_id":line_account_id.account_id.id,
                "account_analytic_id":(account_id.analytic_id and account_id.analytic_id.id) or (enrich.department_id and (enrich.department_id.analytic_account_id and enrich.department_id.analytic_account_id.id) or False),
                "amount":line.cost,
                "name":line.name,
            }
            sum += line.cost
            list_lines.append((0,0,datal))

        data = {
                "partner_id":partner_id,
                "account_id":account_id.account_id.id,
                "reference":enrich.name,
                "company_id":enrich.company_id.id,
                "date":datetime.strptime("%d-%d-1"%(int(enrich.year),int(enrich.month)), "%Y-%m-%d"),
                "journal_id":account_id.journal_id.id,
                "line_dr_ids":list_lines,
                "type":'purchase',
                'amount':sum,
        }
        voucher = self.pool.get('account.voucher')
        v_id = voucher.create(cr, uid, data, context=context)
        copy_attachments(self,cr,uid,ids,'payment.enrich',v_id,'account.voucher', context=context)
        return self.write(cr,uid,ids ,{'expenditure_voucher_id':v_id,'state':'closed'},context=context)




    def cancel(self, cr, uid, ids, notes='', context=None):
        """
        Workflow function changes state to cancel and writes note.

        @param notes: contains information of canceling.
        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """
        Changes state to Draft and reset the workflow.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)


class  payment_enrich_lines(osv.osv):
    """ To manage admin affairs payment lines """
    _name = "payment.enrich.lines"

    _description = 'Payment Enrich Lines'

    _columns = {
        'enrich_id':fields.many2one('payment.enrich', 'Payment Enrich',readonly=True),
        'date' :fields.date('Date',readonly=True ,required=True,states={'draft':[('readonly',False)]}),
        'state': fields.selection([('draft', 'Draft'),('done', 'Done'),('cancel', 'Cancel'), ('delaied','Delaied')],'State', readonly=True, select=True),
        'cost':fields.float('Cost',digits=(18,2),readonly=True , required=True,states={'draft':[('readonly',False)]}),
        'name': fields.char('Name', size=256,required=True),
        'department_id': fields.many2one('hr.department',string ='Department'),
        'model_id': fields.selection([('payment.enrich.lines','Enrich Lines'), ('fleet.vehicle.log.contract','Vehicle Contract'),
           ('fleet.vehicle.log.fuel','Vehicle Log')],string="Model"),
        'owner_id': fields.char('Owner Id', size=256),
    }

    def _check_date(self, cr, uid,ids, context=None):
        """
        Check enrich line that its date should be within enrich month/year.

        @return: boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            line_date = datetime.strptime(str(act.date), "%Y-%m-%d")
            if int(line_date.month)!=int(act.enrich_id.month) or int(line_date.year)!=int(act.enrich_id.year):
                raise osv.except_osv(_('ValidateError'), _("Payment Enrich Date Must Be Within Enrich Month And Year %s - %s")%(act.enrich_id.month,act.enrich_id.year))
            return True

    _defaults = {
        'state': 'draft',
        'model_id':'payment.enrich.lines',
    }

    _constraints = [
        #(_check_date, '', ['']),
    ]

    def done(self,cr,uid,ids,context=None):
        """
        Workflow function changes state to done and check, update cost.

        @return: write state
        """
        for record in self.browse(cr, uid, ids, context=context):
            search_result = self.pool.get('payment.enrich').browse(cr, uid,record.enrich_id.id)
            if record.cost < 1 :
                raise osv.except_osv(_('Invalid Action Error'), _('The Entered Cost Is Wrong!'))
            if record.cost > search_result.residual_amount :
                raise osv.except_osv(_('Invalid Action Error'), _('Your Residual Balance Is Less Than Your Cost!'))
        if context:
            if 'owner' in context and 'model_id' in context:
                owner = context['owner']
                owner = int(owner)
                model_id = context['model_id']
                if str(model_id) == 'fleet.vehicle.log.contract':
                    model_obj = self.pool.get(model_id)
                    model = model_obj.browse(cr, uid, owner, context=context)
                    model.write({'state':'open'})
        return self.write(cr, uid, ids, {'state':'done'},context=context)

    def cancel(self, cr, uid, ids, context=None):
        """
        Workflow function changes state to cancel and writes note.

        @param notes: contains information of canceling
        @return: write state
        """
        if context:
            if 'owner' in context and 'model_id' in context:
                owner = context['owner']
                owner = int(owner)
                model_id = context['model_id']
                if str(model_id) == 'fleet.vehicle.log.contract':
                    model_obj = self.pool.get(model_id)
                    model = model_obj.browse(cr, uid, owner, context=context)
                    model.write({'state':'cancel','note':'إلغاء لأسباب إداربة'})
        return self.write(cr, uid, ids, {'state':'cancel'})

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """
        Changes state to Draft and reset the workflow.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'draft'})
    
    def delay(self, cr, uid, ids, context=None):
        """
        Workflow function changes state to delay .

        @return: write state
        """
        if context:
            if 'owner' in context and 'model_id' in context:
                owner = context['owner']
                owner = int(owner)
                model_id = context['model_id']
                if str(model_id) == 'fleet.vehicle.log.contract':
                    model_obj = self.pool.get(model_id)
                    model = model_obj.browse(cr, uid, owner, context=context)
                    model.write({'state':'wait','note':'تأجيل لأسباب إداربة'})
        return self.write(cr, uid, ids, {'state':'delaied'})
