# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
import re


class finance_Transfer_Customer_wiz(models.TransientModel):
    _name = "finance.transfer.customer.wiz"
    _description = "Transfer Customer"

    @api.multi
    @api.onchange('change_type','new_company_id')
    def officer_domain(self):
        """
        To return user that have officer group only
        :return:
        """
        ids = []
        if self.change_type == 'officer':
            ids = []
            for user in self.env['res.users'].search([('company_id', '=', self.user_id.company_id.id)]):
                for group in user.groups_id:
                    if (group.name == "Officer" and group.category_id.name == "Financing") \
                            or (group.name == "اخصائي التمويل".decode('utf-8','ignore')
                            and group.category_id.name == "التمويل".decode('utf-8', 'ignore')):
                        ids.append(user.id)
            return {'domain': {'new_user_id': [('id', 'in', ids), ('id', '!=', self.user_id.id)]}}
        elif self.change_type == 'branch':
            ids = []
            if self.new_company_id:
                for user in self.sudo().env['res.users'].sudo().search([('company_id', '=', self.new_company_id.id)]):

                    for group in user.groups_id:
                        if (group.name == "Officer" and group.category_id.name == "Financing") \
                                or (group.name == "اخصائي التمويل".decode('utf-8', 'ignore')
                                and group.category_id.name == "التمويل".decode('utf-8', 'ignore')):
                            ids.append(user.id)
                return {'domain': {'new_user_id': [('id', 'in', ids)]}}

    @api.multi
    @api.onchange('change_type')
    def company_chcek(self):
        """
        To treturn Company not in company_id
        :return:
        """
        ids = []
        for company in self.env['res.company'].search([('id', '!=', self.company_id.id)]):
            ids.append(company.id)
        return {
            'domain': {
                'new_company_id': [('id', 'in', ids)]
            }
        }


    change_type = fields.Selection([('officer','Officer'),('branch','Branch')])
    partner_id = fields.Many2one('res.partner', string='Customer',  default=lambda self: self._context.get('partner_id'),ondelete='restrict', required=True)

    user_id = fields.Many2one('res.users', string="Current Officer", default=lambda self: self._context.get('user_id')
                              , readonly=True,required=True, ondelete='restrict')
    new_user_id = fields.Many2one('res.users', string="New Officer",ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Current Branch", default=lambda self: self._context.get('company_id'),
                              readonly=True,  ondelete='restrict')
    new_company_id = fields.Many2one('res.company', string="New Branch", ondelete='restrict')


    def action_transfer(self):
        """
        Desc : Transfer Customer
        :return:
        """

        if self.change_type == 'officer':
            if self.user_id == self.new_user_id:
                raise exceptions.ValidationError(_('You cannot Transfer Customer to same Officer '))

            for order in self.env['finance.order'].search([('partner_id','=',self.partner_id.id)]):
                order.user_id = self.new_user_id
                for visit in  self.env['finance.visit'].search([('order_id','=',order.id)]):
                    visit.user_id = self.new_user_id
                for approval in self.env['finance.approval'].search([('visit_id.order_id','=',order.id)]):
                    approval.user_id = self.new_user_id

            for group in self.env['finance.group'].search([('partner_id','=',self.partner_id.id)]):
                group.user_id = self.new_user_id
            self.sudo().partner_id.sudo().user_id = self.sudo().new_user_id

        elif self.change_type == 'branch':
            if self.company_id == self.new_company_id:
                raise exceptions.ValidationError(_('You cannot Transfer Customer to same Branch '))


            orders = self.env['finance.order'].search([('partner_id', '=', self.partner_id.id)])
            for order in orders:
                for approve in order.approve_ids:
                    if approve.state != 'done' and approve.state != 'canceled':
                        raise exceptions.ValidationError(_(
                            'Customer Cannot be transfered because There are approval already not compeleted yet'))
            for group in self.env['finance.group'].search([('partner_id','=',self.partner_id.id)]):
                group.user_id = self.new_user_id
                group.company_id = self.new_company_id
            self.sudo().partner_id.sudo().user_id = self.sudo().new_user_id
            self.sudo().partner_id.sudo().company_id = self.sudo().new_company_id






