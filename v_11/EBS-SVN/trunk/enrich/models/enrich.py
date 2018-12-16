# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################



#from odoo.osv import  osv,orm
from odoo import api, fields, models , exceptions,_
import time
from datetime import datetime, date
import odoo.addons.decimal_precision as dp
from num2words import num2words

#from .copy_attachments import copy_attachments as copy_attachments



class fleet_service_type(models.Model):
    """
    Manage and customize fleet service types.
    """
    _name='fleet.service.type'

    name = fields.Char(string='Name', required=True, translate=True)
    parent_id = fields.Many2one('fleet.service.type', string='Parent')
    category = fields.Selection([('contract', 'Maintenance'), ('service', 'Service'), ('both', 'Vehicle Request'),
                                  ('env_safety', 'Environment & Safety'), ('hospitality', 'Hospitality'),
                                  ('occasion', 'Occasion'), ('hall', 'Hall'), ('building', 'Building'),
                                  ('media', 'Media'),
                                  ('public_relation', 'Public Relation'), ('general', 'General'),
                                  ('insurance', 'Vehicle Insurance'), ('license', 'Vehicle License')], 'Category',
                                 required=True,default=lambda self: self._context.get('category',False))
    cost = fields.Float(string="Cost")
    building = fields.Boolean(string='Building',default=lambda self: self._context.get('building',False))
    quantity = fields.Float(string="Quantity",default=1.0)
    active = fields.Boolean(string='Active',default=True)
    child_ids = fields.One2many('fleet.service.type', 'parent_id', string='Items')
    #location_id = fields.Many2one('stock.location', string='Location')
    address = fields.Char(string='Address', )
    time_to_request = fields.Integer(string='Hours To Request', )
    users = fields.Many2many('hr.employee', string='Users')
    #hall_type = fields.Many2many('service.hall.type', string='Types'),
    #is_free = fields.Boolean(string='Free',default=False)
    is_free = fields.Selection(([('not_free','Not Free'),('free','Free')]),required=1,default="not_free",string="Free")
    price = fields.Float(string='Price')
    linked_to_hall = fields.Many2many('fleet.service.type', 'linked_to_hall_rel', 'current_hall', 'linked_hall',
                                       string='Linked')

    @api.onchange('child_ids')
    def onchange_child_ids(self):
        sum_cost = 0
        list_ids = []

        sum_cost =sum(item.cost for item in self.child_ids)
        self.cost = sum_cost



    @api.onchange('is_free')
    def onchange_free(self):
        temp = self.cost
        if self.is_free == 'free':
            temp = 0
        self.cost=temp


    def unlink(self):
        connected = self.env['payment.enrich.lines'].search([('service_id','=',self.id)])
        if connected:
            raise exceptions.ValidationError(
                _('Can not delete Service, Where there are some enrich with this service'))
        super(fleet_service_type,self).unlink()

