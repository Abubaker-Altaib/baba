# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
# from odoo import fields, osv, orm
from odoo import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import re

###########################################################
#                       #Portfolios#
###########################################################

class finance_portfolio(models.Model):
    _name = 'finance.portfolio'

    name = fields.Char(required=True, string="Portfolio Name")
    active = fields.Boolean(default=True)
    funded_party = fields.Many2one('res.partner', required=True, string="Funded Party", ondelete='restrict')
    portfolio_amount = fields.Float(required=True, string="Portfolio Amount")
    portfolio_month_period = fields.Integer(string="Portfolio Month Period", default="", help="Portfulto Month Period")
    portfolio_year_period = fields.Integer(string="Portfolio Year Period", default="", help="Portfulto Year Period")
    formula = fields.Many2many('finance.formula', string="Formulas")
    custom = fields.Float(string="Custom")
    cus_result = fields.Float(compute='_compute_custom', string="Custom Amount", help="convert custom from percentage to real SDG money")
    installment_ids = fields.One2many('account.payment', "portfolio_id", string='Installment',domain=[('payment_type','=','inbound')])
    installment_ids_check = fields.Boolean(string="Calculate Defecation Date")
    start_date = fields.Date(string="First Pay Date", compute='_set_start_date', readonly=True)
    end_date = fields.Date(string="Last Defecation Date",compute='_set_end_date', readonly=True)
    portfolio_format = fields.Selection([ ("modarba_mogayeda" , "Modarba Mogayeda") , ("gared_hason" , "Gared Hason") ], default="modarba_mogayeda", string="Portfolio Format")
    funded_party_ratio = fields.Float(required=True, string="Funded Party ")
    speculation_ratios = fields.Float(required=True, string="Speculation  ")
    others = fields.Float(required=True, string="Others")
    pr_members = fields.Float(compute='_compute_pr_members_ratio', string="Total Ratio",
                              help="Total Ratio of Portfolio Member")
    guarantee_ids = fields.One2many('finance.guarantee.lines', "portfolio_id" , string='Gruntee')
    amount_ids = fields.One2many('finance.portfolio.payment', "portfolio_id" , string='Amounts')
    amount_ids_check = fields.Boolean(string="Calculate Profits")
    real_value = fields.Float(compute="_currentrealmoney", readonly=True, string="Current Net Portfolio")
    # prevents
    company_ids = fields.Many2many('res.company', string="Companies")
    sectors_ids = fields.Many2many('finance.sector', String="Sectors")
    individual = fields.Boolean(string='Individual')
    group = fields.Boolean(string='Group')
    male = fields.Boolean(string='Male')
    female = fields.Boolean(string='Female')
    property_account_payable_id = fields.Many2one('account.account', string="Account Payable", company_dependent=True,
                                                  domain=[('internal_type', '=', 'payable'), ('deprecated', '=', False)])
    property_account_receivable_id = fields.Many2one('account.account', string="Account Receivable", company_dependent=True,
                                                     domain=[('internal_type', '=', 'receivable'), ('deprecated', '=', False)])
    profit_margin_account_id = fields.Many2one('account.account', string="Profit Margin Account", company_dependent=True,
                                                     domain=[('internal_type', '=', 'receivable'), ('deprecated', '=', False)])
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account',company_dependent=True)
    others_partner_id = fields.Many2one('res.partner', string="Others Partner", domain=[('supplier', '=', True)])
    profit_suspend_account_id = fields.Many2one('account.account', string="Profit Suspend Account", company_dependent=True,
                                                domain=[('internal_type', '=', 'payable'), ('deprecated', '=', False)])
    profit_account_id = fields.Many2one('account.account', string="Profit Account",company_dependent=True)
    expected_profit_account_id = fields.Many2one('account.account', string="Expected Profit Account",company_dependent=True)

    @api.constrains("name")
    def check_name(self):
        """
        Check if name Contain White space char
        :return:
        """
        white_space = re.compile(r'^\s')
        if white_space.search(self.name):
            raise exceptions.ValidationError(_("there is blank space in portfolio name check it"))

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('approved_amount'):
            portfolio_ids = [p.id for p in self.search([]) if p.real_value>=self._context.get('approved_amount')]
            args.append(('id', 'in', portfolio_ids))
        return super(finance_portfolio, self).name_search(name=name, args=args, operator=operator, limit=limit)

    @api.multi
    def name_get(self):
        """
        Desc : To display record in view as (Portfolio Name - Real Value)
        :return:
        """
        return [(portfolio.id, '%s - ' % (portfolio.name)) for portfolio in self]

    @api.onchange('funded_party_ratio', 'speculation_ratios', 'others')
    def change_ratio(self):
        if self.portfolio_format == 'gared_hason':
            self.funded_party_ratio = 0
            self.speculation_ratios = 100
            self.others = 0
        if self.others == 0 :
            self.others_partner_id = self.env['res.partner']

    def _get_default_formula_ids(self):
        cr = self.pool.cursor()
        self.env
        return self.pool.get('finance.formula').search(cr, self.env.uid, [])

    @api.one
    @api.depends('installment_ids')
    def _currentrealmoney(self):
        """
        Desc:Calculate net value for portfoluo
        :return:
        """
        installments = 0  # (-)get all installemnt amount in current portfolio
        amounts = 0  # (-)get all amount.name in finance.portfolio.payment for current portfolio
        branchesmoney = 0  # (-)get all amount recieved when branch request amount and Head Accept it
        revivedrequest = 0  # (+)get all amount Head accept
        order_approved_amount = 0  # (-)get Funding Amount in every Approval
        approval_installments = 0  # (+)get  Amount Recived in every Approval installment
        if self.id:
            #calculate just for main company
            if self.env.user.company_id.id == 1:

                installments = sum(record.amount for record in self.installment_ids)

                amounts = sum(record.name for record in self.amount_ids)

                for record in self.env['portfolio.branch.request'].search(
                        [('portfolio_id', '=', self.id), ('state', '=', 'approved')]):
                    if record.portfolio_id.id == self.id:
                        branchesmoney += record.amount_received

                for record in self.env['portfolio.head.request'].search(
                        ['&', ('portfolio', '=', self.id), ('state', '=', 'done')]):
                    revivedrequest += record.amount

            else:
                # calculate for Branch
                for record in self.env['portfolio.branch.request'].search([('portfolio_id', '=', self.id),('state', '=', 'approved'),
                                                                           ('name','=',self.env.user.company_id.id)]):
                    if record.portfolio_id.id == self.id:
                        branchesmoney += record.amount_received*-1

                for record in self.env['portfolio.head.request'].search(
                        ['&', ('portfolio', '=', self.id), ('state', '=', 'done'),('name','=',self.env.user.company_id.id)]):
                    revivedrequest += record.amount*-1

            # get all receive amount from installments connected with order state = approved for specific Portfolio
            # use cr exceute for speed because ORM is soOOOOOo slooooooooow $_$
            self._cr.execute("""
                                       select sum(receive_amount) from finance_installments inst join finance_approval app on inst.approval_id = app.id join finance_visit vis on app.visit_id = vis.id
                                       join finance_order ord on vis.order_id = ord.id
                                       where ord.state = 'approved' and ord.portfolio_id =
                                    """ + str(self.id) +""" and app.company_id = """ +str(self.env.user.company_id.id))

            result = self._cr.fetchall()

            installments_receive_amount = result[0][0] or 0

            self._cr.execute("""
                                           select sum(app.approve_amount) from finance_approval app join finance_visit vis on app.visit_id = vis.id
                                           join finance_order ord on vis.order_id = ord.id
                                           where ord.state = 'approved' and ord.portfolio_id =
                                    """ + str(self.id)+""" and app.company_id = """ +str(self.env.user.company_id.id))

            result = self._cr.fetchall()
            approvals_amount = result[0][0] or 0

            order_approved_amount = approvals_amount
            approval_installments = installments_receive_amount

            self.real_value = (installments - amounts - branchesmoney - order_approved_amount + revivedrequest + approval_installments)*-1

    @api.constrains('funded_party_ratio', 'speculation_ratios' , 'others')
    def _check_ratios_total(self):
        """
        Desc : Verifies the total of ratios not exceed 100%
        :return:
        """
        if ((self.funded_party_ratio + self.speculation_ratios + self.others) != 100):
            raise exceptions.ValidationError(_('Total of Ratios(Funded Party+Speculation+Others ) must be Excatly 100 % .'))

    @api.constrains('custom')
    def _check_custom_ratio(self):
        """
        Desc:Verifies the ocustom not exceed 100%
        :return:
        """
        if ((self.custom) > 100):
            raise exceptions.ValidationError(
                _('custom Ratio must not exceed 100 % .'))

    @api.constrains('funded_party_ratio')
    def _check_funded_party_ratio(self):
        """
        Desc:Verifies the funded_party_ratio notexceed 100%
        :return:
        """
        if ((self.funded_party_ratio) > 100):
            raise exceptions.ValidationError(
                _('Funded Party Ratio must not exceed 100 % .'))

    @api.constrains('speculation_ratios')
    def _check_speculation_ratios(self):
        """
        Desc:Verifies the speculation_ratios notexceed 100%
        :return:
        """
        if ((self.speculation_ratios) > 100):
            raise exceptions.ValidationError(
                _('Speculation Ratio must not exceed 100 % .'))

    @api.constrains('others')
    def _check_others_ratios(self):
        """
        Desc:Verifies the others notexceed 100%
        :return:
        """
        if ((self.others) > 100):
            raise exceptions.ValidationError(
                _('others Ratio must not exceed 100 % .'))

    @api.constrains('installment_ids', 'portfolio_amount')
    def _check_amount_total(self):
        """
        Desc:Verifies the amount_ids(amount) total equal or less then portfolio amount.

        """
        amount_sum = 0
        for amount in self.installment_ids:
            amount_sum += amount.amount
            if (amount_sum > self.portfolio_amount):
                raise exceptions.ValidationError(_('Total of Amounts must not exceed Portfolio Amount .'))

    @api.depends('portfolio_amount', 'custom')
    def _compute_custom(self):
        self.cus_result = (self.custom / 100) * self.portfolio_amount

    @api.depends('funded_party_ratio', 'speculation_ratios', 'others')
    def _compute_pr_members_ratio(self):
        """
        Desc:sum portfolio members ratio
        :return:
        """
        self.pr_members = self.funded_party_ratio + self.speculation_ratios + self.others

    @api.depends('installment_ids')
    def _set_start_date(self):
        """
        Set The First Date for portfolio
        :return:
        """
        if self.installment_ids:
            self.start_date = min([datetime.strptime(date.payment_date, '%Y-%m-%d') for date in self.installment_ids])

    @api.depends('start_date', 'installment_ids_check', 'portfolio_month_period', 'portfolio_year_period')
    def _set_end_date(self):
        """
        Set The End Date for the portfolio
        :return:
        """
        if self.installment_ids:
            months = relativedelta(months=self.portfolio_month_period)
            years = relativedelta(years=self.portfolio_year_period)
            self.end_date = datetime.strptime(self.start_date, "%Y-%m-%d") + months + years

    @api.onchange('portfolio_amount', 'amount_ids', 'amount_ids_check')
    def calculate_profits(self):
        '''
        Desc:Function to calculate profit for in each pay for Funded Party and Speculator
        :return:
        '''
        for paid in self.amount_ids:
            if paid.amount_source == "profit":
                paid.funded_party = paid.name * (self.funded_party_ratio / 100)
                paid.speculater = paid.name * (self.speculation_ratios / 100)
                paid.others = paid.name * (self.others / 100)
            if paid.amount_source == "assets":
                paid.funded_party = paid.name
                paid.speculater = 0
                paid.others = 0


    @api.onchange('portfolio_format')
    def wallet_cond(self):
        '''
        Desc:Function to get first date and lastdate of installmens
        :return:
        '''
        if(self.portfolio_format == "gared_hason"):
            self.funded_party_ratio = 100
            self.speculation_ratios = 0
            self.others = 0
        if(self.portfolio_format == "modarba_mogayeda"):
            self.funded_party_ratio = 0

    # This Model has been replaced by: FinanceAccountPayment
    """
class finance_portfolio_installment(models.Model):
    _name = 'finance.portfolio.installment'

    #name = fields.Char(required=True, string="Installment No.")
    amount=fields.Float(required=True,string="Amount")
    pay_date = fields.Date(required=True,string="Pay Date")
    defecation_date = fields.Date(readonly=True,string="Defecation Date")
    portfolio_id=fields.Many2one('finance.portfolio',ondelete='restrict')
    journal_id = fields.Many2one('account.journal','Bank Journal',domain=[('type', '=', 'bank')],ondelete='restrict')
    state = fields.Selection([('draft', 'Draft'), ('post', 'Post')], default='draft', readonly=True,required=True)

    @api.one
    def action_post(self):
        
        create account.move when post installment
        :return:change state ==> post and create account.move object
        
        self.write({'state' : 'post'})
        
        To-do:
        self.env['account.move'].create()
        """




