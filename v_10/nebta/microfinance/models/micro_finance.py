# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, models, fields, exceptions, _
from dateutil.relativedelta import relativedelta
import datetime
import re


class finance_group_member(models.Model):
    _name = "finance.group.member"
    _order = "create_date desc"
    _description = "Finance Group Member"

    name = fields.Char(string="Name", required=True, size=256)
    identity_type_id = fields.Many2one("finance.identity.type", string="Identity Type", required=True, ondelete="restrict")
    identity_number = fields.Char(string="Identity Number", required=True, size=256)
    employer_id = fields.Many2one('micro.finance.employer', string='Employer',required=True)
    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender", required=True)
    company_currency_id = fields.Many2one("res.currency", related="company_id.currency_id", string="Company Currency", readonly=True,
        help="Utility field to express amount currency", store=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.user.company_id, string="Company",ondelete='cascade')
    phone = fields.Char(string="Phone")
    title = fields.Selection([("head", "Group Head"), ("secretary", "Secretary"), ("financial_secretary", "Financial Secretary"), ("member", "Member")], string="Title", required=True)
    group_id = fields.Many2one("finance.group", string="finance Group", required=True, ondelete="cascade")


    @api.constrains('name','identity_number')
    def _check_member_name(self):
        """
        To prevent name from accepting white space
        :return:
        """
        white_space = re.compile(r'^\s')
        if white_space.search(self.name) or white_space.search(self.identity_number):
            raise exceptions.ValidationError(_("cannot accept blank space you must enter real data..!!"))


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('order_member_ids', []):
            member_ids = self.env["finance.group.order"].resolve_2many_commands('order_member_ids', self._context.get('order_member_ids', []))
            args.append(('id', 'not in', [isinstance(d['group_member_id'], tuple) and d['group_member_id'][0] or d['group_member_id'] for d in member_ids]))
        return super(finance_group_member, self).name_search(name, args=args, operator=operator, limit=limit)