class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = "create_date desc"


    #name = fields.Char(string="Full Name")
    code =fields.Char(string='Code', readonly=True)
    #display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    ar_first_name = fields.Char(string='First Name', track_visibility='onchange')
    ar_second_name = fields.Char(string='Second Name', track_visibility='onchange')
    ar_third_name = fields.Char(string='Third Number', track_visibility='onchange')
    ar_forth_name = fields.Char(string='Forth Number', track_visibility='onchange')
    eng_first_name = fields.Char(string='First Name')
    eng_second_name = fields.Char(string='Second Name')
    eng_third_name = fields.Char(string='Third Number')
    eng_forth_name = fields.Char(string='Forth Number')
    address_description = fields.Text(string="Address Description")
    neighborhood = fields.Char(string='Neighborhood')
    home_number = fields.Char(string='Home Number', size=256)
    address_type = fields.Selection([('owned', 'Owned'), ('rented', 'Rented'), ('hosted', 'Hosted'),
                                     ('others', 'Others')], string='Address Type')
    identity_id = fields.Many2one('finance.identity.type', string='Identity Type', ondelete='cascade', track_visibility='onchange')
    identity_number = fields.Char(string='ID Number', track_visibility='onchange')
    identity_date = fields.Date(string='Date Of The Issuance')
    identity_location = fields.Char(string='Location Of The Issuance')
    identity_exp_date = fields.Date(string='Expiration Date')
    identity_country = fields.Char(string='Country Of The Issuance')
    place_of_birth = fields.Char(string='Place Of Birth')
    date_of_birth = fields.Date(string='Date Of Birth')
    mobile = fields.Char(string='Phone2')
    phone3 = fields.Char(string='Phone3')
    fame_name = fields.Char(index=True, string='Fame Name')
    mother_name = fields.Char(index=True, string='Mother Name')
    social_status = fields.Selection([('married', 'Married'), ('single', 'Single'), ('widowed', 'Widowed'),
                                      ('abandoned', 'Abandoned')], string='Social Status')
    sbouse_name = fields.Char(string='Sbouse Name')
    education_level = fields.Selection([('illiterate', 'Illiterate'), ('first', 'First'), ('average', 'Average'), ('high', 'High'),
                                    ('university', 'University'), ('postgraduate studies', 'Postgraduate Studies')],string='Education Level')
    number_of_wives = fields.Integer(string='Number Of Wives')
    number_of_children = fields.Integer(string='Number Of Children')
    number_of_parents = fields.Integer(string='Number Of Parents')
    number_of_sibling = fields.Integer(string='Number Of Sibling')
    others = fields.Integer(string='Others')
    type = fields.Selection([('home', 'Home Address'), ('work', 'Work Address')], string='Address Type', default='home')
    individual = fields.Boolean("Individual Customer?")
    number_of_wives = fields.Integer(string='Number Of Wives')
    number_of_children = fields.Integer(string='Number Of Children')
    number_of_parents = fields.Integer(string='Number Of Parents')
    number_of_sibling = fields.Integer(string='Number Of Sibling')
    others = fields.Integer(string='Others')
    #employer = fields.Char(string='Employer',required=True)
    employer_id = fields.Many2one('micro.finance.employer', string='Employer', track_visibility='onchange')
    type = fields.Selection([('home', 'Home Address'), ('work', 'Work Address')], string='Address Type', default='home')
    user_id = fields.Many2one('res.users', string="Officer", default=lambda self: self.env.user, readonly=True,
                              required=True, ondelete='restrict')
    individual = fields.Boolean("Individual Customer?")
    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    customer_name_exist = fields.Integer('Customer Name Exist', default=0, readonly=1)
    customer_info_exist = fields.Integer('Customer Info Exist', default=0, readonly=1)
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable", oldname="property_account_payable",
        domain="[('internal_type', 'in', ('payable','receivable')), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable", oldname="property_account_receivable",
        domain="[('internal_type', 'in', ('payable','receivable')), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True)

    @api.constrains('number_of_wives')
    def check_wives(self):
        """
        check if social_status is married number must be more than zero
        :return:
        """
        if self.social_status == 'married' and self.number_of_wives == 0:
            raise exceptions.ValidationError(_('Number of wives must be greater than zero'))


    @api.constrains('identity_exp_date', 'identity_date', 'date_of_birth')
    def check_date(self):
        """
        check date of identity and birth date
        :return:
        """
        if self.identity_exp_date <= self.identity_date:
            raise exceptions.ValidationError(_('The expire date must be greater than production date'))
        birth_date = datetime.strptime(self.date_of_birth, '%Y-%m-%d')
        now = datetime.now()
        if birth_date.year >= now.year:
            raise exceptions.ValidationError(_('Birth date must be less than this date'))


    @api.multi
    def unlink(self):
        """
        raise custom error whene delete
        :return:
        """
        order_ids = self.env['finance.order'].search([])
        for order in order_ids:
            if order.partner_id.id in self.ids:
                raise exceptions.ValidationError(_("you cannot delete customer. that have order"))
            elif order.partner_id.id not in self.ids:
                return super(ResPartner, self).unlink()

    @api.multi
    def action_customer_transfer(self):
        ###### to open Customer Transfer Wizard ######

        view_ref = self.env['ir.model.data'].get_object_reference('microfinance', 'finance_transfer_customer_wiz_view')
        view_id = view_ref and view_ref[1] or False,

        ###### context to send data from this record to cusomer transfer wizard #######
        return {
            'type': 'ir.actions.act_window',
            'name': _('Customer Transfer'),
            'res_model': 'finance.transfer.customer.wiz',
            'context': {'user_id': self.user_id.id,
                        'company_id': self.user_id.company_id.id,
                        'partner_id':self.id},
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
        }


    @api.model
    def create(self, values):
        if values.has_key('ar_first_name'):
            for customer in self.env['res.partner'].search([('identity_id','=',values.get('identity_id', False)),
                                                            ('identity_number','=',values.get('identity_number', False)),
                                                            ('employee_id','=',values.get('employer_id', False))]):
                # cutomer_ar_exists = 50
                raise exceptions.ValidationError(_('Customer Already exists'))

            for customer in self.env['res.partner'].search([('ar_first_name', '=',values.get('ar_first_name', False)),
                                                            ('ar_second_name', '=',values.get('ar_second_name', False)),
                                                            ('ar_third_name', '=',values.get('ar_third_name', False) ),
                                                            ('ar_forth_name', '=',values.get('ar_forth_name', False)),
                                                            ('eng_first_name', '=',values.get('eng_first_name', False) ),
                                                            ('eng_second_name', '=',values.get('eng_second_name', False) ),
                                                            ('eng_third_name', '=',values.get('eng_third_name', False) ),
                                                            ('eng_forth_name', '=',values.get('eng_forth_name', False) ),
                                                            ('mother_name','=', values.get('mother_name', False))]):
                raise exceptions.ValidationError(_('Customer Already exists'))



        if values.get('name', False) == False:
            values['name'] = values.get('ar_first_name', '') + ' ' + values.get('ar_second_name', '') + ' ' \
                             + values.get('ar_third_name', '') + ' ' + values.get('ar_forth_name', '')
        # set new sequence number in code for every new record
        values['code'] = self.env['ir.sequence'].next_by_code('customer_code')
        return super(ResPartner, self).create(values)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=1000):
        """
        Desc : Function to make user search for customer based on name or customer code
        :param name: (Text) what user want to search about
        :return:
        """
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|',('name', operator, name),('code', operator , name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.depends('name','code')
    def _compute_display_name(self):
        """
        To help in search to search with code and name in the same time
        :return:
        """
        names = dict(self.with_context().name_get())
        for customer in self:
            customer.display_name = names.get(customer.id)

    @api.multi
    def name_get(self):
        """
        Desc : To display record in view as (Sequence(code) - Customer Full Name)
        :return:
        """
        return [(customer.id, '%s - %s ' % (customer.code, customer.name)) for customer in self]

    @api.constrains('ar_first_name', 'ar_second_name', 'ar_third_name', 'ar_forth_name', 'ar_third_name',
                    'ar_forth_name', 'eng_first_name', 'eng_second_name', 'eng_third_name', 'eng_forth_name',
                    'fame_name', 'mother_name', 'neighborhood', 'identity_country', 'place_of_birth',
                    'address_description', 'identity_location')
    def check_name_field(self):
        """
        use regex to check if name fields have a wrong value
        :return:
        """
        num_pattern = re.compile(r'\d', re.I | re.M)
        white_space = re.compile(r'^\s')
        if num_pattern.search(self.ar_first_name):
            raise exceptions.ValidationError(_('there are numbers in first name check it'))
        if num_pattern.search(self.ar_second_name):
            raise exceptions.ValidationError(_('there are numbers in second name check it'))
        if num_pattern.search(self.ar_third_name):
            raise exceptions.ValidationError(_('there are numbers in third name check it'))
        if num_pattern.search(self.ar_forth_name):
            raise exceptions.ValidationError(_('there are numbers in forth name check it'))
        if num_pattern.search(self.eng_first_name):
            raise exceptions.ValidationError(_('there are numbers in first name check it'))
        if num_pattern.search(self.eng_second_name):
            raise exceptions.ValidationError(_('there are numbers in second name check it'))
        if num_pattern.search(self.eng_third_name):
            raise exceptions.ValidationError(_('there are numbers in third name check it'))
        if num_pattern.search(self.eng_forth_name):
            raise exceptions.ValidationError(_('there are numbers in forth name check it'))
        if num_pattern.search(self.fame_name):
            raise exceptions.ValidationError(_('there are numbers in fame name check it'))
        if num_pattern.search(self.mother_name):
            raise exceptions.ValidationError(_('there are numbers in mother name check it'))
        if num_pattern.search(self.identity_country):
            raise exceptions.ValidationError(_('there are numbers in identity country name check it'))
        if white_space.search(self.ar_first_name):
            raise exceptions.ValidationError(_('there is blank space in first name check it'))
        if white_space.search(self.ar_second_name):
            raise exceptions.ValidationError(_('there is blank space in second name check it'))
        if white_space.search(self.ar_third_name):
            raise exceptions.ValidationError(_('there is blank space in third name check it'))
        if white_space.search(self.ar_forth_name):
            raise exceptions.ValidationError(_('there is blank space in forth name check it'))
        if white_space.search(self.eng_first_name):
            raise exceptions.ValidationError(_('there is blank space in first name in english check it'))
        if white_space.search(self.eng_second_name):
            raise exceptions.ValidationError(_('there is blank space in second name in english check it'))
        if white_space.search(self.eng_third_name):
            raise exceptions.ValidationError(_('there is blank space in third name in english check it'))
        if white_space.search(self.eng_forth_name):
            raise exceptions.ValidationError(_('there is blank space in forth name in english check it'))
        if white_space.search(self.fame_name):
            raise exceptions.ValidationError(_('there is blank space in fame name in english check it'))
        if white_space.search(self.mother_name):
            raise exceptions.ValidationError(_('there is blank space in mother name in english check it'))
        if white_space.search(self.identity_country):
            raise exceptions.ValidationError(_('there is blank space in identity country name check it'))
        if white_space.search(self.identity_location):
            raise exceptions.ValidationError(_('there is blank space in identity location name check it'))
        if white_space.search(self.neighborhood):
            raise exceptions.ValidationError(_('there is blank space in neighborhood name check it'))
        if white_space.search(self.place_of_birth):
            raise exceptions.ValidationError(_('there is blank space in place of birth check it'))
        if white_space.search(self.address_description):
            raise exceptions.ValidationError(_('there is blank space in address description check it'))

    @api.constrains('eng_first_name', 'eng_second_name', 'eng_third_name', 'eng_forth_name')
    def eng_check(self):
        """
        Check if english name is in english
        :return:
        """
        eng = re.compile(r'[A-zA-Z]', re.I | re.M)
        if not eng.search(self.eng_first_name) or not eng.search(self.eng_second_name) or \
           not eng.search(self.eng_third_name) or not eng.search(self.eng_forth_name):
            raise exceptions.ValidationError(_("Please Enter the name in English"))

    @api.constrains('phone', 'mobile', 'phone3', 'identity_number','home_number')
    def checks(self):
        """
        Desc:Check format Phones and ID Numbers
        :return:
        """
        # Regex pattern to check all chars are integers
        pattern = re.compile(r'^[0]\d{9,9}$')
        pattern2 = re.compile(r'\d{6,50}$')
        pattern3 = re.compile(r'\d[0-4]$')
        if self.phone != False:
            if not pattern.search(self.phone):
                raise exceptions.ValidationError(_('Phone 1 must be exactly 10 Numbers and Start with ZERO 0 .'))

        if self.mobile != False:
            if not pattern.search(self.mobile):
                raise exceptions.ValidationError(_('Phone 2 must be exactly 10 Numbers and Start with ZERO 0 .'))

        if self.phone3 != False:
            if not pattern.search(self.phone3):
                raise exceptions.ValidationError(_('Phone 3 must be exactly 10 Numbers and Start with ZERO 0 .'))

        if self.identity_number != False:
            if not pattern2.search(str(self.identity_number)):
                raise exceptions.ValidationError(_('ID Number must be at least 6 Numbers.'))

        if self.home_number != False:
            if len(self.home_number) > 4 or len(self.home_number) < 1:
                raise exceptions.ValidationError(_("The home number must be at least 1 to 4 Numbers."))