class enrich_category(models.Model):
    """ To manage enrich category """
    _name = 'enrich.category'
    _description = 'enrich category'

    @api.model
    def create(self, vals):
        """
        create operation
        @return: super create() method
        """
        if 'type' in vals:
            if vals['type'] == 'sol_special':
                vals['current_amount'] = vals['amount']
        return super(enrich_category, self).create(vals)


    def unlink(self):
        """
        delete the enrich category record if record in draft state,
        and create log message to the deleted record.

        @return: super unlink() method
        """
        if len(self.env['payment.enrich'].search([('enrich_category','=',self.id),('state','!=','draft')])) > 0:
                raise exceptions.ValidationError( _('Can not delete category(categories), Where there are some enrich with this category'))
        return super(enrich_category, self).unlink()




    name = fields.Char('Name', size=64, required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get('enrich.category'))
    renew = fields.Boolean('Skip The General Manager In Renew')
    times = fields.Integer('Times', size=32)
    operation_type = fields.Selection([('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ], 'Operation Type',
                                       select=True)
    amount = fields.Float('Total Amount', digits=(16, 2))
    current_amount = fields.Float('Current Amount', digits=(16, 2))
    deposit_amount = fields.Float('Deposit Amount', digits=(16, 2))
    withdraw_amount = fields.Float('Withdrawal Amount', digits=(16, 2))
    type = fields.Selection([('enrich', 'enrich'), ('solidarity', 'solidarity'),
                              ('sol_special', 'special') ], 'Type')
    account_id = fields.Many2one('account.account')
    analytic_id = fields.Many2one('account.analytic.account')
    journal_id =  fields.Many2one('account.journal', required=True,string='Journal')


    def deposit(self, amount):
        """
        deposit in the box.
        param: amount:amount to deposit

        @return: Boolean of True or False
        """
        print(">>>>>>>>>>>>>>>>>>DEF DEPOSIT")
        record = self
        current_amount = record.current_amount
        deposit_amount = record.deposit_amount
        record.write({'current_amount':current_amount + amount,
                      'deposit_amount':deposit_amount + amount })
        return True

    def withdraw(self , amount):
            """
            withdraw from the box.
            param: amount:amount to withdraw

            @return: Boolean of True or False
            """
            record = self
            current_amount = record.current_amount
            withdraw_amount = record.withdraw_amount
            if amount > current_amount:
                raise exceptions.ValidationError(_('Constraint Error'), _("The the amount is greater than the Current Money!"))

            record.write({'current_amount': current_amount - amount,
                          'withdraw_amount': withdraw_amount + amount})
            return True

    @api.constrains('name')
    def _check_unique_insesitive(self):
            """
            Check uniqueness of enrich category name.

            @return: Boolean of True or False
            """
            for category in self:
                if len(self.search([('name', '=ilike', category.name)])) > 1:
                    raise exceptions.ValidationError(_("The Name Must Be Unique!"))

            return True

class payment_enrich(models.Model):
    """ To manage enrich operations """

    _name = "payment.enrich"
    _description = 'Payment Enrich'
    _order = "name desc"

    def num2word(slef , num):
        num2=num2words(num, lang='ar')
        return num2


    @api.one
    @api.depends('amount','state')
    def _amount_all(self):
        """
        Functional field function to finds the value of total paid of enrich.

        @param field_name: list contains name of fields that call this method
        @param arg: extra argument
        @return: dictionary of values
        """
        print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>AMOUNT_ALL")
        res={}
        for record in self:
            val = 0.0
            for line in record.enrich_lines:
                if line.state == 'done' :
                    val += line.cost
            self.paid_amount = val
            self.residual_amount = record.amount - val
            #res[record._origin.id] = {
            #'paid_amount':val,
            #'residual_amount':record.amount - val,
            #}
        #return res



    #_columns = {
    name = fields.Char('Reference', size=64, required=False, select=True, readonly=True,
                        help="unique number of the Payment Enrich",default=lambda self: '/')
    date = fields.Date('Date', required=True,default=time.strftime('%Y-%m-%d'))
    month = fields.Selection([(str(n), str(n)) for n in range(1, 13)], 'Month')
    year = fields.Integer('Year', size=32,default=int(time.strftime('%Y')))
    amount = fields.Float('Total Amount', digits=(16, 2))
    residual_amount = fields.Float(compute="_amount_all", digits=(16, 2),
                                       string='Residual Amount',
                                       readonly=True)
    paid_amount = fields.Float(compute="_amount_all", digits=(16, 2), string='Paid Amount',
                                   readonly=True)
    state = fields.Selection([
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

                ], 'State', readonly=True, select=True,default='draft')
    user_id = fields.Many2one('res.users', 'Responsible', readonly=True, default=lambda self: self._uid)
    notes = fields.Text('Notes', size=256, states={'done': [('readonly', True)]}
                        )
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True,default=lambda self: self.env['res.company']._company_default_get(
                                                                                                 'payment.enrich'))
    enrich_category = fields.Many2one('enrich.category', 'Enrich Category', readonly=True,
                                       states={'draft': [('readonly', False)]}
                                      )
    department_id = fields.Many2one('hr.department', string='Department', required=False)
    enrich_lines = fields.One2many('payment.enrich.lines', 'enrich_id', 'Enrich line',
                                    states={'draft': [('readonly', True)]}
                                   )
    voucher_id = fields.Many2one('account.voucher', 'Voucher')
    desc = fields.Char('Description', size=256, readonly=True, states={'draft': [('readonly', False)]}
                        )
    expenditure_voucher_id = fields.Many2one('account.voucher', 'Expenditure Voucher')
    renew = fields.Boolean('Renew')
    approved_date = fields.Date('Approved Date')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    type = fields.Selection(related='enrich_category.type',
                            string='Type')
    renew_enrich_id = fields.Many2one('payment.enrich', string='Related Enrich')
    service_id = fields.Many2one('fleet.service.type', 'Service')
    #}

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('Enrich Payment Reference Must Be Unique!')),
        ('enrich_item_uniq', 'unique(month,year,enrich_category,department_id)',
         _('Month, Year, Enrich Category and Department Must Be Unique!')),

    ]






    @api.model
    def create(self ,vals):
        """
        Create new entry sequence for every payment enrich.

        @param vals: list of record to be approved
        @param context: context arguments, like lang, time zone
        @return: super create() method
        """
        if ('name' not in vals) or (vals.get('name') == '/'):
            vals['name'] = self.env['ir.sequence'].get('payment.enrich')

        # for the case of the solidarity box request
        #need to get it in migration
        #if 'amount' not in vals:
        #    vals['amount'] = \
        #    self.env['enrich.category'].read( vals['enrich_category'] , ['amount'])['amount']

        return super(payment_enrich, self).create( vals)

    #@api.model
    def write(self , values):
        """
        write vals in selected enrichs.
        @return :ids of enrich
        """
        # for the case of the solidarity box request
        print ("<<<<<<<<<<<<<<<<<<<<<<>>>>")
        if self._context:
            if 'default_type' in self._context and self._context['default_type'] == 'solidarity':
                if 'enrich_category' in values:
                    values['amount'] = self.env['enrich.category'].read(values['enrich_category'], ['amount'],
                                                                           )['amount']
        return super(payment_enrich, self).write(values)

    #@api.one
    def copy(self,default=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy() method
        """
        if default is None:
            default = {}
        default.update(
            {'name': self.env['ir.sequence'].get('payment.enrich'), 'state': 'draft', 'month': None,
             'enrich_lines': None,
             'expenditure_voucher_id': None, 'voucher_id': None, 'approved_date': None})
        return super(payment_enrich, self).copy(default)



    def unlink(self):

        #payenrich = self.read(cr, uid, ids, ['state'], context=context)
        payenrich = self
        for s in payenrich:
            if s.state not in ['draft','cancel'] :
                raise exceptions.ValidationError(_('In Order To Delete A Service Request Order(s), It Must Be Cancelled First!'))
        return super(payment_enrich, self).unlink()



    def name_get(self):
        """
        Making Analytic Account name appear like "code name".

        @return: dictionary,name of all analytic account
        """
        return [
            (r.id, (r.month and r.month + '-' or '') + "Month" + '-' + (r.desc and r.desc + ' ' or '') + '-' + r.name)
            for r in self]



    @api.onchange('amount','state')
    def _get_lines(self):
        """
        Method that maps record ids of a trigger model to ids of the corresponding records
        in the source model (whose field values need to be recomputed).

        @param: list of statement line ids
        @return:  list of statement ids
        """
        List = []
        if self:

            line = self.env['payment.enrich.lines'].search([('enrich_id','=',self._origin.id)])

            record = line.enrich_id
            val = 0.0
            for line in record.enrich_lines:
                if line.state == 'done':
                    val += line.cost
            res = {
                'paid_amount': val,
                'residual_amount': record.amount - val,
            }
            self.paid_amount,self.residual_amount = val , record.amount - val
            #record.write(res)
            #return List

    def _check_cost(self):
        """
        Check if cost is greater than zero.

        @return: boolean true of false
        """
        for enrich in self:
            if enrich.amount <= 0:
                raise exceptions.ValidationError(_('The Cost Must Be Greater Than Zero!'))
        return True

    _constraints = [
        # (_check_cost, '', ['']),
    ]


    @api.onchange('enrich_category')
    def on_category_change(self):
        """
    	On change enrich_category field value function gets the amount  of enrich_category.
    	@return: amount of enrich_category
    	"""
        enrich_category_obj = self.enrich_category
        amount = enrich_category_obj.amount

        return {
            'value': {
                'amount': amount,
            }
        }

    @api.onchange('enrich_id')
    def on_change_renew(self):
        """
        on change of renew enrich get the amount form related enrich to the new one
        @return the amount of related enrich
        """
        enrich = self
        amount = enrich.amount

        return {
            'value': {
                'amount': amount,
            }
        }

    def confirm_so(self):
        """
        Workflow function changes state Requested and check record amount.

        @return: write state
        """
        return self.write({'state': 'confirm_so'})

    def confirm_ss(self):
        """
        Workflow function changes state Requested and check record amount.

        @return: write state
        """
        # send_mail(self, cr, uid, ids[0], 'admin_affairs.group_admin_affair_manager',unicode(' طلب نثرية', 'utf-8'), unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)
        print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>",)
        self.state = 'confirm_ss'
        #return self.write({'state': 'confirm_ss'})

    def Admin_affairs_manager_confirmed(self):
        """
        Workflow function changes state Admin_affairs_manager_confirmed.

        @return: write state
        """
        #send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager', unicode(' طلب نثرية', 'utf-8'),
        #          unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)
        return self.write({'state': 'Admin_affairs_manager_confirmed'})

    def confirm_hf(self):
        """
        Workflow function changes state Requested and check record amount.

        @return: write state
        """
        category = self.enrich_category.renew
        if self._context.get('renew') and category:
            #send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager', unicode(' طلب نثرية', 'utf-8'),
            #          unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)
            return self.done()
        else:
            #send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager',
            #          unicode(' طلب نثرية', 'utf-8'), unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)
            return self.write( {'state': 'confirm_hf'})

    def done(self):
        #partner_id = self.env['res.users'].read(cr, uid, uid, ['partner_id'], context=context)['partner_id'][0]
        partner_id = self.user_id.partner_id.id
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", partner_id)
        for enrich in self:
            for line in enrich.enrich_lines:
                if line.state == 'draft':
                    raise exceptions.ValidationError( _('Please Close All Payment Lines Before Closing The Enrich!'))

            account_voucher = self.env['account.voucher']
            sub_lines = []
            #admin_affairs_account = self.env['admin_affairs.account']
            account_id_check = self.enrich_category.account_id
            account_id = self.enrich_category
            if not account_id_check:
                raise exceptions.ValidationError(_('There Is No Configuration For Enrichs Accounting!'))


            datal = {
                'amount': enrich.amount,
                "account_id": account_id.account_id.id,
                "account_analytic_id": (account_id.analytic_id and account_id.analytic_id.id) or (
                enrich.department_id and (
                enrich.department_id.analytic_account_id and enrich.department_id.analytic_account_id.id) or False),
                'name': enrich.enrich_category.name + str(enrich.month) + str(enrich.year),
            }
            sub_lines.append((0, 0, datal))
            vouch_id = account_voucher.create( {
                "partner_id": partner_id,
                "account_id": account_id.account_id.id,
                "company_id": enrich.company_id.id,
                "date": enrich.date,
                "journal_id": account_id.journal_id and account_id.journal_id.id or False,
                "reference": enrich.name,
                #"line_dr_ids": sub_lines,
                "type": 'purchase',
                #'amount': enrich.amount,
            })
            vouch_id.amount = enrich.amount
            self.voucher_id , self.state , self.approved_date = vouch_id , 'done' , date.today()

            #copy_attachments(self, cr, uid, ids, 'payment.enrich', vouch_id, 'account.voucher', context=context)
            #self.write({'approved_date': date.today()})

            # send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager',unicode(' طلب نثرية', 'utf-8'), unicode(' طلب نثرية في إنتظارك', 'utf-8'), context=context)

        #return ids

    def request(self):
        """
        Workflow function changes state Requested and check record amount.

        @return: write state
        """
        return self.write( {'state': 'request'})

    def social_of(self):
        """
        Workflow function changes state social_of.

        @return: write state
        """
        return self.write({'state': 'social_of'})

    def social_mg(self):
        """
        Workflow function changes state social_mg.

        @return: write state
        """
        return self.write({'state': 'social_mg'})

    def done_solidarity(self):
        """
        write done state in solidarity request.

        @return: write state
        """
        record = self
        if record.type == 'solidarity':
            employee = record.employee_id.id
            amount = record.amount
            category_obj = self.env['enrich.category']

            category = record.enrich_category
            max_amount = category.amount
            max_times = category.times

            rest_money = category_obj.search([('type', '=', 'sol_special')])
            #rest_money = category_obj.browse(cr, uid, rest_money, context=context)

            if not rest_money:
                raise exceptions.ValidationError(_("The No Residual Money!"))
            if category.operation_type == 'deposit':
                # increese the rest_money
                rest_money.deposit(amount)
                # rest_money[0].write({'amount':rest_money[0].amount + amount})
            if category.operation_type == 'withdrawal':
                # get the amount of the first record in the configuration
                rest_money_amount = rest_money.amount

                if amount > max_amount:
                    raise exceptions.ValidationError(_("The the amount is greater than the amount in the category!"))

                # times when this employee get money from this category
                old_times = self.search([('employee_id', '=', employee), ('type', '=', 'solidarity'),
                                                  ('enrich_category', '=', category.id), ('state', '=', 'done')])
                times = 1
                if old_times:
                    times += len(old_times)
                if times > max_times:
                    raise exceptions.ValidationError( _("This employee get all chances of this category!"))


                # rest_money[0].write({'amount':rest_money[0].amount - amount})
                rest_money.withdraw(amount)
        return self.write({'state': 'done' })

    def modify_enrich(self):
        """
        Reset the workflow and changes state to confirmed.

        @return: write state
        """
        return self.write( {'state': 'Admin_affairs_manager_confirmed'})

    def transfer(self):
        enrich = self
        #admin_affairs_account = self.env['admin_affairs.account']
        account_id_check = enrich.enrich_category
        account_id = enrich.enrich_category
        if not account_id_check:
            raise exceptions.ValidationError(_('There Is No Configuration For Enrichs Accounting!'))


        partner_id = self.user_id.partner_id.id

        list_lines = []
        sum = 0.0
        for line in enrich.enrich_lines:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",line.__contains__("service_id") , line.service_id.id)
            service = line.__contains__("service_id") and line.service_id.id
            #to migrate
            #line_account_id = service and admin_affairs_account.browse(cr, uid, admin_affairs_account.search(cr, uid, [
            #    ('model_id', '=', line.model_id), ('service_id', '=', line.service_id.id)]), context=context) or \
            #                  admin_affairs_account.browse(cr, uid, admin_affairs_account.search(cr, uid, [
            #                      ('model_id', '=', line.model_id)]), context=context)
            #if not line_account_id:
            if not account_id_check.journal_id or not account_id_check.account_id:
                raise exceptions.ValidationError(
                    _('There Is No Configuration For Enrichs Lines Accounting!'))
            #line_account_id = line_account_id[0]
            line_account_id = account_id
            datal = {
                "account_id": line_account_id.account_id.id,
                "account_analytic_id": (account_id.analytic_id and account_id.analytic_id.id) or (
                enrich.department_id and (
                enrich.department_id.analytic_account_id and enrich.department_id.analytic_account_id.id) or False),
                "amount": line.cost,
                "name": line.name,
            }
            print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",line.cost)
            sum += line.cost
            list_lines.append((0, 0, datal))

        data = {
            "partner_id": partner_id,
            "account_id": account_id.account_id.id,
            "reference": enrich.name,
            "company_id": enrich.company_id.id,
            "date": datetime.strptime("%d-%d-1" % (int(enrich.year), int(enrich.month)), "%Y-%m-%d"),
            "journal_id": account_id.journal_id.id,
            #"line_dr_ids": list_lines,#field not found , need to be checked
            "type": 'purchase',
            #'amount': sum, # become zero *_*
        }
        voucher = self.env['account.voucher']
        v_id = voucher.create(data)
        v_id.amount = sum  # works like this

        #copy_attachments(self, cr, uid, ids, 'payment.enrich', v_id, 'account.voucher', context=context)
        self.expenditure_voucher_id = v_id
        self.state = 'closed'
        #return self.write({'expenditure_voucher_id': v_id, 'state': 'closed'})

    def cancel(self):
        """
        Workflow function changes state to cancel and writes note.

        @param notes: contains information of canceling.
        @return: write state
        """
        self.state='cancel'
        #return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def ir_action_cancel_draft(self):
        """
        Changes state to Draft and reset the workflow.

        @return: write state
        """
        self.state = 'draft'
        #return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    
class payment_enrich_lines(models.Model):
    """ To manage admin affairs payment lines """
    _name = "payment.enrich.lines"
    _description = 'Payment Enrich Lines'


    enrich_id = fields.Many2one('payment.enrich', 'Payment Enrich', readonly=True)
    date = fields.Date('Date', readonly=True, required=True, states={'draft': [('readonly', False)]}
                       )
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancel'), ('delaied', 'Delaied')], 'State',
        readonly=True, default='draft')
    cost = fields.Float('Cost', digits=(18, 2), readonly=True, required=True,
                         states={'draft': [('readonly', False)]}
                        )
    name = fields.Char('Name', size=256, required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    model_id = fields.Selection(
        [('payment.enrich.lines', 'Enrich Lines'), ('fleet.vehicle.log.contract', 'Vehicle Contract'),
         ('fleet.vehicle.log.fuel', 'Vehicle Log')],default='payment.enrich.lines', string="Model")
    owner_id = fields.Char('Owner Id', size=256)
    service_id = fields.Many2one('fleet.service.type', 'Service')


    def _check_date(self):
        """
        Check enrich line that its date should be within enrich month/year.

        @return: boolean of True or False
        """
        for act in self:
            line_date = datetime.strptime(str(act.date), "%Y-%m-%d")
            if int(line_date.month) != int(act.enrich_id.month) or int(line_date.year) != int(act.enrich_id.year):
                raise exceptions.ValidationError(_("Payment Enrich Date Must Be Within Enrich Month And Year %s - %s") % (
                                     act.enrich_id.month, act.enrich_id.year))
            return True





    def done(self):
        """
        Workflow function changes state to done and check, update cost.

        @return: write state
        """
        for record in self:
            search_result = self.env['payment.enrich'].search([('id','=',record.enrich_id.id)])
            if record.cost < 1:
                raise exceptions.ValidationError(_('The Entered Cost Is Wrong!'))
            if record.cost > search_result.residual_amount:
                raise exceptions.ValidationError(_('Your Residual Balance Is Less Than Your Cost!'))
        if self._context:
            if 'owner' in self._context and 'model_id' in self._context:
                owner = self._context['owner']
                owner = int(owner)
                model_id = self._context['model_id']
                if str(model_id) == 'fleet.vehicle.log.contract':
                    model_obj = self.env[model_id+'']
                    model = model_obj.search([('id','=',owner)])
                    model.write({'state': 'open'})
        return self.write({'state': 'done'})

    def cancel(self):
        """
        Workflow function changes state to cancel and writes note.

        @param notes: contains information of canceling
        @return: write state
        """
        if self._context:
            if 'owner' in self._context and 'model_id' in self._context:
                owner = self._context['owner']
                owner = int(owner)
                model_id = self._context['model_id']
                if str(model_id) == 'fleet.vehicle.log.contract':
                    model_obj = self.env[model_id+'']
                    model = model_obj.search([('id','=',owner)])
                    model.write({'state': 'cancel', 'note': 'إلغاء لأسباب إداربة'})
        return self.write({'state': 'cancel'})

    def ir_action_cancel_draft(self):
        """
        Changes state to Draft and reset the workflow.

        @return: write state
        """
        return self.write( {'state': 'draft'})

    def delay(self):
        """
        Workflow function changes state to delay .

        @return: write state
        """
        if self._context:
            if 'owner' in self._context and 'model_id' in self._context:
                owner = self._context['owner']
                owner = int(owner)
                model_id = self._context['model_id']
                if str(model_id) == 'fleet.vehicle.log.contract':
                    model_obj = self.env['model_id']
                    model = model_obj.search([('id','=',owner)])

                    model.write({'state': 'wait', 'note': 'تأجيل لأسباب إداربة'})
        return self.write({'state': 'delaied'})


    def print_report(self, data):

        self.ensure_one()
       
        datas = {
            'model': 'payment.enrich.lines',
            'id':self.id
        }
        return self.env.ref('enrich.enrich_report').report_action(self, data=datas)
    

    def num2words(self, cost):
       costs = num2words(cost, lang='ar')
       return costs