class finance_portfolio_amounts_paid(models.Model):
    _name = 'finance.portfolio.payment'

    name = fields.Float(required=True, string="Statement(Amount)")
    amount_source = fields.Selection([ ("assets" , "Assets") , ("profit" , "Profit") ], default="assets", string="Amount Source")
    funded_party = fields.Float(string="Funded Party", readonly=True)
    speculater = fields.Float(readonly=True)
    others = fields.Float(readonly=True)
    date = fields.Date(required=True)
    portfolio_id = fields.Many2one('finance.portfolio', ondelete='restrict')
    line_name = fields.Char('Line Name', readonly=True)

    @api.multi
    def execute(self):
        if self.amount_source == 'assets':
            payment = self.env['account.payment'].create({
                'communication': _('Payback portfolio Amount'),
                'payment_date': self.date,
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': self.portfolio_id.funded_party.id,
                'amount': self.name,
                'payment_method_id': '',  # to avoid error in check printing module

            })
            self.line_name = payment.communication

        elif self.amount_source == 'profit':
            if (self.portfolio_id.profit_account_id.id == False):
                raise exceptions.ValidationError(
                    _('You must First Select Profit Account in Micro-Finance Settings'))
            if (self.portfolio_id.profit_suspend_account_id.id == False):
                raise exceptions.ValidationError(_('You must First Select Profit Suspend Account in Portfolio setting'))

            ml = [(0, 0, {
                'name': _('Funded Party Profit'),
                'date': self.date,
                'partner_id': self.portfolio_id.funded_party.id,
                'account_id': self.portfolio_id.profit_suspend_account_id.id,
                'company_id': self.portfolio_id.env.user.company_id.id,
                'debit': 0.0,
                'credit': self.funded_party
            })]

            ml += [(0, 0, {
                'name': _('Others Profit'),
                'date': self.date,
                'partner_id': self.portfolio_id.others_partner_id.id,
                'account_id': self.portfolio_id.profit_suspend_account_id.id,
                'company_id': self.portfolio_id.env.user.company_id.id,
                'debit': 0.0,
                'credit': self.others
            })]

            ml += [(0, 0, {
                'name': _('Collected Profit'),
                'date': self.date,
                'account_id': self.portfolio_id.profit_account_id.id,
                'company_id': self.env.user.company_id.id,
                'debit': self.funded_party + self.others,
                'credit': 0.0
            })]

            # to avoid unblanced journal Exception in (account.move.line) we must sent context (check_move_validity) = False
            # to avoid post_validate check
            move = self.env['account.move'].with_context(check_move_validity=False).create({
                'name':'Portfolio Move',
                'date': self.date,
                'company_id': self.env.user.company_id.id,
                'journal_id': self.env.user.company_id.journal_id.id,
                'line_ids': ml
            })

            self.line_name = move.name


