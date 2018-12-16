# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import ValidationError

class AccountAccountType(models.Model):

    _inherit = "account.account.type"

    active = fields.Boolean(default=True, help="Set active to false to hide the Account Type without removing it.")
    nature = fields.Selection([("debit","Debit"),("credit","Credit")],"Nature",)
   


class AccountJournal(models.Model):
    _inherit = "account.journal"

    #type = fields.Selection(selection_add=[('pl_close','Profit and loss close')])
    depit_account_balance = fields.Float(string="Balance",compute="_calc_depit_account_balance")
    journal_balance = fields.Float(string="Balance",compute="_compute_journal_balance")

    @api.constrains('default_debit_account_id','default_credit_account_id', 'type')
    def _check_default_accounts(self):
        if self.type == 'bank' and self.default_debit_account_id != self.default_credit_account_id :
            raise UserError(_("Default Debit Account and Default Credit Account must be the same "))

    @api.one
    def _compute_journal_balance(self):
        """
        Function compute journal balance
        :return:
        """
        self.journal_balance = 0.0
        account_id = self.default_debit_account_id and self.default_debit_account_id or self.default_credit_account_id
        if self.type == 'bank' and account_id:
            self._cr.execute("""select sum(credit), sum(debit) ,(sum(debit - credit))
                                    from account_move_line
                                    where account_id=%s""", (self.default_debit_account_id.id,))
            sum = self._cr.fetchone()
            self.journal_balance = sum[2]
    

class resPartner(models.Model):
    _inherit = 'res.partner'
    
    code = fields.Char(string="code")
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable", oldname="property_account_payable",
        domain=[],
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable", oldname="property_account_receivable",
        domain=[],
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True)
    
    _sql_constraints = [
        ('code_name_uniq', 'unique (code,name,company_id)', 'The code,name must be unique per company !')
    ]

    @api.constrains('email')
    def _validate_email(self):
        for partner in self:
            if partner.email and not tools.single_email_re.match(partner.email):
                raise Warning(_("Please enter a valid email address."))
        return True

    @api.constrains('phone')
    def _validate_phone(self):
        for rec in self:
            if rec.phone and not rec.phone.isdigit() :
                raise Warning(_("phone should contain numbers only .")) 
            if rec.phone and len(rec.phone) > 25 :
                raise Warning(_("The phone number you entered should be less than 25 number ."))

    @api.constrains('mobile')
    def _validate_phone(self):
        for rec in self:
            if rec.mobile and not rec.mobile.isdigit() :
                raise Warning(_("mobile should contain numbers only .")) 
            if rec.mobile and len(rec.mobile) > 25 :
                raise Warning(_("The mobile number you entered should be less than 25 number ."))                          


class AccountTax(models.Model):
    _inherit ='account.tax'

    code = fields.Char(string ="Code")
    date =fields.Date(string ="Date")
    type_tax_use  = fields.Selection([("purchase","Out"),("sale","In")],"Tax Scope" ,required=True)
    
    _sql_constraints = [
        ('code_uniq', 'unique(code,company_id)', 'The code must be unique per company !')
    ]

    @api.multi
    @api.constrains('amount')
    def _not_equel_zero(self):
        for record in self:
            if record.amount_type:
                if record.amount_type != 'group' and record.amount == 0:
                    raise Warning(_("The amount can not be zero!"))
                    
    @api.multi
    def unlink(self):
        parameter_obj = self.env['ir.config_parameter']
        sale_tax=parameter_obj.search([('key','=','account.default_sale_tax_id'),('value','=',self.id)])
        purchase_tax=parameter_obj.search([('key','=','account.default_purchase_tax_id'),('value','=',self.id)])
        if sale_tax or purchase_tax:
            raise ValidationError(_("can't delete this record, Because it is referred to in Default Taxes!"))
        return super(AccountTax, self).unlink()

class AccountAccount(models.Model):
    _inherit = 'account.account'

    active = fields.Boolean(default=True, help="Set active to false to hide the Account without removing it.")
    nature = fields.Selection([("debit","Debit"),("credit","Credit")],"Nature",related='user_type_id.nature', store=True)

    @api.model
    def name_search(self, name, args ,  operator='ilike', limit=100):
        context = self._context
        if 'model' in context and context['model'] == 'res.partner':
            if 'field' in context and context['field'] =='receivable' :  
                domain = [('internal_type','=','receivable'),('deprecated','=',False)]
                if context['customer'] and context['supplier'] :
                    domain = [('internal_type','in',['receivable','payable']),('deprecated','=',False)]
                   
            if 'field' in context and context['field'] =='payable' :
                domain = [('internal_type','=','payable'),('deprecated','=',False)]
                if context['customer'] and context['supplier'] :
                    domain = [('internal_type','in',['receivable','payable']) ,('deprecated','=',False)]        
                
            records_ids = [record.id for record in self.env['account.account'].search(domain)]
          
            if records_ids:
                args.append(('id','in',records_ids))

        return super(AccountAccount, self).name_search(name, args, operator, limit)

    @api.multi
    @api.constrains('code', 'name')
    def _check_name_code(self):
        for account in self:
            if account.move_line_ids:
                raise ValidationError(_('You cannot edit name or code of account that have journal entries.'))

    @api.multi
    @api.constrains('internal_type', 'reconcile')
    def _check_reconcile(self):
        for account in self:
            if account.internal_type in ('receivable', 'payable') and account.reconcile == False:
                raise ValidationError(_('ValidateError:\nYou cannot have a receivable/payable account that is not reconciliable. (account code: %s)') % account.code)



