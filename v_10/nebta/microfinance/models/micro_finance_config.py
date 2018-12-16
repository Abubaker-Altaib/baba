# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import re
import time
import math

from odoo import api, models, fields, _, exceptions
from odoo.exceptions import UserError, ValidationError

class res_users(models.Model):
    _inherit = 'res.users'

    is_officer = fields.Boolean('Access Nebta Mobile');

class payment_method(models.Model):
    _name = 'finance.payment.method'

    name = fields.Char(string='Name', required=True)
    number_of_days = fields.Integer(string='Number Of Days', required=True)

    @api.model
    def create(self, vals):
        """
        to check if the payment is already exist
        :param vals:
        :return:
        """
        for payment in self.env['finance.payment.method'].search([]):
            if payment.name == vals['name']:
                raise exceptions.ValidationError(_("You already have this payment name"))
        return super(payment_method, self).create(vals)

    @api.multi
    def unlink(self):
        """
        Raise Custom Error
        :return:
        """
        order_ids = self.env['finance.order'].search([])
        for record in order_ids:
            if record.payment_method_ids.id in self.ids:
                raise exceptions.ValidationError(_("You cannot delete that payment. it already linked with an order"))
            elif record.payment_method_ids.id not in self.ids:
                return super(payment_method, self).unlink()


class finance_guarantee_type(models.Model):
    _name = 'finance.guarantee.type'
    
    name = fields.Char(string='Guarantee Name', size=256, required=True)
    code = fields.Integer(string='Code')

    @api.model
    def create(self, vals):
        """
        to check if the guarantee is already exist
        :param vals:
        :return:
        """
        for guarantee in self.env['finance.guarantee.type'].search([]):
            if guarantee.name == vals['name']:
                raise exceptions.ValidationError(_("You already have this Guarantee name"))
        return super(finance_guarantee_type, self).create(vals)

    @api.multi
    def unlink(self):
        """
         to raise custom error when trying to delete
        :return:
        """
        order_ids = self.env['finance.order'].search([])
        for record in order_ids:
            for guarantee in record.guarantee_line_ids:
                if guarantee.id in self.ids:
                    raise exceptions.ValidationError(
                        _("You cannot delete this guarantee. it already linked with an order"))
                elif guarantee.id not in self.ids:
                    return super(finance_guarantee_type, self).unlink()




class finance_sector(models.Model):
    _name = 'finance.sector'
    _description = 'Sector'

    name = fields.Char(string='Name', size=256, required=True)
    seq = fields.Integer(string='Sequence')

    @api.model
    def create(self, vals):
        """
        to check if the sector is already exist
        :param vals:
        :return:
        """
        for employer in self.env['finance.sector'].search([]):
            if employer.name == vals['name']:
                raise exceptions.ValidationError(_("You already have this sector name"))
        return super(finance_sector, self).create(vals)

    @api.multi
    def unlink(self):
        """
        to raise custom error when trying to delete
        :return:
        """
        order_ids = self.env['finance.order'].search([])
        for record in order_ids:
            if record.sector_id.id in self.ids:
                raise exceptions.ValidationError(_("You cannot delete this sector. it already linked with an order"))
            elif record.sector_id.id not in self.ids:
                return super(finance_sector, self).unlink()



class microfinance_identification(models.Model):
    _name = 'finance.identity.type'
    _description = 'Identity Type'

    name = fields.Char(string='ID Type', size=256, required=True)
    code = fields.Integer(string='Code')

    @api.model
    def create(self, vals):
        """
        to check if the identity is already exist
        :param vals:
        :return:
        """
        for identity in self.env['finance.identity.type'].search([]):
            if identity.name == vals['name']:
                raise exceptions.ValidationError(_("You already have this identity type"))
        return super(microfinance_identification, self).create(vals)

    @api.multi
    def unlink(self):
        """
         to raise custom error when trying to delete
        :return:
        """
        unl = 0
        gunl = 0
        partners_id = self.env['res.partner'].search([])
        for identity in partners_id:
            if identity.identity_id in self.ids:
                raise exceptions.ValidationError(_("You cannot delete this ID type. it already linked with a partner"))
            elif identity.identity_id not in self.ids:
                unl += 1
        group_member_id = self.env['finance.group.member'].search([])
        for group_identity in group_member_id:
            if group_identity.identity_type_id in self.ids:
                raise exceptions.ValidationError(_("You cannot delete this ID type. it already linked with a group member"))
            elif group_identity.identity_type_id not in self.ids:
                gunl += 1
        if unl and gunl != 0:
            super(microfinance_identification, self).unlink()