###########################################################
# Prevents Models#
###########################################################


class finance_formula(models.Model):
    _name = 'finance.formula'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")

###########################################################
# Head & Branches Models#
###########################################################

class portfolio_branch_request(models.Model):
    _name = "portfolio.branch.request"
    _inherit = ['mail.thread']

    name = fields.Many2one('res.company', string="Branch", default=lambda self: self.env.user.company_id,
                             readonly=True, ondelete='cascade')
    amount_request = fields.Float(string="Amount Request")
    request_date = fields.Datetime(string="Request Date", default=fields.Datetime.now, readonly=True)
    state = fields.Selection([("draft", "Draft"), ("waiting_approval", "Waiting Approval"), ("approved", "Approved"), ("refused"
                            , "Refused")], default="draft", readonly=True, string="State")
    portfolio_id = fields.Many2one('finance.portfolio', readonly=True, string="Portfolio", ondelete='restrict')
    amount_received = fields.Float(readonly=True, string="Amount Received")
    head_partner_id = fields.Many2one('res.partner', domain="[('company_type','=','company')]")
    description = fields.Text(string="Description")

    @api.multi
    def unlink(self):
        """
        if request not in draft state the request cannot bee deleted
        :return:
        """
        branch_request = self.env['portfolio.branch.request'].search([('id','in',self.ids)])
        for branch in branch_request:
            if branch.name.id != self.env.user.company_id.id:
                raise exceptions.ValidationError(_("You cannot delete this record because it's in  %s branch")% branch.name.name)
            elif branch.name.id == self.env.user.company_id.id and branch.state != 'draft':
                raise exceptions.ValidationError(_("You cannot delete this record because it's in %s state") % dict(branch.fields_get(allfields=['state'])['state']['selection'])[branch.state])
            elif branch.state == 'draft':
                return super(portfolio_branch_request, self).unlink()


    @api.constrains('amount_request')
    def check_amount(self):
        if self.amount_request <= 0:
            raise exceptions.ValidationError(_("amount must be more than zero"))

    @api.one
    def send_request(self):
        """
        Desc:save record and send it to head to accept it or refuse it
        :return:
        """
        self.env['portfolio.head.recieve'].create({'requests': self.id, })
        self.write({'state':'waiting_approval'})

    @api.multi
    def in_approved(self):
        """
        Create Account Payment
        :return:
        """
        if self.state in 'approved':
            self.env['account.payment'].create({
                'payment_date': fields.Date.today(),
                'partner_id': self.head_partner_id.id,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'amount': self.amount_received,
                'payment_method_id': '',
                'communication': _("Supplying Branch Portfolio from " + self.portfolio_id.name)
            })


