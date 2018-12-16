# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, exceptions, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import *
from datetime import datetime, timedelta
from odoo.tools import amount_to_text_en, float_round
from odoo.addons.account_check_printing_custom.models import amount_to_text_ar

            ###############################
            #         Extra Order         #
            ###############################

class finance_extra_order(models.Model):
    _name = 'finance.extra.order'

    order_id = fields.Many2one('finance.order', string="Order Ref", domain=[('state', '=', 'approved')],required=1)
    name = fields.Char(string="Extra order")
    user_id = fields.Many2one('res.users', string="Officer", related="order_id.user_id", readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', related="order_id.partner_id", readonly=True)
    visit_id = fields.Many2one('finance.visit', string="Visit", related="order_id.visit_id", readonly=True)
    company_id = fields.Many2one('res.company', string="Branch", related="order_id.company_id", readonly=True)
    formula = fields.Selection([('fixed_murabaha', 'Fixed Murabaha'), ('dec_murabaha', 'Decremental Murabaha'),
                                ('salam', 'Salam'), ('ejara', 'Ejara'), ('gard_hassan', 'Gard Hassan'),
                                ('estisnaa', 'Estisnaa'), ('mugawla', 'Mugawla'), ('mudarba', 'Mudarba'),
                                ('musharka', 'Musharka'), ('muzaraa', 'Muzaraa')], string='Formula',
                               related="order_id.formula", readonly=True)
    formula_clone = fields.Selection([('murabaha', 'Murabaha'), ('buying_murabaha', 'Buying Murabaha'),
                                      ('salam', 'Salam'), ('ejara', 'Ejara'), ('gard_hassan', 'Gard Hassan'),
                                      ('estisnaa', 'Estisnaa'), ('mugawla', 'Mugawla'), ('mudarba', 'Mudarba'),
                                      ('musharka', 'Musharka'), ('muzaraa', 'Muzaraa')], string='Formula',
                                     related="order_id.formula_clone",readonly=True)
    murabaha_selection = fields.Selection(
        [('fixed_murabaha', 'Fixed Murabaha'), ('dec_murabaha', 'Decrmental Murabaha'), ],readonly=True,related="order_id.murabaha_selection" ,string='Murabaha Type')
    original_amount = fields.Monetary(string='Original Amount', related="order_id.amount")
    portfolio_id = fields.Many2one('finance.portfolio', string="Portfolio", related="order_id.portfolio_id",
                                   readonly=True)
    approval_id = fields.Many2one('finance.approval',required=1, string="Approval Ref")

    new_amount = fields.Float(required=1)
    new_formula = fields.Selection([('fixed_murabaha', 'Fixed Murabaha'), ('dec_murabaha', 'Decremental Murabaha'),
                                    ('salam', 'Salam'), ('ejara', 'Ejara'), ('gard_hassan', 'Gard Hassan'),
                                    ('estisnaa', 'Estisnaa'), ('mugawla', 'Mugawla'), ('mudarba', 'Mudarba'),
                                    ('musharka', 'Musharka'), ('muzaraa', 'Muzaraa')], string='New Formula')
    new_formula_clone = fields.Selection([('murabaha', 'Murabaha'), ('buying_murabaha', 'Buying Murabaha'),
                                      ('salam', 'Salam'), ('ejara', 'Ejara'), ('gard_hassan', 'Gard Hassan'),
                                      ('estisnaa', 'Estisnaa'), ('mugawla', 'Mugawla'), ('mudarba', 'Mudarba'),
                                      ('musharka', 'Musharka'), ('muzaraa', 'Muzaraa')], string='Formula',
                                     required=True)
    new_murabaha_selection = fields.Selection(
        [('fixed_murabaha', 'Fixed Murabaha'), ('dec_murabaha', 'Decrmental Murabaha'), ], string='Murabaha Type')

    new_approval = fields.Many2one('finance.approval',string="New Approval",readonly=1)
    state = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'Waiting Recommend'),
                              ('approval_recommended', 'Approval Recommended'),
                              ('su_recommend', 'Supervisor Recommend'),
                              ('br_recommend', 'Branch Manager Recommend'),
                              ('op_recommend', 'Operation Manager Recommend'),
                              ('approved', 'Approved'),
                              ('cancel', 'Canceled')], string='State',
                              default="draft")
    status = fields.Selection(
        [('br_recommend', 'br_recommend'), ('op_recommend', 'op_recommend'), ('approved', 'approved')],
        compute='_get_status')

    @api.multi
    @api.onchange('new_formula_clone', 'new_murabaha_selection')
    def _formual_clone_set(self):
        """
        Desc: set Formula from formula clone in Formula Fields
        :return:
        """
        if (
            self.new_formula_clone == 'murabaha' or self.new_formula_clone == 'buying_murabaha') and self.new_murabaha_selection == 'fixed_murabaha':
            self.new_formula = 'fixed_murabaha'
        elif (
                        self.new_formula_clone == 'murabaha' or self.new_formula_clone == 'buying_murabaha') and self.new_murabaha_selection == 'dec_murabaha':
            self.new_formula = 'dec_murabaha'
        elif self.new_formula_clone == 'salam':
            self.new_formula = 'salam'
        elif self.new_formula_clone == 'ejara':
            self.new_formula = 'ejara'
        elif self.new_formula_clone == 'gard_hassan':
            self.new_formula = 'gard_hassan'
        elif self.new_formula_clone == 'estisnaa':
            self.new_formula = 'estisnaa'
        elif self.new_formula_clone == 'mugawla':
            self.new_formula = 'mugawla'
        elif self.new_formula_clone == 'mudarba':
            self.new_formula = 'mudarba'
        elif self.new_formula_clone == 'musharka':
            self.new_formula = 'musharka'
        elif self.new_formula_clone == 'muzaraa':
            self.new_formula = 'muzaraa'
        else:
            self.new_formula = False


    @api.multi
    def unlink(self):
        """
        to allow to delete order in draft state
        :raise: exceptions
        :return: message with validation error
        """
        for state in self.search([('id', 'in', self.ids)]):
            if state.state != 'draft':
                raise exceptions.ValidationError(_("you cannot delete extra order when it not in draft state" ))
            elif self.state == 'draft':
                return super(finance_extra_order, self).unlink()

    @api.constrains('new_amount')
    def check_amount(self):
        """
        check if the amount is less than zero or less than 1
        :return:
        """
        if self.new_amount <= 0:
            raise exceptions.ValidationError(_("amount must be more than zero"))

    @api.model
    def get_seq_extra_order(self):
        """
        to get extra order sequence to view
        :return:
        """
        return self.env['ir.sequence'].search([('code', '=', self._name)]).get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        """
        to increment the sequence and save it
        :return:
        """
        order_id = self.env['finance.order'].search([('id', '=', vals['order_id'])])
        vals['name'] = order_id.name + ' ' + self.env['ir.sequence'].get(self._name) or '/'
        extra_order = self.env['finance.extra.order'].search([('order_id', '=', vals['order_id'])])
        for order in extra_order:
            if order.order_id.id == vals['order_id']:
                raise exceptions.ValidationError(_('you have extra order with this number % s' % order.name))
        return super(finance_extra_order, self).create(vals)

    @api.depends('state', 'new_approval.approve_amount')
    def _get_status(self):
        """
        Desc : Get State to sh
        :return:
        """
        approved_amount = sum([lines.approve_amount for lines in self.new_approval])
        approved_amount += self.approval_id.approve_amount
        if self.state == 'su_recommend':
            self.status = approved_amount > self.company_id.br_ceiling and 'br_recommend' or 'approved'
        elif self.state == 'br_recommend':
            if approved_amount > self.company_id.op_ceiling:
                self.status = 'op_recommend'
            else:
                self.status = 'approved'
        elif self.state == 'op_recommend':
            self.status = 'approved'

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
    def act_approved(self, all_members_number):
        #celling = 0
        for lines in self.new_approval:

            lines.action_recommend_approved()
            for line in self.approval_id.installment_ids:
                if line.state != 'done':
                    line.state = 'transfered'
        return self.write({'state': 'approved'})

    @api.multi
    def act_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def action_create_extra_order(self):
        """
        Desc : Create New Approval
        :return:
        """
        visit_id = self.visit_id.id
        res = 0
        for line in self.approval_id.installment_ids:
            res += line.residual
        new_approval = self.env['finance.approval'].create({
            'visit_id': self.visit_id.id,
            'formula': self.new_formula,
            'formula_clone':self.new_formula_clone,
            'trust_receipt':self.approval_id.trust_receipt,
            'check':self.approval_id.check,
            'electronic':self.approval_id.electronic,
            'permanent_payment':self.approval_id.permanent_payment,
            'user_id': self.order_id.user_id.id,
            'project_id': self.approval_id.project_id.id,
            'payment_method_id': self.approval_id.payment_method_id.id,
            'installment_no': 0,
            'approve_amount': self.new_amount,
            'profit_margin': 0,
            'grace_period': 0,
            'org_percentage':0,
            'customer_percentage':0,
            'third_percentage':0,
            'approval_type': 'extra_order',
            'residual_approval' : res,
            'installment_no':1,
            'company_id':self.company_id.id
        })
        self.new_approval = new_approval.id
        self.state = 'in_progress'

    @api.onchange('order_id')
    def _domain_approval_id(self):
        """
        Desc: return just approval related to order
        :return: domain
        """
        approval_ids = []
        for line in self.order_id.approve_ids:
            approval_ids.append(line.id)
        return {'domain': {'approval_id': [('id', 'in', approval_ids)]}}