class account_move_line(models.Model):
    _inherit ='account.move.line'


    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account' ,domain="[('type', '=', 'normal')]")


    @api.multi
    @api.constrains('account_id')
    def _check_account_balance(self):
        for record in self:
            if record.account_id.internal_type == 'liquidity' and record.account_id.balance < 0 :
                raise Warning(_('The balance of liquidity account should not be less than zero !!!!! \n -account:%s \n-balance:%s')%(record.account_id.name,record.account_id.balance))
            
            if record.account_id.nature =='debit' and record.account_id.balance < 0 :
                raise Warning(_("The balance of debit account should not be less than zero !!!!!  \n -account:%s \n-balance:%s ")%(record.account_id.name,record.account_id.balance))

            elif record.account_id.nature =='credit' and record.account_id.balance > 0 :
                raise Warning(_("The balance of credit account should not be more than zero  !!!!!  \n -account:%s \n-balance:%s ")%(record.account_id.name,record.account_id.balance))


    @api.multi
    @api.constrains('period_id')
    def _not_close_period(self):
        for line in self:
            if line.period_id and line.period_id.state=='done':
                raise Warning(_("Can not create move in close period!"))


class AccountAnalyticAccount(models.Model):
    """
    Inherit analytic object to add selection field type which options (view, normal)
    """

    _inherit = "account.analytic.account"

    type = fields.Selection([("view","View"),("normal","Normal")],"Type" ,required=True, default='normal')
    parent_id = fields.Many2one('account.analytic.account',string='Parent',required=False)
    child_ids = fields.One2many('account.analytic.account', 'parent_id',string= 'childs')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code, name'
    _order = 'parent_left'
    
    _sql_constraints = [
        ('name_company_uniq', 'unique(name,type,company_id)', 'The name must be unique per  company!'),
        ('code_company_uniq', 'unique(code,type,company_id)', 'The code must be unique per  company!'),
    ]

    @api.onchange('child_ids')
    def onchange_child_ids(self):
        childs_user_ids = [(4,[child_ids.user_id])]               
            
    @api.multi
    def _compute_debit_credit_balance(self):
        analytic_line_obj = self.env['account.analytic.line']
        for account in self:
            sub_accounts = self.with_context({'show_parent_account': True}).search([('id', 'child_of', [account.id])])
            credit = 0.0
            debit = 0.0
            domain = [('account_id', 'in', sub_accounts.ids)]
            if self._context.get('from_date', False):
                domain.append(('date', '>=', self._context['from_date']))
            if self._context.get('to_date', False):
                domain.append(('date', '<=', self._context['to_date']))
            for aal in analytic_line_obj.search(domain):
                if aal.amount < 0.0:
                    debit += aal.amount
                else:
                    credit += aal.amount
            account.credit = credit
            account.debit = abs(debit)
            account.balance = account.credit - account.debit
            
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if not context.get('show_parent_analytic_account',False):
            args += [('type', '!=', 'view')]
        return super(AccountAnalyticAccount, self).search(args, offset, limit, order, count=count)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    account_analytic_id = fields.Many2one('account.analytic.account',
    string='Analytic Account')

class account_analytic_tag(models.Model):
    _inherit = 'account.analytic.tag'
    
     
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Analytic Tag Name must be unique!')
    ]


class account_fiscal_position(models.Model):
    _inherit = 'account.fiscal.position'
    
     
    _sql_constraints = [
        ('fiscal_name_uniq', 'unique (name)', 'Fiscal Position name must be unique!')
    ]
    
class accountPayment(models.Model):
    _inherit = 'account.payment'

    account_id = fields.Many2one('account.account')



class AccountPaymentTerm(models.Model):
    _inherit ='account.payment.term'

    @api.multi
    def unlink(self):

        for payment_term in self:
            invoices=self.env['account.invoice'].search([('payment_term_id','=', payment_term.id)])
            if invoices :
               raise ValidationError(_("can't delete (%s), there is operation uses this payment term")%payment_term.name)
        return super(AccountPaymentTerm, self).unlink()


class currency(models.Model):
    _inherit ='res.currency'

    # @api.constrains('name')
    # def check_currency_name(self):
    #     if not all(x.isalpha() or x.isspace() for x in self.name):
    #         raise UserError(_("currency name must not contains numbers or symbols"))


    @api.constrains('symbol')
    def check_currency_symbol(self):
        if bool(re.search(r'\d', self.symbol)) :
            raise UserError(_("currency symbol must not contains numbers"))        
            

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    credit = fields.Monetary('Credit', required=True,compute='_compute_debit_credit')
    debit = fields.Monetary('Debit', required=True,compute='_compute_debit_credit')
    
    @api.one
    @api.depends('move_id')
    def _compute_debit_credit(self):
        if self.move_id:
            self.debit=self.move_id.debit
            self.credit=self.move_id.credit


class AccountMoveCustom(models.Model):
    _inherit = 'account.move'

    payment_id = fields.Many2one('account.payment', string="Payment")
    invoice_id = fields.Many2one('account.invoice', string='Invoice')