class portfolio_head_recieve(models.Model):
    _name = "portfolio.head.recieve"
    _rec_name = "requests"
    _inherit = ['mail.thread']

    requests = fields.Many2one('portfolio.branch.request', domain=[('state', '=', 'waiting_approval')], required=True,
                             readonly=True, string="Request From", ondelete='restrict')
    amount_requested = fields.Float(compute='_compute_requested_amount', string="Amount Requested", track_visibility='onchange')
    portfolio_id = fields.Many2one('finance.portfolio', string="Portfolio",track_visibility='onchange')
    portfolio_amount = fields.Float(compute='_compute_p_amount', readonly=True, string="Portfolio Amount",track_visibility='onchange')
    portfolio_give = fields.Float(string="Portfolio Give",track_visibility='onchange')
    state = fields.Selection([('waiting_approval', 'Waiting Approval'),
                               ('op_recommend', 'Operation Manager Recommend'),
                               ('gm_recommend', 'General Manager Recommend'),
                               ('ac_approval', 'Waiting for Accounting Approval'),
                               ('approved', 'Approved'), ('refused', 'Refused')],
                              default='waiting_approval', readonly=True, string="State",track_visibility='onchange')
    status = fields.Selection([('gm_recommend', 'gm_recommend'), ('op_recommend', 'op_recommend'), ('ac_approval', 'ac_approval')], compute='get_status')
    company_portfolio_amount = fields.Float(compute='_compute_cmp_portf_amount', readonly=True,
                                            string="Branch Portfolio Balance")
    payment_ids = fields.Many2one('account.payment')
    description = fields.Text(string="Description")

    @api.multi
    def unlink(self):
        """
        :raise custom error when delete a record
        """
        raise exceptions.ValidationError(_("you cannot delete this record"))

    @api.multi
    def act_op_recommend(self):
        return self.write({'state': 'op_recommend'})

    @api.multi
    def act_gm_recommend(self):
        return self.write({'state': 'gm_recommend'})

    @api.constrains('portfolio_id', 'portfolio_give')
    def check_portfolio(self):
        if (self.portfolio_id == False or self.portfolio_give == False):
            raise exceptions.ValidationError(_('You cant Accept Request Without Select Portfolio'))

    @api.one
    def act_ac_approval(self):
        if self.portfolio_give <= 0:
            raise exceptions.ValidationError(_("amount must be more than zero"))
        self.write({'state': 'approved'})
        self.requests.head_partner_id = self.env.user.company_id.partner_id
        self.payment_ids = self.env['account.payment'].create({
            'payment_date': fields.Date.today(),
            'partner_id': self.requests.name.partner_id.id,  # self.requests.head_partner_id.id,
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'amount': self.portfolio_give,
            'payment_method_id': '',
            'communication': _("Supplying Branch Portfolio")
        })

        # To call function in branche request to create account.payment
        self.requests.in_approved()
        self.write({'state': 'ac_approval'})


    #company_ids
    @api.depends('state', 'portfolio_id.company_ids')
    def get_status(self):
        approved_amount = self.portfolio_give
        if self.state == 'waiting_approval':
            self.status = approved_amount > self.env.user.company_id.por_op_ceiling and 'op_recommend' or 'ac_approval'
        elif self.state == 'op_recommend':
            self.status = approved_amount > self.env.user.company_id.por_gm_ceiling and 'gm_recommend' or 'ac_approval'
        elif self.state == 'gm_recommend':
            self.status = 'ac_approval'


    @api.depends('portfolio_id', 'requests')
    def _compute_cmp_portf_amount(self):
        """
        Desc:show current branch money for spicific portfolio
        :return:
        """
        sum = 0
        for portf in self.env['portfolio.branch.request']. \
                search(['&', ('portfolio_id', '=', self.portfolio_id.id),
                        ('state', '=', 'approved'), ('name', '=', self.requests.name.id)]):
            sum += portf.amount_received

        for portf in self.env['portfolio.head.request']. \
                search(['&', ('portfolio', '=', self.portfolio_id.id),
                        ('state', '=', 'done'), ('name', '=', self.requests.name.id)]):
            sum -= portf.amount

        self.company_portfolio_amount = sum

    @api.one
    def refuse(self):
        """
        Desc : request refused so change state
        :return:
        """
        self.write({'state': 'refused'})
        self.requests.write({'state': 'refused'})

    @api.constrains('portfolio_give')
    def _check_portfolio_give(self):
        """
        Desc : Verifies the portfolio_give not exceed portfolio current Money
        :return:
        """
        if (self.portfolio_give > self.portfolio_amount):
            raise exceptions.ValidationError(
                _('You Cant Give Branch Money More Than Portfolio Current Money .'))

    @api.depends('requests')
    def _compute_requested_amount(self):
        """
        Desc : get amount of sent request
        :return:
        """
        self.amount_requested = self.requests.amount_request


    @api.depends('portfolio_id')
    def _compute_p_amount(self):
        """
        Desc:get net money of portfolio
        :return:
        """
        self.portfolio_amount = self.portfolio_id.real_value