class finance_individual_order(models.Model):
    _name = 'finance.individual.order'
    _inherits = {'finance.order': 'order_id'}
    _order = "create_date desc"
    _description = 'Finance Individual Order'

    order_id = fields.Many2one('finance.order')
    name = fields.Char(string='Order Number', required=True, copy=False, readonly=True,
                               default=lambda self: self._get_seq_finance_order_to_view())
    CBOS_id = fields.Char(string='CBOS', size=125)
    project_ownership = fields.Selection([('ownered', 'Ownered'), ('rented', 'Rented'), ('hosted', 'Hosted'),
                                          ('others', 'Others')], string='Place  Of Ownership', required=True)
    legal_situation = fields.Selection([('registered', 'Registered'), ('not_registered', 'Not-Registered')],
                                       string='Legal Situation')
    registration_place = fields.Char(string='Registration Place', size=256)
    registration_number = fields.Integer(string='Registration Number')

    years_of_experiance = fields.Integer(string='Years Of Experience', required=True)
    # number_of_workers = fields.Selection([('from_family','From Family'), ('out_of_family','Out of family'), ('all','All')], string='Number of Workers')
    from_family = fields.Integer(string='Workers from Family', required=True)
    out_of_family = fields.Integer(string='Workers out of Family', required=True)
    both_all = fields.Integer(string='All Workers', compute="_compute_total_workers", required=True)
    income_resources_ids = fields.One2many('income.resources', 'finance_order_id', string='Income Resources', required=True)
    total_income = fields.Monetary(string='Total Income', store=True, compute='_amount_all', currency_field='company_currency_id')
    net_profite_avg = fields.Monetary(string='Net Profit Avg.', currency_field='company_currency_id',readonly=True)
    net_income = fields.Monetary(string='Net Income', compute='_amount_all', currency_field='company_currency_id')
    expenditure_avg = fields.Monetary(string='Expenditure Avg.', currency_field='company_currency_id',readonly=True)
    net_surplus = fields.Monetary(string='Net Surplus', compute='_amount_all', currency_field='company_currency_id')
    payment_period = fields.Integer('Payment Period')
    funding_period = fields.Integer(string='Funding Period',related="order_id.funding_period")
    description = fields.Text(string="Description")

    @api.multi
    @api.onchange('formula_clone', 'murabaha_selection')
    def _formual_clone_set(self):
        """
        Desc: set Formula from formula clone in Formula Fields
        :return:
        """
        if (
                self.formula_clone == 'murabaha' or self.formula_clone == 'buying_murabaha') and self.murabaha_selection == 'fixed_murabaha':
            self.formula = 'fixed_murabaha'
        elif (
                self.formula_clone == 'murabaha' or self.formula_clone == 'buying_murabaha') and self.murabaha_selection == 'dec_murabaha':
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

    @api.onchange('payment_method_ids', 'installments_number')
    def get_funding_period(self):
        """
        Desc : Same function in finance.order with slice change from @depends to @api.onchange
        :return:
        """
        self.funding_period, self.funding_period_day = divmod(
            (self.payment_method_ids.number_of_days * self.installments_number), 30)


    @api.constrains('income_resources_ids','net_surplus','net_profite_avg')
    def _check_net_surplus_not_negative(self):
        """
        Desc: Net Surplust Must not be negative
        :return:
        """
        if(self.net_surplus < 0):
            raise exceptions.ValidationError(_("Net Surplus must not be Negative %s") % (self.net_surplus))

    @api.constrains('income_resources_ids')
    def _check_income(self):
        """
        Desc : Check have at least one income
        :return:
        """
        if len(self.income_resources_ids) == 0:
            raise exceptions.ValidationError(_('Must have Income .'))

    @api.multi
    def unlink(self):
        self.order_id.unlink()

    @api.multi
    def act_visit_confirm(self):
        return self.order_id.act_visit_confirm(self.name)

    @api.multi
    def act_su_recommend(self):
        return self.order_id.act_su_recommend()

    @api.multi
    def act_br_recommend(self):
        return self.order_id.act_br_recommend()

    @api.multi
    def act_op_recommend(self):
        return self.order_id.act_op_recommend()

    @api.multi
    def act_approved(self):
        all_amount = 0
        for approval in self.order_id.approve_ids:
            all_amount += approval.approve_amount
        if self.portfolio_id.real_value < all_amount:
            raise exceptions.ValidationError(_('Can\'t be Approved because Approve amount More Than Portfolio Amount.'))
        if(self.order_id.approve_ids.approve_amount > self.order_id.approve_ids.project_id.celling):
            raise exceptions.ValidationError(_('Can\'t be Approved if Approve Amount in Approval'
                                               ' more than Celling In Project.'))
        return self.order_id.act_approved(1)

    @api.multi
    def act_re_visit(self):
        return self.order_id.act_re_visit()

    @api.multi
    def act_cancel(self):
        # To change state in visit and approval to cancel if order Canceled
        record = self.env['finance.visit'].search([('order_id', '=', self.order_id.id)])
        record.write({'state': 'cancel'})
        for approval in record.approve_ids:
            approval.write({'state': 'canceled'})
        return self.order_id.act_cancel()

    @api.multi
    def act_approve_cancel(self):
        return self.order_id.act_approve_cancel()

    @api.depends('from_family', 'out_of_family')
    def _compute_total_workers(self):
        self.both_all = self.from_family + self.out_of_family

    @api.one
    @api.depends('income_resources_ids.amount','net_profite_avg','expenditure_avg')
    def _amount_all(self):
        """
        Compute the total amounts of the income resources.
        """
        self.total_income = sum([l.amount for l in self.income_resources_ids])
        self.net_income = self.net_profite_avg + self.total_income
        self.net_surplus = self.net_income - self.expenditure_avg

    @api.model
    def _get_seq_finance_order_to_view(self):
        """
        Desc:Function to show next sequence in view without increment sequence
        :return: int
        """
        # search for sequence
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        #By Arwa: Use date range in sequence to reset seq
        """
        # check year if new then restart sequence from 1
        self._cr.execute('select "name" from "finance_order" order by "id" desc limit 1')
        last_id_year_returned = str(self._cr.fetchone())[3:7]
        if (last_id_year_returned != str(datetime.now().year)):
            self._cr.execute('Alter sequence ir_sequence_%03d Restart ' % sequence.id)
        # get next number in sequence
        """
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, values):
        # Override the original create function for the finance_order model
        # Change the value of variables in this super function to increment sequence and save it
        values['name'] = self.env['ir.sequence'].get(self._name) or '/'
        return super(finance_individual_order, self).create(values)



class income_resources(models.Model):
    _name = 'income.resources'
    _description = "Personal Income Resources"

    finance_order_id = fields.Many2one('finance.individual.order', 'Finance Order', index=True, ondelete='cascade')
    name_type = fields.Many2one('income.resources.type', 'Income Resources Type', index=True, ondelete='restrict',required=True)
    company_currency_id = fields.Many2one('res.currency', related='finance_order_id.company_currency_id', string="Company Currency", readonly=True,
        help='Utility field to express amount currency', store=True)
    amount = fields.Monetary(string='Amount', currency_field='company_currency_id',required=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