class finance_group(models.Model):
    _name = "finance.group"
    _order = "create_date desc"
    _description = "Finance Group"

    name = fields.Char(string="Name", required=True, size=256)
    partner_code = fields.Char(related='partner_id.code')
    user_id = fields.Many2one('res.users', string="Officer", default=lambda self: self.env.user, readonly=True,
                              required=True, ondelete='restrict')
    display_name = fields.Char(compute='compute_display_name',string="group name", store=True, index=True)
    #number = fields.Char(string="Number", required=True, size=256, readonly=True, default=lambda self: self._get_seq_finance_grop_to_view())
    member_ids = fields.One2many("finance.group.member", "group_id", string="Group Member", required=True)
    partner_id = fields.Many2one('res.partner', string='Partner Name', readonly=False, domain=[('customer','=',True)],ondelete='cascade')
    company_id = fields.Many2one("res.company", default=lambda self: self.env.user.company_id, string="Company",
                                 ondelete='cascade')

    @api.constrains('name')
    def _name_exsit(self):
        """
        To Check if the name is allready exist
        :return:
        """
    @api.constrains('member_ids')
    def check_members_identity(self):
        """
        Desc:Check Members Identity
        :return:
        """
        identity_number = ''
        employer_id= ''
        phone= ''

        for member in self.member_ids:
            for partner in self.env['res.partner'].search(['&',('identity_id','=',member.identity_type_id.id),('identity_number','=',member.identity_number)]):
                raise exceptions.ValidationError(
                    _("Identity Type  And its Number "+str(member.identity_number)+" For Another Customer By Code"+str(partner.code)))
        for member in self.member_ids:
            identity_type_id = member.identity_type_id.id
            identity_number = member.identity_number
            employer_id = member.employer_id
            phone = member.phone
            count = 0
            for mem in self.member_ids:
                if (identity_number == mem.identity_number and identity_type_id == mem.identity_type_id.id) or (
                    phone == mem.phone):
                    count += 1
                    if count > 1:
                        raise exceptions.ValidationError(
                            _("Every group member must have uniqe phone and idintity number"))
    @api.multi
    def action_group_transfer(self):
        ###### to open Group Transfer Wizard ######


        view_ref = self.env['ir.model.data'].get_object_reference('microfinance', 'finance_transfer_customer_wiz_view')
        view_id = view_ref and view_ref[1] or False,
        ###### context to send data from this record to group transfer wizard #######
        return {
            'type': 'ir.actions.act_window',
            'name': _('Customer Transfer'),
            'res_model': 'finance.transfer.customer.wiz',
            'context': {'user_id': self.user_id.id,
                        'company_id': self.user_id.company_id.id,
                        'partner_id': self.partner_id.id},
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
        }

    @api.multi
    def unlink(self):
        """
        To prevent delete group when group have order
        :return:
        """
        group_order = self.env['finance.group.order'].search([('group_id', 'in', self.ids)])
        for group in group_order:
            if group.group_id.id in self.ids:
                raise exceptions.ValidationError(_("You cannot delete this group. because it already have order"))
        return super(finance_group, self).unlink()

    @api.constrains('name')
    def _check_group_name(self):
        """
        To prevent name from accepting white space
        :return:
        """
        white_space = re.compile(r'^\s')
        if white_space.search(self.name):
            raise exceptions.ValidationError(_("cannot accept blank space you must enter real data..!!"))

    @api.multi
    def name_get(self):
        """
        To Display full group name (partner_code + name)
        :return:
        """
        return [(group.id, '%s - %s ' % (group.partner_code, group.name)) for group in self]

    @api.depends('name', 'partner_id.code')
    def compute_display_name(self):
        """
        To help in search with partner_code and name in the same time
        and display partner_code + name
        :return:
        """
        names = dict(self.with_context().name_get())
        for group in self:
            group.display_name = names.get(group.id)

    @api.constrains('member_ids')
    def check_phones(self):
        """
        Desc:Check Phones correct form
        :return:
        """
        # Regex pattern to check all chars are integers
        pattern = re.compile(r'^[0]\d{9,9}$')
        pattern2 = re.compile(r'\d{6,50}$')

        for member in self.member_ids:
            if not pattern.search(member.phone):
                raise exceptions.ValidationError(_('Phones of Group Members must be exactly 10 Numbers and Start with ZERO 0 .'))
            if not pattern2.search(member.identity_number):
                raise exceptions.ValidationError(_("ID Number must be at least 6 Numbers."))



    @api.constrains('member_ids')
    def _check_title(self):
        #BY Arwa: make msgs translatable, use _(msg)
        head_count = 0
        secretary_count = 0
        financial_secretary_count = 0
        for record in self.env['finance.group.member'].search([('id', 'in', self.member_ids.ids)]):
            if record.title == "head":
                head_count = head_count + 1
            elif record.title == "secretary":
                secretary_count = secretary_count + 1
            elif record.title == "financial_secretary":
                financial_secretary_count = financial_secretary_count + 1
        error_message = _("you can not have more than 1 ")
        if head_count > 1:
            error_message += _("head,")
        if secretary_count > 1:
            error_message += _("secretary,")
        if financial_secretary_count > 1:
            error_message += _("financial secretary,")
        if head_count > 1 or secretary_count > 1 or financial_secretary_count > 1:
            raise exceptions.ValidationError(_(error_message))
        error_message2 = _("Group must have at least one ")
        if head_count == 0:
            error_message2 += _("head , ")
        if secretary_count == 0:
            error_message2 += _("secretary , ")
        if financial_secretary_count == 0:
            error_message2 += _("financial secretary , ")
        if head_count == 0 or secretary_count == 0 or financial_secretary_count == 0:
            raise exceptions.ValidationError(_(error_message2))

    #By Arwa: no need, _check_title constraint enough
    @api.constrains('member_ids')
    def _check_member(self):
        count = 0
        if not self.member_ids:
            for record in self.member_ids:
                count = len(record.member_ids)
            if count == 0:
                raise exceptions.ValidationError(_("Group must have members"))

    """@api.model
    def _get_seq_finance_grop_to_view(self):
    
        Desc:Function to show next sequence in view without increment sequence
        :return: int
    
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.number_next_actual"""

    @api.model
    def create(self, values):
        #By Arwa: Update values dict then create record (reduce DB access)
        # Override the original create function for the finance_group model
        group_name = self.env['finance.group'].search([])
        for names in group_name:
            if names.name == values['name']:
                raise exceptions.ValidationError(
                    _("This Group is already exist with %s code" % names.partner_code))
        record = super(finance_group, self).create(values)
        #By Arwa: Server WARNING ir_sequence.get() and ir_sequence.get_id() are deprecated. Please use ir_sequence.next_by_code() or ir_sequence.next_by_id().
        # Change the value of variable in this super function to increment sequence and save it
        #record['number'] = self.env['ir.sequence'].get(self._name)
        # send last id in res.partner to link it with new group
        record['partner_id'] = self.env['res.partner'].create({'name': values['name'],'customer':True})
        return record