###########################################################
# Head Requests Models#
###########################################################

class portfolio_head_request(models.Model):
    _name = "portfolio.head.request"
    _inherit = ['mail.thread']


    name = fields.Many2one('res.company', string="Branch",
                             readonly=False, required=True, ondelete='cascade')
    company_portfolio_amount = fields.Float(compute='_compute_cmp_portf_amount', readonly=True, string="Branch Portfolio Balance")
    portfolio = fields.Many2one('finance.portfolio', string="Portfolio", required=True, ondelete='restrict')
    portfolio_amount = fields.Float(compute='_compute_p_amount', readonly=True, string="Portfolio Amount")
    amount_source = fields.Selection([("assets", "Assets"), ("profit", "Profit")], default="assets", string="Amount Source")
    amount = fields.Float(string="Amount", required=True)
    state = fields.Selection([("draft", "Draft"), ("waiting_approval", "Waiting Approval"), ("done", "Done")],
                             default="draft", readonly=True)
    @api.multi
    def unlink(self):
        """
        :raise custom error when remove request in done state or waiting state
        """
        for state in self.search([('id', 'in', self.ids)]):
            if state.state in ['waiting_approval', 'done']:
                raise exceptions.ValidationError(_("you cannot delete request when it in %s state" % state.state))
            elif self.state == 'draft':
                return super(portfolio_head_request, self).unlink()

    @api.constrains('amount')
    def check_amount(self):
        if self.amount <= 0:
            raise exceptions.ValidationError(_("amount must be more than zero"))


    @api.one
    def accept(self):
        """
        Desc:save record and send it to bransh to accept it and change state
        :return:
        """
        self.env['portfolio.branch.receive'].create({'name':self.id, 'amount_source' : self.amount_source,
                                                     'amount':self.amount, 'state' : 'waiting_approval',
                                                     'head_partner_id' :  self.env.user.company_id.partner_id.id})
        self.write({'state':'waiting_approval'})


    @api.constrains('amount')
    def _check_amount_company(self):
        """
        Desc : varify amount wanted by branch not exceed current money in branch for spicific portfolio
        :return:
        """
        if(self.amount > self.company_portfolio_amount):
            raise exceptions.ValidationError(
                _('You cant make Request to Branch with amount more than amount in Branch Portfolio'))

    @api.depends('portfolio', 'name')
    def _compute_cmp_portf_amount(self):
        """
        Desc:computo branch money for specific portfolio
        :return:
        """
        sum = 0
        for portf in self.env['portfolio.branch.request']. \
                search(['&', ('portfolio_id', '=', self.portfolio.id),
                        ('state', '=', 'approved'), ('name', '=', self.name.id)]):
            sum += portf.amount_received

        for portf in self.env['portfolio.head.request']. \
                search(['&', ('portfolio', '=', self.portfolio.id),
                        ('state', '=', 'done'), ('name', '=', self.name.id)]):
            sum -= portf.amount

        self.company_portfolio_amount = sum

    @api.multi
    @api.onchange('portfolio')
    def _get_portfolio_company(self):
        """
        Desc:Return Dynamic domain to just select branch that use selected Portfolio
        :return:
        """
        company_ids = []
        for portf in self.env['portfolio.branch.request'].\
                search(['&', ('portfolio_id', '=', self.portfolio.id),
                        ('state', '=', 'approved')]):
            if portf.name.id != self.env.user.company_id.id:
                company_ids.append(portf.name.id)
        # to return dynamic domain
        return {'domain': {'name': [('id', '=', company_ids)]}}

    @api.depends('portfolio')
    def _compute_p_amount(self):
        """
        Desc : get portfolio net money
        :return:
        """
        self.portfolio_amount = self.portfolio.real_value