class finance_visit(models.Model):
    _name = 'finance.visit'
    _description = 'Finance Visit'
    _order = "create_date desc"
    _inherit = ['mail.thread']

    name = fields.Char(string='Visit Number', copy=False, default='/',readonly=True)
    order_id = fields.Many2one('finance.order',string='Order',readonly=True)
    date = fields.Date(index=True, default=fields.Datetime.now())
    company_id = fields.Many2one('res.company', string='Branch', default=lambda self: self.env['res.company']._company_default_get('finance.visit'), readonly=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, readonly=True)
    project_status = fields.Selection([('new', 'New'), ('exist', 'Exist'), ('stopped', 'Stopped')], related="order_id.project_status", string='Project Status', required=True)
    product_id = fields.Many2one('finance.product', domain=[('state','=','approve')],string="Product")
    #Assets
    asset_line_ids=fields.One2many('finance.asset.line','visit_id')
    fix_value = fields.Float(string="Fixed Total",compute="_compute_assets",readonly=True)
    current_value = fields.Float(string="Current Total",compute="_compute_assets",readonly=True)
    asset_value = fields.Float(string="Assets Total",compute="_compute_assets",readonly=True)
    current_sale=fields.Float(string="Monthly Sale Avg.")
    current_prof = fields.Float(string="Monthly Profit Net.")
    avg_sale = fields.Float(string="Monthly Sale Avg.")
    avg_prof = fields.Float(string="Monthly Profit Net.")
    approve_ids = fields.One2many('finance.approval', 'visit_id')
    partner_id = fields.Many2one(string="Customer", related='order_id.partner_id', store=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], required=True,default='draft', readonly=True, track_visibility='onchange')


    @api.constrains('date')
    def check_order_date(self):
        """
        check if the visit date is before than order date
        :return:
        """
        if self.order_id.date > self.date:
            raise exceptions.ValidationError(_('visit date cannot be before the order date'))

    @api.multi
    def action_open_order(self):
        '''
        This function opens the order form (individual, group) that the visit created from.
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        if self.order_id.type == 'group':
            ids = self.env['finance.group.order'].search([('order_id', '=', self.order_id.id)]).id 
            try:
                res = ir_model_data.get_object_reference('microfinance', 'view_finance_group_order_form')[1]
            except ValueError:
                res = False
                  
            return {
                'name': _('Finance Group Order'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'finance.group.order',
                'views': [(res, 'form')],
                'view_id':[res],
                'res_id':  ids,
                'noupdate': True,
                'target': 'current',
            }
        elif self.order_id.type == 'individual':
            ids = self.env['finance.individual.order'].search([('order_id', '=', self.order_id.id)]).id
            try:
                res = ir_model_data.get_object_reference('microfinance', 'view_finance_order_form')[1]
            except ValueError:
                res = False
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'finance.individual.order',
                'views': [(res, 'form')],
                'view_id':[res],
                'res_id': ids,
                'target': 'current',
            }

    @api.multi
    def get_amount(self):
        """
        Get Default Value for amount field in approve_ids
        :return:
        """
        if self._context.has_key('id'):
            for record in self.env['finance.visit'].search([('id', '=', self._context.get('id'))]):
                for order in self.env['finance.order'].search([('id', '=', record.order_id.id)]):
                    return order.amount

    @api.depends('asset_line_ids')
    def _compute_assets(self):
        """
        Desc : compute total Assets
        :return:
        """
        for l in self.asset_line_ids:
            if(l.asset_type == "fixed" ):
                self.fix_value += (l.market_value * l.number)
            else:
                self.current_value += (l.market_value * l.number)
        self.asset_value = self.fix_value + self.current_value

    @api.one
    def action_done(self):
        #prevent change state if no approval record created
        if len(self.approve_ids) == 0:
            raise UserError(_('Recommendations must be added before making visit Done'))
        if self.env['finance.approval'].search([('state','!=','recommend'),('visit_id','=',self.id)]):
            raise UserError(_('All recommendations state should be recommend before making visit Done'))
        self.order_id.write({'state': 'visit_complete'})
        self.write({'state': 'done'})

    @api.one
    def action_cancel(self):
        self.write({'state' : 'cancel'})


class finance_asset_line(models.Model):
    _name = 'finance.asset.line'
    _description = 'Finance Asset Line'

    name = fields.Char(string="Asset Name", required=True)
    asset_type = fields.Selection([("fixed", "Fixed"), ("current", "Current")], required=True)
    number = fields.Integer(string="Quantity", required=True)
    market_value = fields.Float(string="Market Value", required=True)
    visit_id = fields.Many2one('finance.visit',ondelete='restrict')


class finance_installments(models.Model):
    _name = 'finance.installments'
    _order = 'due_date'

    installment_no = fields.Integer(string="No.", readonly=True)
    partner_id = fields.Many2one(string="Customer", related='approval_id.partner_id', store=True)
    due_date = fields.Date(index=True,string="Due Date", required="True")
    date = fields.Date(string="Receive Date")
    amount_before_profit = fields.Float(string="Amount Before Profit")
    profit_amount = fields.Float(string="Profit Amount")
    amount = fields.Float(string="Amount")
    receive_amount = fields.Float(string="Receive Amount")
    residual = fields.Float(string="Residual", compute="_compute_amounts")
    order_type = fields.Selection([('individual', 'Individual'), ('group', 'Group')], string='Order Type')
    indivadial_order = fields.Many2one('finance.order',ondelete='restrict')
    approval_id = fields.Many2one('finance.approval')
    line_id = fields.Many2one('account.move.line', ondelete='restrict')
    state = fields.Selection([('draft', 'Draft'), ('delay', 'Delay'), ('adverse', 'Adverse'), ('done', 'Done'),('transfered','Transfered')],
                             string='State', default='draft')
    user_id = fields.Many2one(related='approval_id.user_id', store=True, readonly=True, copy=False)
    company_id = fields.Many2one(related='approval_id.company_id', store=True, readonly=True, copy=False)
    is_migration = fields.Boolean('Migration',default=False)


    def _search_status(self,operator, value):
        value = isinstance(value,list) and tuple(value) or value
        self.env.cr.execute("""SELECT id FROM 
                                (SELECT id,CASE
                                    WHEN (amount-receive_amount) > 0 AND due_date < CURRENT_DATE - INTERVAL '30 day' then 'adverse'
                                    WHEN (amount-receive_amount) > 0 AND due_date < CURRENT_DATE then 'delay'
                                    WHEN (amount-receive_amount) <= 0 then 'done'
                                    ELSE 'draft' 
                                    END AS state
                                FROM finance_installments) s
                            WHERE state """+operator+' %s',(value,))
        ids = [x[0] for x in self.env.cr.fetchall()]
        return [('id', 'in', ids)] 


    def update_state(self):
        for i in self.search([('state','not in',('done','adverse'))]):
            if i.residual > 0 and i.due_date < str(datetime.today().date() - timedelta(days=30)) and i.state != 'adverse':
                i.state = 'adverse'
            elif i.residual > 0 and i.due_date < str(datetime.today().date()) and i.state != 'delay':
                i.state = 'delay'
            elif i.residual == 0 and i.state != 'done':
                i.state = 'done'
                if not i.date:
                    i.date = datetime.today().date()

    @api.depends('amount', 'receive_amount')
    @api.multi
    def _compute_amounts(self):
       for i in self:
            i.residual = max(i.amount-i.receive_amount,0)


    @api.multi
    def pay(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        return {
            'name': _('Pay Installment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'view_id': self.env.ref("microfinance.view_installment_payment_wizard",False).id,
            'target': 'new',
            'context': {'installment_id':self.id,
                        'default_amount':self.residual,
                        'default_partner_id':  self.partner_id.id,
                        'default_payment_type': 'inbound',
                        'default_partner_type': 'customer',
                        'default_destination_account_id': self.line_id.account_id.id
                       }
        }


class finance_approval_re_scheduel_wiz(models.TransientModel):
    _name = "finance.approval.reschedule.wiz"
    _order = "create_date desc"
    _description = "Approval Re-Scheduel"

    @api.multi
    def get_residual_amount(self):
        """
        to get the residual amount to Re-schedule it
        :return:
        """
        approval_id = self._context.get('re_sche')
        total_residual_amount = 0
        approval_ids = self.env['finance.approval'].search([('id', '=', approval_id)])
        for installment in approval_ids.installment_ids:
            total_residual_amount += installment.residual
        return total_residual_amount

    @api.multi
    def get_assets(self):
        """
        to get the residual assest amount to Re-schedule it
        :return:
        """
        assets = 0
        recive = 0
        new_total = 0
        approval_id = self._context.get('re_sche')
        approval_ids = self.env['finance.approval'].search([('id', '=', approval_id)])
        for installment in approval_ids.installment_ids:
            if installment.state != 'done':
                assets += installment.amount_before_profit
                recive += installment.receive_amount
        if recive > assets:
            new_total = recive - assets
        elif assets > recive:
            new_total = assets - recive
        return new_total

    re_scheduel_amount = fields.Integer('Re-Schedule Amount',readonly=1,required = 1, default = get_residual_amount)
    formula = fields.Selection([('fixed_murabaha', 'Fixed Murabaha'), ('dec_murabaha', 'Decremental Murabaha'),
                                ('salam', 'Salam'), ('ejara', 'Ejara'), ('gard_hassan', 'Gard Hassan'),
                                ('estisnaa', 'Estisnaa'), ('mugawla', 'Mugawla'), ('mudarba', 'Mudarba'),
                                ('musharka', 'Musharka'), ('muzaraa', 'Muzaraa')], string='Formula', readonly=True,
                               default=lambda self:self._context.get('formula',False))
    profit = fields.Float('Profit',required=1,default=lambda self:self._context.get('profit',False))
    assest = fields.Float('Assest',readonly=1,required=1, default=get_assets)
    ins_profit = fields.Float('Installment Profit')
    ins_after_profit = fields.Float('Installment after Profit')
    installment_no = fields.Integer('Installment No',required=1,default=lambda self:self._context.get('count_not_done',False))
    payment_method_id = fields.Many2one('finance.payment.method', string="Payment Method", required=1,default=lambda self:self._context.get('payment_method_id',False),)
    grace_period = fields.Integer(string="Grace Period",required=1,default=lambda self:self._context.get('grace_period',False))
    approval=fields.Many2one('finance.approval',default=lambda self:self._context.get('approval_id',False))
    inst_date= fields.Date('Installment Startb Date',required=1)


    @api.constrains('inst_date','profit','installment_no','grace_period')
    def check_date(self):
        """
        To check the date of Re-Schedule it must be after the last payment date
        :return:
        """
        last_date = max([datetime.strptime(l.date, '%Y-%m-%d')]for l in self.approval.payment_ids)
        if str(self.inst_date) < str(last_date[0]):
            raise exceptions.ValidationError(_('Re-Schedule Date must be after the last payment %s') % datetime.strftime(last_date[0], '%Y-%m-%d'))
        if self.profit <= 0:
            raise exceptions.ValidationError(_("Profit amount cannot be zero or less"))
        elif self.installment_no <= 0:
            raise exceptions.ValidationError(_("Installment no cannot be zero or less"))
        elif self.grace_period < 0:
            raise exceptions.ValidationError(_("grace period cannot be less than zero "))



    @api.depends('approval.payment_period', 'approval.payment_days', 'approval.project_id.profit_margin', 'approval.amount', 'approval.installment_no',
                 'approval.org_percentage', 'approval.customer_percentage', 'approval.third_percentage', 'approval.expected_profit', 'approval.expected_production',
                 'approval.expected_price', 'approval.org_qty', 'approval.customer_qty', 'approval.downpayment', 'approval.profit_margin', 'approval.ins_profit',
                 'approval.approve_amount', 'approval.customer_percentage', 'approval.org_percentage', 'approval.third_percentage')
    def _compute_formula(self):
        """
        Check The Type of formula and Calculate for Re-Schecduel
        :return:
        """
        # Calculate Formula fixed murabaha estisnaa mugawla ejara gard_hassan Common calculations
        for rec in self.approval:
            # in case extra order add residual from prev approval to total_funding
            rec.total_funding += rec.residual_approval
            if (self.installment_no != 0):
                payment_period = ((rec.payment_period * 30) + rec.payment_days) / 30
                rec.ins_before_profit = self.assest
                rec.profit = self.profit
                rec.total_funding = rec.profit + rec.amount - rec.downpayment
                rec.ins_after_profit = rec.total_funding / rec.installment_no
                rec.ins_profit = rec.ins_after_profit - rec.ins_before_profit
            else:
                rec.ins_after_profit = 0

            # Calculate Formula mudarba
            if rec.formula in ['mudarba', 'musharka']:
                rec.org_profit = (rec.org_percentage * rec.expected_profit) / 100
                rec.custumer_profit = (rec.customer_percentage * rec.expected_profit) / 100

            # Calculate Formula musharka
            if rec.formula == 'musharka':
                rec.third_profit = (rec.third_percentage * rec.expected_profit) / 100

            # Calculate Formula salam
            if rec.formula == 'salam':
                rec.customer_qty = (rec.customer_percentage * rec.expected_production) / 100
                rec.customer_amount = (rec.expected_price * rec.customer_qty)
                rec.org_qty = (
                                  rec.org_percentage * rec.expected_production) / 100  # rec.expected_production - rec.customer_qty
                rec.org_amount = (rec.expected_price * rec.org_qty)

            # Calculate Formula dec_murabaha
            if rec.formula == 'dec_murabaha':
                margin_avg = sum(
                    range(self.grace_period + 1, rec.payment_period + 1)) * rec.profit_margin / self.installment_no
                rec.ins_profit = margin_avg * (rec.approve_amount - rec.downpayment) / 100 / self.installment_no
                rec.ins_after_profit = self.ins_before_profit + rec.ins_profit
                rec.profit = rec.ins_profit * rec.installment_no
                rec.total_funding = rec.ins_after_profit * rec.installment_no

    @api.one
    def action_re_scheduel(self):
        """
        Desc  : Re-Schedule Approval Installments
        :return:
        """
        self.check_date
        if self.profit > self._context.get('profit',False):
            raise exceptions.ValidationError(_('The Profit Must be less than Resuidual Profit in installments'))
        #if self.assest > self._context.get('assest',False):
        #    raise exceptions.ValidationError(_('The Assest must be less than ResuduaL Assest in installment'))

        approval = self.env['finance.approval'].search([('id','=',self._context['current_id'])])
        approval.re_schedule_no += 1
        approval.ins_before_profit = self.assest
        approval.profit = self.profit
        approval.grace_period = self.grace_period
        profit_done = 0
        seq = 0

        for line in approval.installment_ids:
            for line in approval.installment_ids:
                if line.state in ['draft', 'delay', 'adverse'] and line.receive_amount == 0:
                    # To unlink installment and Reschedule it
                    line.unlink()
                elif line.state in ['draft', 'delay', 'adverse'] and line.receive_amount != 0:
                    # check for part-payment in installment
                    if line.receive_amount > line.amount_before_profit:
                        reaming_profit = line.amount - line.receive_amount
                        re_profit = reaming_profit
                        re_total = line.amount_before_profit + re_profit
                        line.update({
                            'amount': re_total,
                            'amount_before_profit': line.amount_before_profit,
                            'profit_amount': re_profit,
                            'receive_amount': line.receive_amount})
                    elif line.receive_amount < line.amount_before_profit:
                        re_amount = line.receive_amount
                        re_profit = line.profit_amount
                        re_total = re_amount + re_profit
                        line.update({
                            'amount': re_total,
                            'amount_before_profit': re_amount,
                            'profit_amount': re_profit,
                            'receive_amount': re_amount, })
                    elif line.receive_amount == line.amount_before_profit:
                        re_amount = line.amount_before_profit
                        re_profit = 0
                        re_total = re_amount + re_profit
                        line.update({
                            'amount': re_total,
                            'amount_before_profit': re_amount,
                            'profit_amount': re_profit,
                            'receive_amount': re_amount, })
                else:
                    profit_done += line.profit_amount
            break
        for line in approval.installment_ids:
            seq = line.installment_no
        amount_before_profit_sum = 0
        profit_amount = 0
        # to get max payment ids.date
        #my_date = max([datetime.strptime(l.date, '%Y-%m-%d') for l in  approval.payment_ids])
        my_date = datetime.strptime(self.inst_date, '%Y-%m-%d')
        #self.installment_ids.unlink()
        """if ( approval.downpayment > 0):
            self.env['finance.installments'].create({
                'installment_no': 0,
                'amount':  approval.downpayment,
                'due_date': my_date,
                'approval_id':  approval.id,
            })"""
        my_date = my_date + relativedelta(months=self.grace_period)
        #my_date = my_date

        # Calculate Formula fixed murabaha estisnaa mugawla ejara

        if approval.formula != 'dec_murabaha' or (approval.formula == 'dec_murabaha' and  approval.calc_type == 'average'):
            for i in range(1, self.installment_no + 1):
                if i == 1:
                    my_date = my_date + relativedelta(months=0)
                else:
                    my_date = my_date + relativedelta(months=1)
                self.env['finance.installments'].create({
                    'installment_no': i + seq,
                    'due_date': my_date.strftime('%m/%d/%y'),
                    'amount':  (self.profit/self.installment_no) + (self.assest/self.installment_no),
                    'approval_id':  approval.id,
                    'amount_before_profit':  self.assest/self.installment_no,
                    'profit_amount':  self.profit/self.installment_no
                })
                amount_before_profit_sum += self.assest
                profit_amount += self.profit

        # Calculate Formula dec_murabaha
        elif self.formula == 'dec_murabaha' and self.calc_type == 'decremental':
            # payment_Period = ((self.payment_period * 30) + self.payment_days) / 30
            for i in range(1, self.installment_no + 1):
                if i == 1:
                    my_date = my_date + relativedelta(months=0)
                else:
                    my_date = my_date + relativedelta(months=1)
                monthly_repayment = self.grace_period + i
                installment_margin =  approval.profit_margin * monthly_repayment
                ins_profit = (( approval.approve_amount - self.downpayment) / self.installment_no * installment_margin) / 100
                ins_amount = ins_profit +  self.ins_before_profit
                self.env['finance.installments'].create({
                    'installment_no': i + seq,
                    'due_date': my_date.strftime('%m/%d/%y'),
                    'amount': ins_amount,
                    'approval_id':  approval.id,
                    'amount_before_profit':  self.assest,
                    'profit_amount': ins_profit
                })
                amount_before_profit_sum += self.assest
                profit_amount += self.profit
                raise exceptions.ValidationError(
                    _('The Assest must be less than Resuduak Assest in installment ' + move_id.id + ' here'))

        # Accounting Section
        """
        Create account.move & and account.move.line
        """
        company_journal = approval.company_id.journal_id.id
        expected_profit_account = approval.visit_id.order_id.portfolio_id.expected_profit_account_id.id
        profit_margin_account = approval.visit_id.order_id.portfolio_id.profit_margin_account_id.id
        # check if branch have journal & Expected Profit Amount Account in Micro finance setting
        if (company_journal == False):
            raise UserError(_('You must First Specify Journal Account in Micro-Finance Settings'))
        if (expected_profit_account == False):
            raise UserError(
                _('You must First Specify Expected Profit Amount Account in Micro-Finance Settings'))
        if profit_margin_account == False:
            raise UserError(
                _('You must specify profit margin account for your portfolio'))
        if (approval.approval_type != 'extra_order'):
            if (approval.visit_id.order_id.portfolio_id.property_account_receivable_id.id == False):
                raise UserError(_('You must First Specify Property Account Receivable in Selected Portfolio'))

        #################
        # make clone of installment inserted to just show sum of profit and asset installment
        if self.profit < self._context.get('profit',False):
            if self.profit:
                move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': 'Re-Schedule',
                    'date': datetime.today(),
                    'company_id': approval.company_id.id,
                    'partner_id': approval.partner_id.id,
                    'journal_id': company_journal,
                    'line_ids': [(0, 6, {'name': _('Profit Marigin Re-Schedule'),
                                        'due_date': datetime.today(),
                                        'account_id': profit_margin_account,
                                        'debit': 0.0,
                                        'credit': self._context.get('profit',False) - self.profit,
                                        'partner_id': approval.partner_id.id}),
                                (0, 6, {'name': _('Expected Profit Re-Schedule'),
                                        'due_date': datetime.today(),
                                        'account_id': expected_profit_account,
                                        'debit': self._context.get('profit',False) - self.profit,
                                        'credit': 0.0,
                                        'partner_id': approval.partner_id.id})]
                })

        approval.write({'state': 'in_progress'})



class finance_approval(models.Model):
    _name = 'finance.approval'
    _order = "create_date desc"
    _inherit = ['mail.thread']

    @api.multi
    def get_default(self):
        """
        set the default value for the approve_amount
        :return:
        """
        amount = self.visit_id.get_amount()
        return amount

    name = fields.Char(string="approval number", readonly=True,copy=False)
    order_no = fields.Char(related="visit_id.order_id.name", string='order number', readonly=True)
    project_id = fields.Many2one('finance.project', string="Project",required=False)
    amount = fields.Monetary(string='Funding Amount',compute="_compute_amount" ,currency_field='company_currency_id', track_visibility='onchange')#approve_amount+insurance_amount
    approve_amount = fields.Monetary(string='Approve Amount', required=True, currency_field='company_currency_id', default=get_default) #for profit calculation
    insurance_amount = fields.Monetary('Insurance Amount', currency_field='company_currency_id')
    profit = fields.Monetary(string='Profit', currency_field='company_currency_id', compute= '_compute_formula', track_visibility='onchange')
    total_funding = fields.Monetary(string='Total Funding', compute= '_compute_formula', currency_field='company_currency_id', track_visibility='onchange')#amount+profit 
    formula = fields.Selection([('fixed_murabaha','Fixed Murabaha'), ('dec_murabaha','Decremental Murabaha'), 
                                ('salam', 'Salam'), ('ejara','Ejara'), ('gard_hassan','Gard Hassan'),
                                ('estisnaa','Estisnaa'), ('mugawla','Mugawla'), ('mudarba','Mudarba'),
                                ('musharka','Musharka'), ('muzaraa','Muzaraa') ], string='Formula', required=True, track_visibility='onchange')
    formula_clone = fields.Selection([('murabaha','Murabaha'), ('buying_murabaha','Buying Murabaha'),
                                ('salam', 'Salam'), ('ejara','Ejara'), ('gard_hassan','Gard Hassan'),
                                ('estisnaa','Estisnaa'), ('mugawla','Mugawla'), ('mudarba','Mudarba'),
                                ('musharka','Musharka'), ('muzaraa','Muzaraa') ], string='Formula', required=True)
    murabaha_selection = fields.Selection([('fixed_murabaha', 'Fixed Murabaha'), ('dec_murabaha', 'Decrmental Murabaha'),], string='Murabaha Type')
    profit_margin = fields.Float(string='Profit Margin', required=True, track_visibility='onchange')
    installment_no = fields.Integer(string="No of Installments", required=True, track_visibility='onchange')
    grace_period = fields.Integer(string="Grace Period", required=True, track_visibility='onchange')
    payment_period = fields.Integer(string="Payment Period", compute='_get_payment_period', required=True, track_visibility='onchange')
    payment_days = fields.Integer(string="Payment Days", compute='_get_payment_period', required=True)
    payment_method_id = fields.Many2one('finance.payment.method', string="Payment Method",ondelete='restrict', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Branch')
    trust_receipt = fields.Boolean(string="Trust Receipt")
    check = fields.Boolean(string="Check Payment")
    permanent_payment = fields.Boolean(string="Permanent payment order")
    electronic = fields.Boolean(string="Electronic Payment")
    visit_id = fields.Many2one('finance.visit')
    company_currency_id = fields.Many2one('res.currency', string="Company Currency",
                                          related='company_id.currency_id',help='Utility field to express amount currency', store=True)
    payment_ids = fields.One2many('finance.approval.payment','approval_id')
    user_id = fields.Many2one('res.users', string="Officer", default=lambda self: self.env.user, readonly=True,
                              required=True, ondelete='restrict')
    calc_type = fields.Selection([('average', 'Average'), ('decremental', 'Decremental')],
                                 string="Calculation Type", default='average')
    installment_ids = fields.One2many('finance.installments', 'approval_id')
    downpayment=fields.Monetary('Down-Payment', currency_field='company_currency_id')
    hide = fields.Boolean(string='Hide', help="To help make downpayment visible when project.overdrow = True",
                          compute="_compute_hide")
    partner_id = fields.Many2one(string="Customer", related='visit_id.partner_id', store=True)
    insurance_partner_id = fields.Many2one('res.partner',domain="[('supplier','=','True')]",string="Insurance Partner")
    expense_partner_id = fields.Many2one('res.partner',domain="[('supplier','=','True')]",string="Expense Partner")
    state = fields.Selection([('draft', 'Draft'), ('recommend', 'Recommend'),
                              ('approved', 'Approved'), ('paid', 'Paid'), ('in_progress', 'In Progress'),
                              ('done', 'Done'),('canceled','Canceled')], default='draft', readonly=True, string="State",
                             track_visibility='onchange')
    # dec_murabaha
    ins_before_profit = fields.Monetary(string='Installment Before Profit', currency_field='company_currency_id', compute= '_compute_formula')#(amount-downpayment)/installment_no
    ins_profit = fields.Monetary(string='Installment Profit Avg.', currency_field='company_currency_id', compute= '_compute_formula')#average sum(range(1,installment_no))*profit_margin/installment_no
    # Fixed Murabaha & dec_murabaha
    ins_after_profit = fields.Monetary(string='Installment Amount', currency_field='company_currency_id', compute= '_compute_formula') #dec_murabaha:ins_profit*(approve_amount-downpayment)/100/installment_no 
                                                                        #(approve_amount-downpayment)*profit_margin
    #ins_prof_margin = fields.Float(string='Installment Profit Margin')  
    mudarba_type = fields.Selection(string='Mudarba Type', readonly=False,
                                    selection=[('restricted', 'Restricted'), ('not-restricted', 'Not-Restricted')])
    #Mudarba, Musharka, Salam & Muzaraa
    capital = fields.Monetary(string='Capital', currency_field='company_currency_id')# Same as approve_amount
    #Mudarba, Musharka & Muzaraa
    org_percentage = fields.Integer(string='Organization', required=True,track_visibility='onchange')
    customer_percentage = fields.Integer(string='Customer', required=True, track_visibility='onchange')
    #Mudarba & Musharka 
    expected_profit = fields.Monetary(string='Expected Profit', currency_field='company_currency_id')
    org_profit = fields.Float(string='Organization Profit', currency_field='company_currency_id', 
                             compute= '_compute_formula')#org_percentage*expected_profit/100
    custumer_profit = fields.Monetary(string='Customer Profit', currency_field='company_currency_id',
                             compute= '_compute_formula')#customer_percentage*expected_profit/100
    #Musharka & Muzaraa
    third_percentage = fields.Integer(string='Third Party', required=True, track_visibility='onchange')
    #Musharka
    third_profit = fields.Monetary(string='Third Party Profit', currency_field='company_currency_id', 
                                   compute= '_compute_formula')#third_percentage*expected_profit/100
    #Salam & Muzaraa
    crop_id = fields.Many2one('finance.crop', string="Crop", track_visibility='onchange')
    uom = fields.Many2one(related='crop_id.uom_id', string='Unit of Measure')
    crop_price = fields.Monetary(string='Crop Price', currency_field='company_currency_id', track_visibility='onchange')
    expected_production = fields.Integer(string='Expected Production')
    expected_price = fields.Monetary(string='Expected Price', currency_field='company_currency_id')
    org_qty = fields.Integer(string='Organization Qty', compute= '_compute_formula')
    customer_qty = fields.Integer(string='Customer Qty', compute= '_compute_formula')
    org_amount = fields.Monetary(string='Organization Amount', currency_field='company_currency_id', compute= '_compute_formula', track_visibility='onchange')#(expected_price*org_qty)
    customer_amount = fields.Monetary(string='Customer Amount', currency_field='company_currency_id', compute= '_compute_formula', track_visibility='onchange')#(expected_price*customer_qty)
    #Muzaraa
    org_share = fields.Monetary(string='Organization Share', currency_field='company_currency_id', 
                               compute= '_compute_formula', track_visibility='onchange')#capital*org_percentage
    customer_share = fields.Monetary(string='Customer Share', currency_field='company_currency_id', compute= '_compute_formula', track_visibility='onchange')#(capital*customer_percentage
    third_qty = fields.Monetary(string='Third Party Qty', currency_field='company_currency_id', compute= '_compute_formula')
    third_amount = fields.Monetary(string='Third Party Amount', currency_field='company_currency_id',
                                   compute='_compute_formula')  # cal_org_amount = fields.Integer(string='Organization Amount')
    installments_number = fields.Integer(string='Installment Number', store=True, default=0)
    done_date = fields.Date(string='Done Date', compute='_compute_done_date')
    standing_balance = fields.Float(string="Standing Balance", store=True, compute='_compute_standing_balance')
    approval_type = fields.Selection([('normal_order', 'Normal Order'), ('extra_order', 'Extra Order')],
                                     default='normal_order',readonly=1)
    residual_approval =  fields.Float(string='Residaul from Approval',readonly=1,default=0)
    re_schedule_no= fields.Integer(string="Re-Schedule No",default=0,track_visibility='onchange')
    expenses = fields.Float(string="Expenses Amount")

    @api.constrains('grace_period', 'approve_amount', 'installments_number', 'profit_margin')
    def check_field(self):
        """
        check the fields if it zero or less than zero
        :return:
        """
        if not self._context.get('exo_id', False):
            if self.approve_amount <= 0:
                raise exceptions.ValidationError(_("amount must be more than zero"))
            if self.installment_no <= 0 and self.formula not in ['salam', 'mudarba', 'muzaraa', 'musharka']:
                raise exceptions.ValidationError(_("installment cannot be zero or less"))
            if not self._context.get('re_sche', False):
                if self.profit_margin <= 0 and self.formula not in ['gard_hassan', 'salam', 'mudarba', 'muzaraa','musharka']:
                    raise exceptions.ValidationError(_("profit margin cannot be zero or less"))
            if self.grace_period < 0:
                raise exceptions.ValidationError(_("grace period cannot be less than zero"))

    @api.multi
    def action_open_order(self):
        """
        this function open an order that related to this approval
        :return:
        """
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        if self.visit_id.order_id.type == 'group':
            ids = self.env['finance.group.order'].search([('order_id', '=', self.visit_id.order_id.id)]).id
            try:
                res = ir_model_data.get_object_reference('microfinance', 'view_finance_group_order_form')[1]
            except ValueError:
                res = False
            return {
                'name': _('Finance Group Order'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'finance.group.order',
                'views': [(res, 'form')],
                'view_id': [res],
                'res_id': ids,
                'noupdate': True,
                'target': 'current',

            }
        elif self.visit_id.order_id.type == 'individual':
            ids = self.env['finance.individual.order'].search([('order_id', '=', self.visit_id.order_id.id)]).id
            try:
                res = ir_model_data.get_object_reference('microfinance', 'view_finance_order_form')[1]
            except ValueError:
                res = False
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'finance.individual.order',
                'views': [(res, 'form')],
                'view_id': [res],
                'res_id': ids,
                'target': 'current',
            }

    @api.constrains('trust_receipt', 'electronic', 'permanent_payment', 'check')
    def _check_payemnt_type(self):
        """
        check if one of payment type is checked or not to raise an exception
        :return:
        """
        count = 0
        if not self.trust_receipt and not self.electronic and not self.permanent_payment and not self.check:
            raise exceptions.ValidationError(_("you must select one of the payment method"))
        if self.trust_receipt:
            count += 1
        if self.electronic:
            count += 1
        if self.permanent_payment:
            count += 18
        if self.check:
            count += 1
        if count > 1:
            raise exceptions.ValidationError(_("you Cannot select more than one Payment method"))


    @api.multi
    @api.onchange('formula_clone','murabaha_selection')
    def _formual_clone_set(self):
        """
        Desc: set Formula from formula clone in Formula Fields
        :return:
        """
        if (self.formula_clone == 'murabaha' or self.formula_clone == 'buying_murabaha') and self.murabaha_selection == 'fixed_murabaha':
            self.formula = 'fixed_murabaha'
        elif (self.formula_clone == 'murabaha' or self.formula_clone == 'buying_murabaha') and self.murabaha_selection == 'dec_murabaha':
            self.formula = 'dec_murabaha'
        elif self.formula_clone == 'salam':
            self.formula = 'salam'
        elif self.formula_clone == 'ejara':
            self.formula = 'ejara'
        elif self.formula_clone == 'gard_hassan':
            self.formula = 'gard_hassan'
        elif self.formula_clone == 'estisnaa':
            self.formula = 'estisnaa'
        elif self.formula_clone == 'mugawla':
            self.formula = 'mugawla'
        elif self.formula_clone == 'mudarba':
            self.formula = 'mudarba'
        elif self.formula_clone == 'musharka':
            self.formula = 'musharka'
        elif self.formula_clone == 'muzaraa':
            self.formula = 'muzaraa'
        else:
            self.formula = False
        #return {'domain': {'project_id': project_domain}}


    @api.multi
    def action_re_scheduel(self):
        ###### to open Re-Scheduel Wizard ######

        view_ref = self.env['ir.model.data'].get_object_reference('microfinance','finance_rescheduel_wiz_view')
        view_id = view_ref and view_ref[1] or False,

        re_scheduel_amount = 0

        count_not_done = 0
        assest = 0
        profit = 0
        for line in self.installment_ids:
            if line.state == 'draft' or line.state == 'adverse' or line.state == 'delay':
                re_scheduel_amount += line.amount
                assest += line.amount_before_profit
                profit += line.profit_amount
            if line.state != 'done':
                count_not_done += 1

        ###### context to send data from this record to wizard #######
        return {
            'type': 'ir.actions.act_window',
            'name': _('Re-Scheduel Order'),
            'res_model': 'finance.approval.reschedule.wiz',
            'context': {'current_id': self.id,
                        'formula':self.formula,
                        'grace_period':self.grace_period,
                        'payment_method_id':self.payment_method_id.id,
                        'count_not_done':count_not_done,
                        're_scheduel_amount':re_scheduel_amount,
                        'assest':assest,
                        'profit':profit,
                        'approval_id':self.id},
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
        }

    @api.one
    @api.depends('payment_ids')
    def _compute_done_date(self):
        """
        Desc:To help know approval done date
        :return:
        """
        for line in self.payment_ids:
            self.done_date = line.date

    @api.one
    def action_draft_recommend(self):
        self.write({'state': 'recommend'})

    @api.one
    def action_recommend_approved(self):
        """
        change state to approve and make payment_ids editable and create account payment
        """
        
        self.write({'state': 'approved'})
        if self.insurance_amount > 0:
            self.env['account.payment'].create({
                'beneficiary_id': self.insurance_partner_id.id,
                'payment_method_id': '',
                'partner_id': self.visit_id.order_id.partner_id.id,
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'amount': self.insurance_amount,
                'communication': _("Pay insurance amount"),
            })
        if self.expenses > 0:
            self.env['account.payment'].create({
                'beneficiary_id': self.expense_partner_id.id,
                'payment_method_id': '',
                'partner_id': self.visit_id.order_id.partner_id.id,
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'amount': self.expenses,
                'communication': _("Pay general expenses"),
            })

    @api.one
    def action_paid_in_progress(self):
        """
        Change The state to in_progress
        :return:
        """
        self.write({'state': 'in_progress'})

    @api.model
    def create(self, values):
        # Override the original create function for the finance_approval model
        # Change the value of variables in this super function to increment sequence and save it
        count = 1
        visit_id = self.env['finance.visit'].search([('id', '=', values['visit_id'])])
        order_id = self.env['finance.order'].search([('id', '=', visit_id.order_id.id)])
        for visit in visit_id:
            for approval_ids in visit.order_id.approve_ids:
                count += 1
        values['name'] = order_id.name + ' - '+ str(count)
        approval_project_ids = self.env['finance.approval'].search([('visit_id', '=', values['visit_id'])])
        if not self._context.get('exo_id', False):
            for approval in approval_project_ids:
                if approval.project_id.id == values['project_id']:
                    raise exceptions.ValidationError(_("you cannot use the same recommendation"))
            return super(finance_approval, self).create(values)
        if self._context.get('exo_id'):
            return super(finance_approval, self).create(values)

    @api.depends('project_id')
    def _compute_hide(self):
        """
        Desc:To help make downpayment visible when project.overdrow = True
        :return:
        """
        self.hide = True
        if self.project_id.overdrow == True:
                self.hide = False

    @api.one
    @api.depends('approve_amount', 'insurance_amount', 'downpayment', 'expenses')
    def _compute_amount(self):
        """
        Desc : compute amount
        :return:
        """
        self.amount = self.approve_amount+self.insurance_amount+self.expenses

    @api.multi
    def act_recommend(self):
        if self.approval_type == 'extra_order':
            for r in self.env['finance.extra.order'].search([('new_approval', '=', self.id)]):
                r.write({'state': 'approval_recommended'})

        return self.write({'state': 'recommend'})

    @api.multi
    @api.onchange('project_id')
    def _domain_product(self):
        """
        Desc: return just product with same type of order id (Individual or Group)
        :return: domain
        """
        project_domain = [('product_id', '=', self.visit_id.product_id.id)]
        project_domain+=self.visit_id.order_id.type == 'individual' and [('individual', '=', True)] or [('group', '=', True)]
        return {'domain': {'project_id': project_domain}}

    @api.onchange('project_id')
    def _get_fields(self):
        self.formula = self.project_id.formula
        self.formula_clone = self.project_id.formula_clone
        self.murabaha_selection= self.project_id.murabaha_selection
        self.profit_margin = self.project_id.profit_margin
        self.installment_no = self.project_id.installment_no
        self.grace_period = self.project_id.grace_period
        self.payment_method_id = self.project_id.payment_method_id
        self.payment_period = self.project_id.payment_period
        self.payment_days = self.project_id.payment_days

    @api.constrains('amount','payment_ids')
    def check_total_amount(self):
        """
        Check the total amount in payment_ids.ammount
        """
        payment_amount = 0 #sum(payment.amount for payment in self.payment_ids)
        for payment in self.payment_ids:
            if payment.state != 'canceled':
                payment_amount += payment.amount
        if self.approve_amount < payment_amount:
            raise exceptions.ValidationError(_('The Total of Payments Amount Must not exceed the Approve amount'))

    @api.onchange('formula')
    def specific__payment_formulas(self):
        """
        Desc : to set payment periode = to grace only in specific formulas
        :return:
        """
        if self.formula in ['salam', 'mudarba', 'musharka', 'muzaraa']:
            self.payment_period = self.grace_period
            self.payment_days = 0
        else:
            self.payment_period = (self.payment_method_id.number_of_days * self.installment_no) / 30 + self.grace_period
            self.payment_days = (self.payment_method_id.number_of_days * self.installment_no) % 30

    @api.multi
    @api.depends('payment_method_id.number_of_days', 'installment_no', 'grace_period')
    def _get_payment_period(self):
        """

        """
        for rec in self:
            if rec.formula in ['salam', 'mudarba', 'musharka', 'muzaraa']:
                rec.payment_period = rec.grace_period
                rec.payment_days = 0
            else:
                rec.payment_period = (rec.payment_method_id.number_of_days * rec.installment_no) / 30 + rec.grace_period
                rec.payment_days = (rec.payment_method_id.number_of_days * rec.installment_no) % 30

    @api.onchange('formula')
    def _onchange_formula(self):
        if self.formula in ('mudarba','musharka','salam','muzaraa'):
            self.profit_margin = 0
            self.installment_no = 1
        elif self.formula == 'gard_hassan':
            self.profit_margin = 0
            
    def create_installment(self):
        #to get max payment ids.date
        my_date = max([datetime.strptime(l.date, '%Y-%m-%d') for l in self.payment_ids])
        self.installment_ids.unlink()
        if (self.downpayment > 0):
            self.env['finance.installments'].create({
                'installment_no': 0,
                'amount': self.downpayment,
                'due_date': my_date,
                'approval_id': self.id,
            })
        my_date = my_date + relativedelta(months=((self.payment_method_id.number_of_days/30) + self.grace_period))
        # Calculate Formula fixed murabaha estisnaa mugawla ejara
        if self.formula != 'dec_murabaha' or (self.formula == 'dec_murabaha' and self.calc_type == 'average'):
            for i in range(1,self.installment_no + 1):
                if i == 1:
                    my_date = my_date + relativedelta(months=0)
                else:
                    my_date = my_date + relativedelta(months=self.payment_method_id.number_of_days/30)
                self.env['finance.installments'].create({
                    'installment_no': i,
                    'due_date':my_date.strftime('%m/%d/%y'),
                    'amount': self.ins_after_profit,
                    'approval_id':self.id,
                    'amount_before_profit':self.ins_before_profit,
                    'profit_amount':self.ins_profit
                })
                

        # Calculate Formula dec_murabaha
        elif self.formula == 'dec_murabaha' and self.calc_type == 'decremental':
            # payment_Period = ((self.payment_period * 30) + self.payment_days) / 30
            for i in range(1, self.installment_no + 1):
                if i == 1:
                    my_date = my_date + relativedelta(months=0)
                else:
                    my_date = my_date + relativedelta(months=self.payment_method_id.number_of_days/30)
                monthly_repayment = self.grace_period + i
                installment_margin = self.profit_margin * monthly_repayment
                ins_profit = ((self.approve_amount-self.downpayment)/self.installment_no * installment_margin) / 100
                ins_amount = ins_profit + self.ins_before_profit
                self.env['finance.installments'].create({
                    'installment_no': i,
                    'due_date': my_date.strftime('%m/%d/%y'),
                    'amount': ins_amount,
                    'approval_id': self.id,
                    'amount_before_profit':self.ins_before_profit,
                    'profit_amount': ins_profit
                })
        
        #Accounting Section
        """
        Create account.move & and account.move.line
        """
        company_journal = self.company_id.journal_id.id
        expected_profit_account = self.visit_id.order_id.portfolio_id.expected_profit_account_id.id
        profit_account = self.visit_id.order_id.portfolio_id.profit_account_id.id
        stock_account = self.company_id.stock_account_id.id
        #check if branch have rights journal setted in Account Micro finance setting
        if (company_journal == False):
            raise UserError(_('You must First Specify Journal Account in Acoounting - Micro-Finance SettingsSettings'))
        if (expected_profit_account == False):
            raise UserError(_('You must First Specify Expected Profit Amount Account in Acoounting - Micro-Finance Settings Settings'))
        if (profit_account == False):
            raise UserError(_('You must First Specify Profit Amount Account in Accounting - Micro-Finance Settings Settings'))
        if (stock_account == False):
                raise UserError(_('You must First Specify Stock  Account in Accounting - Micro-Finance Settings'))
        if (self.approval_type != 'extra_order'):
            if (self.visit_id.order_id.portfolio_id.property_account_receivable_id.id == False):
                raise UserError(_('You must First Specify Property Account Receivable in Selected Portfolio'))

        #Create Lines Credit (Officer,Expected Profit) , Depit (Profit,Assest,Insurance,Expenses)

        stock_amount = sum([p.amount for p in self.payment_ids if p.type=='stock'])
        Officer_amount = self.approve_amount - stock_amount

        #run Update State After Installment Sccessfully created
        self.env['finance.installments'].update_state()
        #################
        m_clone = [(0, 6, {
            'name': _('Assest'),
            'account_id': self.visit_id.order_id.portfolio_id.property_account_receivable_id.id,
            'debit': self.approve_amount,
            'credit': 0.0,
            'partner_id':self.visit_id.order_id.partner_id.id
        })]
	if Officer_amount:
            m_clone += [(0, 6, {
                'name': _('Officer'),
                'account_id': self.visit_id.order_id.user_id.partner_id.property_account_payable_id.id,
                'debit': 0.0,
                'credit': Officer_amount,
                'partner_id':self.visit_id.order_id.user_id.partner_id.id
            })]
        if stock_amount:
            m_clone += [(0, 6, {
                'name': _('Stock'),
                'account_id': stock_account,
                'debit': 0.0,
                'credit': stock_amount,
            })]
        if self.profit:
            m_clone += [(0, 6, {
                'name': _('Expected Profit'),
                'due_date': datetime.today(),
                'account_id': expected_profit_account,
                'debit': 0.0,
                'credit': self.profit,
                'partner_id':self.visit_id.order_id.partner_id.id
            })]
            m_clone += [(0, 6, {
                'name': _('Profit Margin'),
                'account_id': self.visit_id.order_id.portfolio_id.profit_margin_account_id.id,
                'debit': self.profit,
                'credit': 0.0,
                'partner_id':self.visit_id.order_id.partner_id.id
            })]

        move_id = self.env['account.move'].with_context(check_move_validity=False).create({
            'ref': self.name,
            'date': datetime.today(),
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'journal_id': company_journal,
            'line_ids': m_clone
        })

        self.write({'state': 'in_progress'})


    @api.constrains('org_percentage','customer_percentage', 'third_percentage')
    def _check_percentage(self):
        # Check if summation of percentages fields must be = 100.
        percentage_sum = 0
        if self.formula in ('mudarba', 'muzaraa', 'salam'):
            percentage_sum = self.org_percentage + self.customer_percentage
        elif self.formula == 'musharka':
            percentage_sum = self.org_percentage + self.customer_percentage + self.third_percentage
        if (percentage_sum > 0) and (percentage_sum != 100):
            raise UserError(_('The summation of Percentages fields not equal 100!'))


    @api.depends('payment_period','payment_days', 'project_id.profit_margin', 'amount', 'installment_no', 'org_percentage','customer_percentage','third_percentage', 'expected_profit', 'expected_production', 'expected_price', 'org_qty', 'customer_qty', 'downpayment', 'profit_margin','ins_profit', 'approve_amount', 'customer_percentage', 'org_percentage', 'third_percentage')
    def _compute_formula(self):
        """
        Check The Type of formula and Calculate
        :return:
        """
        # Calculate Formula fixed murabaha estisnaa mugawla ejara gard_hassan Common calculations
        for rec in self:
            #in case extra order add residual from prev approval to total_funding
            rec.total_funding += rec.residual_approval
            if (rec.installment_no != 0):
                payment_period = ((rec.payment_period * 30) + rec.payment_days) / 30
                rec.ins_before_profit = (rec.amount-rec.downpayment)/rec.installment_no
                rec.profit = (rec.payment_period * rec.profit_margin * (rec.approve_amount-rec.downpayment)) / 100
                rec.total_funding = rec.profit + rec.amount-rec.downpayment
                rec.ins_after_profit = rec.total_funding / rec.installment_no
                rec.ins_profit = rec.ins_after_profit - rec.ins_before_profit
            else:
                rec.ins_after_profit = 0
    
            # Calculate Formula mudarba
            if rec.formula in ['mudarba','musharka']:
                rec.org_profit = (rec.org_percentage * rec.expected_profit) / 100
                rec.custumer_profit = (rec.customer_percentage * rec.expected_profit) / 100
    
            # Calculate Formula musharka
            if rec.formula == 'musharka':
                rec.third_profit = (rec.third_percentage * rec.expected_profit) / 100

            # Calculate Formula salam
            if rec.formula == 'salam':
                rec.customer_qty = (rec.customer_percentage * rec.expected_production) / 100
                rec.customer_amount = (rec.expected_price * rec.customer_qty)
                rec.org_qty = (
                              rec.org_percentage * rec.expected_production) / 100  # rec.expected_production - rec.customer_qty
                rec.org_amount = (rec.expected_price * rec.org_qty)

            # Calculate Formula muzaraa
            if rec.formula == 'muzaraa':
                rec.third_qty = (rec.third_percentage * rec.expected_production) / 100
                rec.third_amount = rec.third_qty * rec.expected_price
               
                remaning =  rec.expected_production - rec.third_qty
                rec.org_share = (rec.capital * rec.org_percentage)/100
                rec.org_qty = (rec.org_percentage * remaning) / 100
                rec.org_amount = rec.org_qty * rec.expected_price
                rec.customer_share = (rec.capital * rec.customer_percentage)/100
                rec.customer_qty = (rec.customer_percentage * remaning) / 100
                rec.customer_amount = rec.customer_qty * rec.expected_price 
                rec.approve_amount = rec.org_share
    
            # Calculate Formula dec_murabaha
            if rec.formula == 'dec_murabaha':
                margin_avg = sum(
                    range(rec.grace_period + 1, rec.payment_period + 1)) * rec.profit_margin / rec.installment_no
                rec.ins_profit = margin_avg * (rec.approve_amount - rec.downpayment) / 100 / rec.installment_no
                rec.ins_after_profit = rec.ins_before_profit + rec.ins_profit
                rec.profit = rec.ins_profit * rec.installment_no
                rec.total_funding = rec.ins_after_profit * rec.installment_no


class finance_approval_payment(models.Model):
    _name = "finance.approval.payment"

    name = fields.Char(related='benaficiary_id.name')
    benaficiary_id = fields.Many2one('res.partner',string='Benaficiary', domain=[('supplier','=',True)])
    payment_id = fields.Many2one('account.payment')
    payment_state = fields.Selection(related='payment_id.state')
    ref = fields.Char(String="Payment Ref")
    date = fields.Date(required=True)
    amount = fields.Float(required=True)
    type = fields.Selection([('check','Check'),('cash','Cash'), ('stock','Stock')],required=True)
    state = fields.Selection([('draft','Draft'), ('complete','Complete'),('receive','Receive'),('canceled','Canceled'),('done','Done')],readonly=True,default='draft',required=True)
    approval_id = fields.Many2one('finance.approval')
    print_check_1 = fields.Boolean(default=False)
    print_check_2 = fields.Boolean(default=False)
    print_check_3 = fields.Boolean(default=False)
    print_check_4 = fields.Boolean(default=False)

    @api.constrains('amount')
    def check_amount(self):
        """
        Check Amount If zero rise exceptions
        :return:
        """
        if self.amount == 0:
            raise exceptions.ValidationError(_('Amount Must be Greater Than 0'))
        else:
            return True


    @api.one
    def complete(self):
        """
        Create Account payment and change state to complete
        :return:
        """
        if self.type in ('check','cash'):
            self.payment_id = self.env['account.payment'].create({
                'payment_date':self.date,
                'beneficiary_id': self.benaficiary_id.id,
                'payment_method_id': '',
                'partner_id':  self.approval_id.user_id.partner_id.id,
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'amount': self.amount,
                'communication':  _('Purchase goods for customer'),
                'is_approval' : True,
            })
        self.write({'state': 'complete'})

    @api.one
    def receive(self):
        """
        Check The type and change the workflow
        :return:
        """
        if self.type in ('check','cash') and self.payment_id.state in ('sent','posted'):
            self.write({'state': 'receive'})
        elif self.type == 'stock':
            self.write({'state': 'receive'})

    @api.one
    def done(self):
        """
        Change the state to done if state in receive
        and check all state in payment if it done change state to paid in approval
        :return:
        """
        self.write({'state': 'done'})
        self.check_state()

    @api.constrains('date')
    def check_date(self):
        """
        To ensure that the date of payment must not be greater than visit date
        :return:
        """
        if self.date < self.approval_id.visit_id.date:
            raise exceptions.ValidationError(_("Payment date can not be before visit date"))

    @api.multi
    def check_state(self):
        """
        check all state in payment if it done change state to paid in approval
        :return:
        """
        total_paid = 0
        var = 0
        for record in self.env['finance.approval.payment'].search([('approval_id','=',self.approval_id.id)]):
            if record.state == 'done':
                total_paid += record.amount
            if not record.state == 'done':
                var += 1
                break
        if var == 0:
            approval_record = self.env['finance.approval'].search([('id', '=', self.approval_id.id)])
            if total_paid == approval_record.approve_amount:
                approval_record.write({'state': 'paid'})


class account_abstract_payment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=False, oldname="payment_method")

class AccountPayment(models.Model):
    _inherit = "account.payment"

    beneficiary_id = fields.Many2one('res.partner',string='Beneficiary')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=False,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    portfolio_id = fields.Many2one('finance.portfolio', ondelete='restrict', string="Portfolio Name")
    portfolio = fields.Boolean(string="Portfolio")
    amount_source = fields.Selection([("assets" , "Assets"),("profit" , "Profit")])
    check_amount_in_words_general = fields.Text(string='Check Amount in Words General',compute= '_check_amount_in_words_general')
    check = fields.Integer(compute="_check_compute")
    is_approval = fields.Boolean(default=False)

    @api.onchange('portfolio','amount_source','check','payment_type')
    def set_check(self):
        """
        Set partner_id for funded party
        :return:
        """
        if self.portfolio == True and self.payment_type == 'outbound':
            self.check = 1
        else:
            self.check = 0

    @api.one
    @api.depends('portfolio','amount_source','check','payment_type')
    def _check_compute(self):
        """
        check to show and hide amount source in view
        :return: int
        """
        if self.portfolio == True and self.payment_type == 'outbound':
            self.check = 1
        else :
            self.check = 0

    @api.one
    @api.depends('amount')
    def _check_amount_in_words_general(self):
        """
        If language English then type amount in english text , if arabic write it in Arabic
        :return: Text
        """
        context = self._context or {}
        self.check_amount_in_words_general = amount_to_text_en.amount_to_text(self.amount)
        if context.get('lang') == 'ar_SY':
            self.check_amount_in_words_general = amount_to_text_ar.amount_to_text(self.amount, 'ar')

    @api.onchange('portfolio_id')
    def set_funded_party(self):
        """
        Set partner_id for funded party
        :return:
        """
        res = self.env['res.partner'].search([('id', '=', self.portfolio_id.funded_party.id)])
        self.partner_id = res

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        if self._context.get('default_destination_account_id'):
            self.destination_account_id = self._context.get('default_destination_account_id')
        if self.beneficiary_id:
            self.destination_account_id = self.beneficiary_id.property_account_payable_id.id
        else:
            super(AccountPayment, self)._compute_destination_account_id()


    @api.model
    def create(self, values):
        # amount must not exceed portfolio net if payment for portfolio assets
        if values.get('portfolio',False) and values['amount_source'] == 'assets':
            if values['amount'] > self.env['finance.portfolio'].search([('id','=',values['portfolio_id'])]).real_value:
                raise exceptions.ValidationError(_('Payment Amount Must not exceed the Portfolio net Amount'))
        return super(AccountPayment, self).create(values)


    @api.multi
    def post(self):
        # to set payment for funding party and speculater and others in portfolio payment
        if self.portfolio == True and self.payment_type == 'inbound':
            current_partner_property_account_payable = self.partner_id.property_account_receivable_id
            self.partner_id.property_account_receivable_id = self.portfolio_id.property_account_payable_id


        if self.payment_type != 'inbound':
            if self.portfolio == True:
                if self.payment_type == "outbound" and self.amount_source == 'profit':
                    current_partner_property_account_payable = self.partner_id.property_account_payable_id
                    self.partner_id.property_account_payable_id = self.portfolio_id.profit_suspend_account_id



                
                if self.amount_source == 'assets' and self.payment_type == "outbound":
                    current_partner_property_account_payable = self.partner_id.property_account_payable_id
                    self.partner_id.property_account_payable_id = self.portfolio_id.property_account_payable_id
                    self.portfolio_id.amount_ids = ([(0, 0, {'name': self.amount,
                                                             'date': fields.Datetime.now(),
                                                             'amount_source': 'assets',
                                                             'funded_party': self.amount,
                                                             'speculater': 0,
                                                             'line_name': 'Payback portfolio Amount'})])

                else:
                    self.portfolio_id.amount_ids = ([(0, 0, {'name': self.amount,
                                                             'date': fields.Datetime.now(),
                                                             'amount_source': self.amount_source,
                                                             'funded_party': self.amount * (
                                                                 self.portfolio_id.funded_party_ratio / 100),
                                                             'speculater': self.amount * (
                                                                 self.portfolio_id.speculation_ratios / 100),
                                                             'others': self.amount * (self.portfolio_id.others / 100),
                                                             'line_name': 'Payback portfolio Amount',
                                                             })])
                #self.unlink()
                #return
        super(AccountPayment, self).post()

        if self.portfolio == True and self.payment_type == 'outbound' and self.amount_source == 'profit':
            self.partner_id.property_account_payable_id = current_partner_property_account_payable
            for line in self.move_line_ids:
                if line.name == 'Vendor Payment':
                    line.name = 'Funded Party Portfolio'
        elif self.portfolio == True:
            for line in self.move_line_ids:
                if line.name == 'Vendor Payment':
                    line.name = 'portfolio asset payback'

        if self.amount_source == 'assets' and self.payment_type == "outbound":
            self.partner_id.property_account_payable_id = current_partner_property_account_payable


    @api.one
    def installment_post(self):
        installment_id = self._context.get('installment_id')
        if installment_id:
            installment = self.env['finance.installments'].browse(installment_id)
            approval_id = installment.approval_id

            #constaraint to not let user pay installment before installment above it paid
            if installment.installment_no != 1:
                if self.env['finance.installments'].search([('approval_id','=',approval_id.id),('installment_no','=',installment.installment_no -1)]).state != 'done':
                    raise exceptions.ValidationError(_("Sorry !! you cannot pay installment before installment above get paid"))
            portfolio_id = approval_id.visit_id.order_id.portfolio_id

            portfolio_receivable = portfolio_id.property_account_receivable_id.id
            insurance_account = self.company_id.insurance_account_id.id
            expense_account = self.company_id.expence_account.id
            expected_profit_account = portfolio_id.expected_profit_account_id.id
            profit_account = portfolio_id.profit_account_id.id
            profit_margin_account = portfolio_id.profit_margin_account_id.id

            installment_insurance = approval_id.insurance_amount / approval_id.installment_no
            installment_expense = approval_id.expenses / approval_id.installment_no
            installment_asset = installment.amount_before_profit - installment_expense - installment_insurance

            installment_amount = installment.amount
            asset_perc = installment_asset/installment_amount
            insurance_perc = installment_insurance/installment_amount
            expense_perc = installment_expense/installment_amount
            profit_perc = installment.profit_amount/installment_amount

            installment_ids = self.env['finance.installments'].search([('approval_id','=',installment.approval_id.id),('installment_no','>=',installment.installment_no)])
            total_residual = 0
            amount = self.amount
            for installment in installment_ids:
                installment_residual = installment.residual
                total_residual += installment_residual
                print"installment_residual======",installment_residual
                installment.receive_amount += min(amount,installment_residual)
                if installment.amount<=installment.receive_amount:
                    installment.state='done'
                amount -= installment_residual
                if amount <= 0:
                    break;
            if amount > 0:
                raise UserError(_('You can\'t pay amount greater than total residual amount for your customer'))
            pay_perc = self.amount/total_residual
            asset_pay = total_residual*asset_perc*pay_perc
            insurance_pay = total_residual*insurance_perc*pay_perc
            expense_pay = total_residual*expense_perc*pay_perc
            profit_pay = total_residual*profit_perc*pay_perc

            if not portfolio_receivable:
                raise UserError(_('Kindly specify receivable account for your portfolio in Micro Finance/Portfolio Management/Portfolios'))
            ml = [(0, 6, {'name': _('Installment Payment'),
                          'account_id': self.journal_id.default_credit_account_id.id,
                          'debit': self.amount,
                          'credit': 0,
                          'payment_id': self.id,
                          'partner_id': self.partner_id.id}),
                (0, 6, {'name': _('Paid Asset'),
                        'account_id': portfolio_receivable,
                        'debit': 0.0,
                        'credit': asset_pay,
                        'payment_id': self.id,
                        'partner_id': self.partner_id.id})]
            if profit_pay!=0:
                if not expected_profit_account or not profit_account or not profit_margin_account:
                    raise UserError(_('Kindly specify expected profit account,profit account and profit margin account for your portfolio in Micro Finance/Portfolio Management/Portfolios'))
                ml += [(0,6,{'name': _('Expected Profit'),
                          'account_id': expected_profit_account,
                          'debit': profit_pay,
                          'credit': 0.0,
                          'payment_id': self.id,
                          'partner_id': self.partner_id.id}),
                    (0,6,{'name': _('Real Profit'),
                          'account_id': profit_account,
                          'debit': 0.0,
                          'credit': profit_pay,
                          'payment_id': self.id,
                          'partner_id': self.partner_id.id}),
                    (0, 6, {'name': _('Paid Profit'),
                            'account_id': profit_margin_account,
                            'debit': 0.0,
                            'credit': profit_pay,
                            'payment_id': self.id,
                            'partner_id': self.partner_id.id})]
            if insurance_pay!=0:
                if not insurance_account:
                    raise UserError(_('Kindly specify insurance account for your branch in Accounting/Configuration/Settings'))
                ml += [(0, 6, {'name': _('Paid Insurance'),
                                'account_id': insurance_account,
                                'debit': 0.0,
                                'credit': insurance_pay,
                                'payment_id': self.id,
                                'partner_id': self.partner_id.id})]
            if expense_pay!=0:
                if not expense_pay:
                    raise UserError(_('Kindly specify expense account for your branch in Accounting/Configuration/Settings %s'))
                ml += [(0, 6, {'name': _('Paid Expenses'),
                                'account_id': expense_account,
                                'debit': 0.0,
                                'credit': expense_pay,
                                'payment_id': self.id,
                                'partner_id': self.partner_id.id})]
            move = self.env['account.move'].with_context(check_move_validity=False).create({
                    'date': self.payment_date,
                    'ref': self.communication or '',
                    'company_id': self.company_id.id,
                    'journal_id': self.journal_id.id,
                    'line_ids': ml})
            move.post()
            seq = self.env['ir.sequence'].with_context(ir_sequence_date=self.payment_date).next_by_code('account.payment.customer.invoice')
            self.write({'state': 'posted', 'move_name': move.name,'name':seq})
            if len([i for i in approval_id.installment_ids if i.state!='done'])==0:
                approval_id.state='done'



class AccountMove(models.Model):
    _inherit = 'account.move'

    testprogress = fields.Integer('Progress',default=90)

    @api.model
    def create(self, vals):
        # Override the original create function for the account.move mode
        return models.Model.create(self,vals)

    @api.model
    def write(self, vals):
    	#Override the original write function for the account.move mode
        return models.Model.write(self,vals)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