class finance_group_order(models.Model):
    _name = "finance.group.order"
    _order = "create_date desc"
    _inherits = {'finance.order': 'order_id'}
    _description = 'Finance Group Order'

    @api.onchange("group_id")
    def _compute_no(self):
        if self.group_id:
            self.partner_id= self.group_id.partner_id
            member_count = self.env["finance.group.member"].read_group([("group_id", "=", self.group_id.id)], ["gender"], ["gender"])
            gender_count = dict([(m.get('gender'), m.get('gender_count')) for m in member_count])
            self.update(gender_count)

    @api.depends("male","female")
    def _compute_total_no(self):
        self.all_member = self.male + self.female

    order_id = fields.Many2one('finance.order')
    name = fields.Char(string="Order Number", required=True, copy=False, readonly=True, default=lambda self: self._get_seq_finance_grop_order_to_view())
    group_id = fields.Many2one("finance.group", string="Group",ondelete='cascade', required=True)
    male = fields.Integer(string="No of Male", required=True)
    female = fields.Integer(string="No of Female", required=True)
    all_member = fields.Integer(string="No of Member", compute="_compute_total_no", required=True)
    phone1 = fields.Char(String="Phone 1", required=True)
    phone2 = fields.Char(String="Phone 2", required=True)
    phone3 = fields.Char(String="Phone 3", required=True)
    order_member_ids = fields.One2many("finance.group.order.member", "group_order_id", string="Group Member")
    allocation = fields.Selection([ ('collective', 'Collective'), ('collaborative', 'Collaborative')], default='collective')
    payment_period = fields.Integer('Payment Period')
    funding_period = fields.Integer(string='Funding Period', related="order_id.funding_period")
    description = fields.Text(string="Description")


    @api.multi
    def unlink(self):
        self.order_id.unlink()

    @api.constrains('payment_period')
    def check_payemnt_period(self):
        if self.formula in ['salam','mudarba','muzaraa','musharka']:
            if self.payment_period <= 0:
                raise exceptions.ValidationError(_("payment period must be more than zero"))

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


    @api.onchange('group_id')
    def _set_members_zero(self):
        """
        When Change the Group Change number of members to zero
        and recompute it
        :return:
        """
        self.all_member = 0
        self.female = 0
        self.male = 0
        self._compute_no()
        self._compute_total_no()


    @api.constrains('guarantee_line_ids')
    def _check_guantee_income(self):
        """
        Desc : Check have at least one guarantee and income
        :return:
        """
        if len(self.guarantee_line_ids)==0:
            raise exceptions.ValidationError(_('Must have Guarantee.'))


    @api.onchange('payment_method_ids', 'installments_number')
    def get_funding_period(self):
        """
        Desc : Same function in finance.order with slice change from @depends to @api.onchange
        :return:
        """
        self.funding_period, self.funding_period_day = divmod(
            (self.payment_method_ids.number_of_days * self.installments_number), 30)

    @api.onchange('project_status')
    def insert_project_status(self):
        """
        Desc:insert project status to all group members
        :return:
        """
        for lines in self.order_member_ids:
            lines.project_status=self.project_status

    @api.constrains('amount', 'order_member_ids')
    def _check_project_status(self):
        """
        Desc:Verifies Project Status for all group member.

        """
        
        if (self.allocation == 'collective'):
            status = set([lines.project_status for lines in self.order_member_ids])
            if(len(status)>1):
                    raise exceptions.ValidationError(_('When Collective Selected All Group Member must Have same Project Status'))

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

        return self.order_id.act_approved(self.all_member)

    @api.multi
    def act_re_visit(self):
        return self.order_id.agt_re_visit()

    @api.multi
    def act_cancel(self):
        # To change state in visit to cancel if order Canceled
        record = self.env['finance.visit'].search([('order_id', '=', self.order_id.id)])
        record.write({'state': 'cancel'})
        for approval in record.approve_ids:
            approval.write({'state': 'canceled'})
        return self.order_id.act_cancel()

    @api.multi
    def act_approve_cancel(self):
        return self.order_id.act_approve_cancel()

    '''By Arwa: all_member could be not equal number of group member which entered in system  
    @api.constrains('order_member_ids')
    def _check_members_numbers(self):
        """
        Desc:Verifies the number of selected members equal to group members number.

        """
        if len(self.order_member_ids) != self.all_member:
            raise exceptions.ValidationError(_('All Group Member Must Be Selected .'))
    '''
    
    @api.onchange('amount', 'group_id')
    def import_group_members(self):
        '''
        Desc:Function to return selected group member from group into member ids and divide amount equally between them
        :return:
        '''
        # store current amount
        amount = self.amount
        # variable to count members to divide amount later
        count = len(self.group_id.member_ids)
        # bring into members ids member and title and amount share
        writevals = []
        for memberids in self.group_id.member_ids:
            writevals.append([0, False, {'amount': (amount / count), 
                                         'group_member_id': memberids.id,
                                         'title': memberids.title,
                                         'project_status': self.project_status}, ])
        # to set phones of head , secretary and financial secretary in phones fields
            if(memberids.title == 'head'):
                self.phone1 = memberids.phone
            if(memberids.title == 'secretary'):
                self.phone2 = memberids.phone
            if(memberids.title == 'financial_secretary'):
                self.phone3 = memberids.phone
        self.order_member_ids = writevals

    @api.model
    def _get_seq_finance_grop_order_to_view(self):
        """
        Desc:Function to show next sequence in view without increment sequence in order number
        :return: int
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        # check year if new then restart sequence from 1
        #By Arwa: Use date range in sequence to reset seq
        """
        self._cr.execute('select "name" from "finance_group_order" order by "id" desc limit 1')
        last_id_year_returned = str(self._cr.fetchone())[3:7]
        if(last_id_year_returned != str(datetime.now().year)):
            self._cr.execute('Alter sequence ir_sequence_%03d Restart ' % sequence.id)
        # check year if new then restart sequence from 1
        """
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, values):
        # Override the original create function for the finance_group_order model
        # Change the value of variables in this super function to increment sequence and save it
        values['name'] = self.env['ir.sequence'].next_by_code( self._name)
        return super(finance_group_order, self).create(values)

    @api.constrains('amount', 'order_member_ids')
    def _check_order_amount_equal_total_group_amount(self):
        """
        Desc:Verifies the order amount equal to total group amount.
        """
        members_amount_total = sum(m.amount for m in self.order_member_ids)  # sum all members account
        if(self.amount != members_amount_total):
            raise exceptions.ValidationError(_('total of members amounts must be equal to "amount" order.'))

    @api.constrains('allocation', 'order_member_ids')
    def _check_group_collective_amount(self):
        """
        Desc:Verifies the order amount equals to each other if collective selected.
        """
        if self.allocation == 'collective':
            if len(set([m.amount for m in self.order_member_ids])) > 1:
                raise exceptions.ValidationError(_(
                    'must amount of members equal to each other when collective selected in Microfinance Details page.'))


class finance_group_order_member(models.Model):
    _name = "finance.group.order.member"
    _description = "Finance Group Order Member"

    company_currency_id = fields.Many2one("res.currency", related="group_order_id.company_currency_id", string="Company")
    amount = fields.Monetary(string="Amount", currency_field='company_currency_id', required=True)
    group_member_id = fields.Many2one("finance.group.member", string="Member", required=True, ondelete="cascade")
    title = fields.Selection(related="group_member_id.title", string="Title", store=True)
    project_status = fields.Selection([("new", "New"), ("exist", "Exist"), ("stopped", "Stopped")],
                                      string="Project Status")
    group_order_id = fields.Many2one("finance.group.order", string="finance Group Order", required=True, ondelete="cascade")
    alc =  fields.Selection(related="group_order_id.allocation")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
