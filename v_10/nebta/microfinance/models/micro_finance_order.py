# coding: utf-8
import sys


from odoo import api, models, fields, exceptions, _
import re


class finance_order(models.Model):
    _name = "finance.order"
    _description = "Finance Order"
    _order = "create_date desc"
    _inherit = ['mail.thread']

    @api.one
    @api.depends('formula')
    def _formula_forbidden(self):
        """
        Desc : select same formula id in finance.formula based on current order formula
          to help in Formula forbidden domain.
        """
        if self.formula == 'fixed_murabaha':
            self.formula_forbidden = 1
        elif self.formula == 'dec_murabaha':
            self.formula_forbidden = 2
        elif self.formula == 'salam':
            self.formula_forbidden = 3
        elif self.formula == 'ejara':
            self.formula_forbidden = 4
        elif self.formula == 'gard_hassan':
            self.formula_forbidden = 5
        elif self.formula == 'estisnaa':
            self.formula_forbidden = 6
        elif self.formula == 'mugawla':
            self.formula_forbidden = 7
        elif self.formula == 'mudarba':
            self.formula_forbidden = 8
        elif self.formula == 'musharka':
            self.formula_forbidden = 9
        elif self.formula == 'muzaraa':
            self.formula_forbidden = 10
        else:
            self.formula_forbidden = 0

    #name = fields.Char(string="Order Number", required=True, copy=False, readonly=True, default='/')
    name = fields.Char(string="Order Number", required=True, readonly=True, default='/')
    date = fields.Date(string='Date', index=True, default=fields.Datetime.now(), required=True)
    user_id = fields.Many2one('res.users', string="Officer", default=lambda self: self.env.user, readonly=True, required=True,ondelete='restrict')#restrict
    partner_id = fields.Many2one('res.partner', string='Customer',ondelete='restrict', required=True)

    company_id = fields.Many2one('res.company', string="Branch", default=lambda self: self.env.user.company_id, readonly=True, required=True,ondelete='restrict')#restrict
    company_currency_id = fields.Many2one('res.currency', string="Company Currency", default=lambda self: self.env.user.company_id.currency_id, help='Utility field to express amount currency')
    project_name = fields.Char(string='Project Name', size=256, required=True)
    project_status = fields.Selection([('new', 'New'), ('exist', 'Exist'), ('stopped', 'Stopped')], string='Project Status', required=True)
    project_address = fields.Text(string='Project Address', required=True)
    state_id = fields.Many2one("res.country.state", string='State', domain=[('parent_id','=',False)], ondelete='restrict', required=True)
    local_state_id = fields.Many2one("res.country.state", string='Local State', ondelete='restrict', required=True)
    zone_id = fields.Many2one("res.country.state", string='Zone', ondelete='restrict', required=True)
    sector_id = fields.Many2one('finance.sector', string='Sector', ondelete='restrict', required=True)
    amount = fields.Monetary(string='Amount', currency_field='company_currency_id', required=True)
    formula = fields.Selection([('fixed_murabaha','Fixed Murabaha'), ('dec_murabaha','Decremental Murabaha'), 
                                ('salam', 'Salam'), ('ejara','Ejara'), ('gard_hassan','Gard Hassan'),
                                ('estisnaa','Estisnaa'), ('mugawla','Mugawla'), ('mudarba','Mudarba'),
                                ('musharka','Musharka'), ('muzaraa','Muzaraa') ], string='Formula', required=True)
    formula_clone = fields.Selection([('murabaha', 'Murabaha'), ('buying_murabaha', 'Buying Murabaha'),
                                      ('salam', 'Salam'), ('ejara', 'Ejara'), ('gard_hassan', 'Gard Hassan'),
                                      ('estisnaa', 'Estisnaa'), ('mugawla', 'Mugawla'), ('mudarba', 'Mudarba'),
                                      ('musharka', 'Musharka'), ('muzaraa', 'Muzaraa')], string='Formula',
                                     required=True)
    murabaha_selection = fields.Selection(
        [('fixed_murabaha', 'Fixed Murabaha'), ('dec_murabaha', 'Decrmental Murabaha'), ], string='Murabaha Type')
    installments_number = fields.Integer(string='Installments Number', required=True)
    payment_method_ids = fields.Many2one('finance.payment.method', string='Payment Method', ondelete='restrict')
    funding_period = fields.Integer(string='Funding Period', store=True, compute='get_funding_period')
    funding_period_day = fields.Integer(string="Day", store=True, compute='_get_funding_period')
    state = fields.Selection([('draft', 'Draft'), ('waiting_visit', 'Waiting for Visit'), ('visit_complete', 'Visit Completed'),
                              ('su_recommend', 'Supervisor Recommend'), ('br_recommend', 'Branch Manager Recommend'), 
                              ('op_recommend', 'Operation Manager Recommend'),('approved', 'Approved'), ('cancel', 'Canceled')], 
                              copy=False, default="draft", readonly=True, required=True, track_visibility='onchange')
    note = fields.Text(string="Description")
    visit_id = fields.Many2one('finance.visit', string='Visit', readonly=True)
    crop_id = fields.Many2one('finance.crop', string="Crop", ondelete='restrict')
    uom = fields.Many2one(related='crop_id.uom_id', string='Unit of Measure')
    description = fields.Text(string="Description")
    type = fields.Selection([('individual','Individual'),('group','Group')])
    approve_ids=fields.One2many('finance.approval',related='visit_id.approve_ids')
    approved_amount = fields.Float(string="Total Approval Amount",compute="_sum_approved_amounts")
    portfolio_id=fields.Many2one('finance.portfolio',string="Portfolio")
    status = fields.Selection([('br_recommend', 'br_recommend'), ('op_recommend', 'op_recommend'),('approved','approved')], compute='get_status')
    formula_forbidden = fields.Integer('Formula Forbidden ID', compute="_formula_forbidden")
    guarantee_line_ids = fields.One2many('finance.guarantee.lines', 'finance_order_id', string='Guarantee Value', required=True)
    
    first_due_date = fields.Date(compute="compute_due_dates",store=True)
    last_due_date = fields.Date(compute="compute_due_dates",store=True)

    @api.one
    @api.depends('approve_ids.installment_ids')
    def compute_due_dates(self):
        installment = self.approve_ids.installment_ids
        if installment:
            self.first_due_date = installment[0].due_date
            self.last_due_date = installment[len(installment)-1].due_date

    @api.multi
    def unlink(self):
        for states in self.search([('id', 'in', self.ids)]):
            if states.state !='draft':
                raise exceptions.ValidationError(_("You cannot delete order in %s state" % states.state))
            elif states.state == 'draft':
                return super(finance_order, self).unlink()

    @api.constrains('project_name')
    def check_project_name(self):
        """
        To prevent name from accepting white space
        :return:
        """
        white_space = re.compile(r'^\s')
        if white_space.search(self.project_name):
            raise exceptions.ValidationError(_("cannot accept blank space you must enter real data..!!"))

    @api.constrains('installments_number', 'amount')
    def check_fields_value(self):
        """
        To prevent zero value in numeric fields
        :return:
        """

        if self.installments_number <= 0 and self.formula not in ['salam', 'mudarba', 'muzaraa', 'musharka']:
            raise exceptions.ValidationError(_("installment cannot be zero or less"))
        if self.amount <= 0:
            raise exceptions.ValidationError(_("amount must be more than zero"))

    @api.constrains('partner_id')
    def check_order_state(self):
        """
        make sure the customer not allowed to request
        new order until he finish his installments
        :return:
        """
        count = 0
        for order in self.env['finance.order'].search([('partner_id','=',self.partner_id.id)]):
            count+=1
            if(count == 2):
                if order.state != 'approved' and order.state != 'cancel':
                    raise exceptions.ValidationError(_("Customer Have Another Order not completed"))
                for approval in order.approve_ids:
                    if approval.state != 'done':
                        raise exceptions.ValidationError(_("Customer Have Installments Not Paid"))


    #By Arwa: doesn't work! can use fields_view_get() or name_search() in portfolio
    '''
    @api.multi
    @api.onchange('amount')
    def _domain_portfolio_id(self):
        """
        Desc : Func to display only portfolio that have balance equal or more than visit amount
        :return:
        """
        ids = []
        for portfolio in self.env['finance.portfolio'].search([('id','>',0)]):
            if portfolio.real_value >= self.amount:
                ids.append(portfolio.id)
        return {'domain': {'portfolio_id': [('id', 'in', ids)]}}
    '''

    @api.one
    @api.depends('approve_ids')
    def _sum_approved_amounts(self):
        """
        Compute the total amounts of approve records.
        """
        self.approved_amount = sum([lines.approve_amount for lines in self.approve_ids])

    @api.depends('state','approve_ids.approve_amount')
    def get_status(self):
        approved_amount = sum([lines.approve_amount for lines in self.approve_ids])
        if self.state == 'su_recommend':
            self.status = approved_amount > self.company_id.br_ceiling and 'br_recommend' or 'approved'
        elif self.state == 'br_recommend':
            self.status = approved_amount > self.company_id.op_ceiling and 'op_recommend' or 'approved'
        elif self.state == 'op_recommend':
            self.status = 'approved'

    @api.one
    @api.depends('payment_method_ids.number_of_days', 'installments_number')
    def get_funding_period(self):
        self.funding_period,self.funding_period_day = divmod((self.payment_method_ids.number_of_days * self.installments_number), 30)

    @api.multi
    def act_visit_confirm(self,order_name):
        """
        Create visit Record with necessary Data
        :return: Change state
        """
        self.visit_id = self.env['finance.visit'].create({'order_id':self.id})
        self.name = str(self.type) + " " + str(order_name)
        self.visit_id.name = str(order_name) + " " + str(self.visit_id.date)
        return self.write({'state': 'waiting_visit'})

    @api.multi
    def act_su_recommend(self):
        return self.write({'state': 'su_recommend'})

    @api.multi
    def act_br_recommend(self):
        return self.write({'state': 'br_recommend'})

    @api.multi
    def act_op_recommend(self):
        return self.write({'state': 'op_recommend'})

    @api.multi
    def act_approved(self,all_members_number):
        celling = 0
        for lines in self.approve_ids:
            # calculate celling (project celling * group members number)
            celling = lines.project_id.celling * all_members_number
            if (lines.approve_amount > celling ):
                raise exceptions.ValidationError(_(
                    "Cannot be approved due to approvals not approved because approval amount more than celling amount in %s" % lines.project_id.name))
            else :
                lines.action_recommend_approved()
        return self.write({'state': 'approved'})

    @api.multi
    def act_re_visit(self):
        self.visit_id.state = 'draft'
        self.visit_id.approve_ids.unlink()
        return self.write({'state': 'waiting_visit'})

    @api.multi
    def act_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def act_approve_cancel(self):
        """
        Cancel Order After approval and check if there no payment to cancel order
         and set state to cancel in order and approval
        :return:
        """
        all_state_in_approve = 0
        for approve_id in self.approve_ids:
            if not approve_id.payment_ids:
                if not approve_id.state == 'approved':
                    all_state_in_approve += 1
                    break
                elif all_state_in_approve == 0:
                    approve_id.write({'state': 'canceled'})
            elif approve_id.payment_ids:
                raise exceptions.UserError(_("you Cannot Cancel order that have payment !!!"))
        return self.write({'state': 'cancel'})

    @api.constrains('guarantee_line_ids')
    def _check_guarantee(self):
        """
        Desc : Check have at least one guarantee
        :return:
        """
        if len(self.guarantee_line_ids) == 0:
            raise exceptions.ValidationError(_('Must have Guarantee .'))


class finance_guarantee_lines(models.Model):
    _name = 'finance.guarantee.lines'
    _rec_name = 'guarantee_type'

    guarantee_type = fields.Many2one('finance.guarantee.type', string='Guarantee Type', required=True)
    document_number = fields.Char(string='Document Number/Description', size=256, required=True)
    guarantee_value = fields.Integer(string='Guarantee Value', required=True)
    finance_order_id = fields.Many2one('finance.order', 'Finance Order', index=True, ondelete='cascade')
    portfolio_id = fields.Many2one('finance.portfolio', ondelete='restrict')