class contry_state(models.Model):
    _inherit = 'res.country.state'

    country_id = fields.Many2one('res.country', string='Country', required=False)
    code = fields.Char(string='Code', help='The state code.', required=False)
    parent_id = fields.Many2one('res.country.state', 'Parent',ondelete='restrict')
    child_ids = fields.One2many('res.country.state', 'parent_id')

    @api.multi
    def unlink(self):
        """
        to raise custom error when trying to delete
        :return:
        """
        order_ids = self.env['finance.order'].search([])
        for order in order_ids:
            if order.state_id.id in self.ids:
                raise exceptions.ValidationError(_("You Cannot delete a local state. that already linked with order"))
            elif order.state_id.id not in self.ids:
                return super(contry_state, self).unlink()


class income_resources_type(models.Model):
    _name = 'income.resources.type'
    _description = "Personal Income Resources Type"

    name = fields.Char(string='Resource Type', required=True)
    code = fields.Char(string='Code')

    @api.model
    def create(self, vals):
        """
        to check if the income is already exist
        :param vals:
        :return:
        """
        for income in self.env['income.resources.type'].search([]):
            if income.name == vals['name']:
                raise exceptions.ValidationError(_("You already have this Income Resources Type"))
        return super(income_resources_type, self).create(vals)

    @api.multi
    def unlink(self):
        """
        to raise custom error when trying to delete
        :return:
        """
        individual_id = self.env['finance.individual.order'].search([])
        for ind in individual_id:
            for income in ind:
                if income.id in self.ids:
                    raise exceptions.ValidationError(
                        _("You cannot delete this income resources. it already linked with an Individual order"))
                elif income.id not in self.ids:
                    return super(income_resources_type, self).unlink()





class micro_finance_employer(models.Model):
    _name = 'micro.finance.employer'
    _description = "Micro-finance Employer"

    name = fields.Char(string='Employer Name', required=True)
    code = fields.Char(string='Code')

    @api.model
    def create(self, vals):
        """
        to check if the employer is already exist
        :param vals:
        :return:
        """
        for employer in self.env['micro.finance.employer'].search([]):
            if employer.name == vals['name']:
                raise exceptions.ValidationError(_("You already have this employer name"))
        return super(micro_finance_employer, self).create(vals)

    @api.multi
    def unlink(self):
        """
        to raise custom error when trying to delete
        :return:
        """
        partner_id = self.env['res.partner'].search([])
        for employer in partner_id:
            if employer.id in self.ids:
                raise exceptions.ValidationError(
                    _("You cannot delete this employer. it already linked with an partner"))
            elif employer.id not in self.ids:
                return super(micro_finance_employer, self).unlink()