class portfolio_branch_receive(models.Model):
    _name = "portfolio.branch.receive"
    _inherit = ['mail.thread']
    # need rule to show only request record to spicific branch only
    name = fields.Many2one('portfolio.head.request', string="Request", readonly=True, ondelete='restrict')
    amount_source = fields.Selection([("assets", "Assets"), ("profit", "Profit"), ["cash", "Cash"]], compute='set_p_type', string="Source")
    amount = fields.Float(compute='set_p_amount', string="Amount")
    state = fields.Selection([("waiting_approval", "Waiting Approval"), ("done", "Done")], readonly=True, string="Request State")
    head_partner_id = fields.Many2one('res.partner', domain="[('company_type','=','company')]")


    @api.depends('name')
    def set_p_type(self):
        """
        Desc:get what branch need (assets or profit)
        :return:
        """
        self.amount_source = self.name.amount_source

    @api.depends('name')
    def set_p_amount(self):
        """
        Desc : get request amount
        :return:
        """
        self.amount = self.name.amount

    @api.one
    def accept(self):
       """
       Desc : Accept request from branch and change state
       and make account payment
       :return:
       """
       self.write({'state':'done'})

       self.env['account.payment'].create({
           'payment_date': fields.Date.today(),
           'partner_id': self.head_partner_id.id,
           'payment_type': 'outbound',
           'partner_type': 'supplier',
           'amount': self.amount,
           'payment_method_id': '',
           'communication': _("Transfer " + self.name.portfolio.name + " Portfolio "
                              + self.amount_source + " to Head Quarter")
       })

       self.name.write({'state':'done'})
       self.env['account.payment'].create({
           'payment_date': fields.Date.today(),
           'partner_id': self.head_partner_id.id,
           'payment_type': 'inbound',
           'partner_type': 'customer',
           'amount': self.amount,
           'payment_method_id':'',
           'communication': _(self.name.portfolio.name + " Portfolio "
                              + self.amount_source + " Transfer from " + self.name.name.name)
       })

class AccountPaymentCustom(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):
        """
        Add head recive state to change it to approve when post is called
        :return:
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)
            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()
            rec.write({'state': 'posted', 'move_name': move.name})
        head_recive = self.env['portfolio.head.recieve'].search([('payment_ids', '=', self.id)])
        if head_recive:
            head_recive.write({'state': 'approved'})
            head_recive.requests.write(
                {'state': 'approved', 'portfolio_id': head_recive.portfolio_id.id, 'amount_received': head_recive.portfolio_give})