class finance_product(models.Model):
    _name = "finance.product"
    _description = "Finance Product"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        link sector in product with a sector in order
        """
        company_id = self.env.user.company_id.id
        if self._context.get('order_id'):
            for order_sector_id in self.env['finance.order'].search([('id', '=', self._context.get('order_id'))]):
                ids = order_sector_id.sector_id.id
            product_ids = [product.id for product in self.search([])
                           if ids in product.sector_ids.ids and company_id not in product.company_ids.ids]
            args.append(('id', 'in', product_ids))
        return super(finance_product, self).name_search(name=name, args=args, operator=operator, limit=limit)

    name = fields.Char(string="Name", required=True, size=256)
    description = fields.Text(string="Description", required=True)
    project_ids = fields.One2many("finance.project", "product_id", string="Projects")
    sector_ids = fields.Many2many('finance.sector', 'finance_product_sector_rel', 'product_id', 'sector_id',
                                  string='Sector')
    company_ids = fields.Many2many('res.company', string="Prevented Branches")
    active = fields.Boolean(default=True)
    overdrow = fields.Boolean(string="Overdrow")
    state=fields.Selection([('draft', 'Draft'), ('request', 'Request'),('approve', 'Approved')],default='draft')

    @api.constrains('name', 'description')
    def check_name_description(self):
        """
        check if the name and description contain a white space
        :return:
        """
        white_space = re.compile(r'^\s')
        if white_space.search(self.name) or white_space.search(self.description):
            raise exceptions.ValidationError(_("cannot accept blank space you must enter real data..!!"))

    @api.multi
    def unlink(self):
        """
        check if the product is linked to a visit if not the product will be removed
        with it's project
        :return:
        """
        visit_ids = self.env['finance.visit'].search([('product_id.id', 'in', self.ids)])
        if visit_ids:
            raise exceptions.ValidationError(_("this product cannot be deleted. it already linked with an order"))
        elif not visit_ids:
            self.project_ids.unlink()
            return super(finance_product, self).unlink()
    @api.model
    def create(self, vals):
        product_ids = self.env['finance.product'].search([])
        for product in product_ids:
            if product.name == vals['name']:
                raise exceptions.ValidationError(_("this product is already exist"))
        return super(finance_product, self).create(vals)

    @api.multi
    def action_draft(self):
        """
        Change State to draft
        :return:none
        """
        return self.write({'state': 'draft'})

    @api.multi
    def action_request(self):
        """
        Change State to request
        :return:none
        """
        return self.write({'state': 'request'})

    @api.multi
    def action_approve(self):
        """
        Change State to approve
        :return:none
        """
        return self.write({'state': 'approve'})


    @api.constrains('project_ids')
    def _req_project_ids(self):
        print "<<<<<<<<<<<<<<<<<<<<<<<<<", self.project_ids

class finance_project(models.Model):
    _name = "finance.project"
    _description = "Finance Project"


    name = fields.Char(string="Name", required=True, size=256)
    celling = fields.Float(string='Financing Ceiling', required=True)
    individual=fields.Boolean(string='Individual')
    group=fields.Boolean(string='Group')
    min_member = fields.Integer(string="Min Member", default=1, required=True)
    max_member = fields.Integer(string="Max Member", default=1, required=True)
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
    profit_margin = fields.Float(string='Profit Margin', required=True)
    installment_no = fields.Integer(string="No of Installments", required=True)
    grace_period = fields.Integer(string="Grace Period", required=True)
    payment_period = fields.Integer(string="Payment Period", compute='_get_payment_period', required=True)
    payment_days = fields.Integer(string="Payment Days", compute='_get_payment_period', required=True)
    payment_method_id = fields.Many2one('finance.payment.method', string="Payment Method",ondelete='restrict')
    product_id = fields.Many2one('finance.product', string='Project', required=True,ondelete='restrict')
    payment_period_month = fields.Integer(compute='_get_payment_period')
    overdrow = fields.Boolean(string="Overdrow")

    @api.constrains('name')
    def check_name_description(self):
        """
        check if the name contain a white space
        :return:
        """
        white_space = re.compile(r'^\s')
        if white_space.search(self.name):
            raise exceptions.ValidationError(_("cannot accept blank space you must enter real data..!!"))

    @api.constrains('celling', 'profit_margin', 'max_member', 'min_member', 'grace_period','installment_no')
    def check_fields(self):
        """
        To check a specific fields value
        :return:
        """
        if self.max_member <= 0 or self.max_member < self.min_member:
            raise exceptions.ValidationError(_("max member cannot be less than zero or min member"))
        if self.min_member <= 0 or self.min_member > self.max_member:
            raise exceptions.ValidationError(_("max member cannot be less than zero or greater than max member"))
        if self.celling <= 0:
            raise exceptions.ValidationError(_("celling cannot be zero or less"))
        if self.profit_margin < 0:
            raise exceptions.ValidationError(_("profit margin cannot be less than zero"))
        if self.grace_period < 0:
            raise exceptions.ValidationError(_("grace period cannot be less than zero"))
        if self.installment_no <= 0:
            raise exceptions.ValidationError(_("installment number cannot be zero or less"))

    @api.model
    def create(self, vals):
        """
        To check if this project is already exist in this product
        :return:
        """
        product_ids = self.env['finance.product'].search([('id', '=', vals['product_id'])])
        for product in product_ids.project_ids:
            if product.name == vals['name']:
                raise exceptions.ValidationError(_("this project is already exist!!!"))
        return super(finance_project, self).create(vals)

    @api.constrains('individual', 'group')
    def check_selection(self):
        """
        To check if the user select one of the following fields
        :return:
        """
        if self.individual == False and self.group == False:
            raise exceptions.ValidationError(_('You must select individual or group in project'))

    @api.multi
    @api.onchange('formula_clone', 'murabaha_selection')
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



    @api.depends('payment_method_id.number_of_days', 'installment_no','grace_period')
    def _get_payment_period(self):
        """
        
        """
        self.payment_period_month = self.payment_method_id.number_of_days /30
        self.payment_period = (self.payment_method_id.number_of_days * self.installment_no)/30+self.grace_period
        self.payment_days = (self.payment_method_id.number_of_days * self.installment_no)%30

    @api.onchange('formula')
    def _onchange_formula(self):
        if self.formula in ['gard_hassan','salam','mudarba','muzaraa','musharka']:
            self.profit_margin = 0
            if self.formula != 'gard_hassan':
                self.installment_no = 1
                self.payment_method_id = False
        
###################################
#
# Finance Crop
#
###################################

class finance_crop(models.Model):
    _name = 'finance.crop'

    name = fields.Char(string="Name", required=True)
    uom_id = fields.Many2one('product.uom', string="Unit of Measure", require=True, ondelete='restrict')

    @api.multi
    def unlink(self):
        """
        :return:
        """
        order_ids = self.env['finance.order'].search([])
        for order in order_ids:
            if order.crop_id.id in self.ids:
                raise exceptions.ValidationError(_("You cannot delete this crop. it already linked to an order"))
            elif order.crop_id.id not in self.ids:
                return super(finance_crop, self).unlink()

    @api.model
    def create(self, vals):
        """
        to check if the crop is already exist
        :param vals:
        :return:
        """
        for crop in self.env['finance.crop'].search([]):
            if crop.name == vals['name']:
                raise exceptions.ValidationError(_("You already have this crop name"))
        return super(finance_crop, self).create(vals)


class res_company(models.Model):
    _inherit = 'res.company'

    br_ceiling = fields.Integer(string="Branch manager ceiling")
    op_ceiling = fields.Integer(string="Operational manager ceiling")
    por_gm_ceiling = fields.Integer(string="General-Manager ceiling")
    por_op_ceiling = fields.Integer(string="Operational-manager ceiling")
    journal_id = fields.Many2one('account.journal', 'Financing Journal', domain=[('type','=','sale')])
    company_current_account_id = fields.Many2one('account.account', string="Current account")
    counsel_character = fields.Char(string="Counsel Character")
    counsel = fields.Char(string="Counsel")
    insurance_account_id = fields.Many2one('account.account',string="Insurance Account")
    expence_account = fields.Many2one('account.account',string="Expences Account")
    stock_account_id = fields.Many2one('account.account',string="Stock Account")


####################################
#
# Wizard finance settings
#
#####################################

class finance_settings(models.TransientModel):
    #_inherit = 'res.config.settings'
    _name = 'finance.settings'

    company_id = fields.Many2one('res.company', string="Company",required=True,
                                 default=lambda self: self.env.user.company_id)
    br_ceiling = fields.Integer(string="Branch-Manager ceiling")
    op_ceiling = fields.Integer(string="Operational-manager ceiling")
    por_gm_ceiling = fields.Integer(string="General-Manager ceiling")
    por_op_ceiling = fields.Integer(string="Operational-manager ceiling")
    counsel_character = fields.Char(string="Counsel Character")
    counsel = fields.Char(string="Counsel")
    parent_id = fields.Many2one(related="company_id.parent_id")


    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        self.br_ceiling = company.br_ceiling
        self.op_ceiling = company.op_ceiling
        self.counsel_character = company.counsel_character
        self.counsel = company.counsel
        self.por_gm_ceiling = company.por_gm_ceiling
        self.por_op_ceiling = company.por_op_ceiling

    @api.one
    def set_company_values(self):
        company = self.company_id
        company.br_ceiling = self.br_ceiling
        company.op_ceiling = self.op_ceiling
        company.por_op_ceiling = self.por_op_ceiling
        company.por_gm_ceiling = self.por_gm_ceiling
        company.counsel = self.counsel
        company.counsel_character = self.counsel_character


    @api.multi
    def cancel(self):
        # ignore the current record, and send the action to reopen the view
        actions = self.env['ir.actions.act_window'].search([('res_model', '=', self._name)], limit=1)
        if actions:
            return actions.read()[0]
        return {}



######################################
#
#  Accounting inheritance settings
#
######################################

class AccountCnfigCustom(models.TransientModel):
    _inherit = 'account.config.settings'


    journal_id = fields.Many2one('account.journal', 'Financing Journal')
    company_current_account_id = fields.Many2one('account.account', string="Current account",
                                                 domain="[('company_id','=',company_id),('deprecated', '=', False)]")

    insurance_account_id = fields.Many2one('account.account',string="Insurance Account")
    expence_account = fields.Many2one('account.account',string="Expences Account")
    stock_account_id = fields.Many2one('account.account',string="Stock Account")


    @api.onchange('company_id')
    def get_company_values(self):

        self.journal_id = False
        if self.company_id:
            company = self.company_id
            self.journal_id = company.journal_id
            self.insurance_account_id = company.insurance_account_id
            self.expence_account = company.expence_account
            self.stock_account_id = company.stock_account_id


    @api.one
    def set_company_values(self):
        company = self.company_id
        company.journal_id = self.journal_id
        company.insurance_account_id = self.insurance_account_id
        company.expence_account = self.expence_account
        company.stock_account_id = self.stock_account_id

############################################
#  Custom Chart of Accounts
#
############################################

class CustomAccountAccount(models.Model):
    _inherit = 'account.account'

    companys = fields.Selection([('all_company', 'All Company'), ('specified', 'Specified Companies')], string="For")
    company_ids = fields.Many2many('res.company', string='Company', required=False,
                                 default=False)
    active = fields.Boolean('Active', default=True)


    @api.model
    def create(self, vals):
        """
        modify create to create multi account for all branch if user select all_company
        else create on account for a specific branch
        :param vals:
        :return:
        """
        new_name = []
        company_id = []
        # if user select all companies
        if vals['companys'] == 'all_company':
            company_ids = self.env['res.company'].search([])
            for company in company_ids:
                if company.parent_id:
                    new_name.append(vals['name'] + ' ' + company.name)
                    company_id.append(company.id)
            for code in range(len(new_name)):
                vals.update({'name': new_name[code],'company_id': company_id[code]})
                res_id = super(CustomAccountAccount, self).create(vals)
            return res_id

        # if user selecte a spcific company
        if vals['companys'] == 'specified':
            for company in vals['company_ids'][0][2]:
                company_id.append(company)
            company_ids = self.env['res.company'].search([('id', 'in', company_id)])
            for company in company_ids:
                if company.parent_id:
                    new_name.append(vals['name'] + ' ' + company.name)
            for code in range(len(new_name)):
                vals.update({'name': new_name[code],'company_id': company_id[code]})
                res_id = super(CustomAccountAccount, self).create(vals)
            return res_id

        return super(CustomAccountAccount, self).create(vals)

#  vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

