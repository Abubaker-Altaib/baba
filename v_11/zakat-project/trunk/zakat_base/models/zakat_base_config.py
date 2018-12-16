# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api, exceptions, _
from datetime import datetime
from odoo.exceptions import ValidationError


class State_state(models.Model):
    _name = 'zakat.state'
    _order = 'create_date desc'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        """ Returns a list of tupples containing id, name, as internally it is called {def name_get}
            result format: {[(id, name), (id, name), ...]}
        """

        if self._context.get('states_ids', []):
            state_plan = self.env['dzc2.project.planning'].resolve_2many_commands('plan_ids',
                                                                                  self._context.get('states_ids', []))
            args.append(('id', 'not in',
                         [isinstance(d['state_plan_ids'], tuple) and d['state_plan_ids'][0] or d['state_plan_ids']
                          for d in state_plan]))

        return super(State_state, self).name_search(name, args=args, operator=operator, limit=limit)

    _sql_constraints = [
        ('name', 'unique(name)', _('The state name must not be repeated')),
        ('number', 'unique(state_number)', _('The state number must not be repeated')),
    ]

    name = fields.Char(string="State Name", required=True)
    state_number = fields.Char(string="State Number", required=True)
    local_state_ids = fields.One2many('zakat.local.state', 'state_id')
    company_id = fields.Many2one('res.company', string="Company", ondelete='restrict')
    sectors_state_ids = fields.One2many('zakat.sectors', 'sector_state')

    @api.constrains('state_number', 'name')
    def fields_check(self):
        if not re.match("^[0-9]*$", self.state_number.replace(" ", "")):
            raise ValidationError(_('State Number Field must be number'))
        if self.state_number.replace(" ", "") != self.state_number:
            raise ValidationError(_('State Number Field must be number'))
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('State name Field must be Literal'))
        if self.state_number == '0':
            raise exceptions.ValidationError(_("State Number Cannot Be Zero"))


class local_states_sectors(models.Model):
    _name = 'local.states.sectors'
    _order = 'create_date desc'

    local_state = fields.Many2one('zakat.sectors', string="")
    sector_local_states = fields.Many2one('zakat.local.state', 'Local States')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')


class sectors(models.Model):
    _name = 'zakat.sectors'
    _order = 'create_date desc'

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    name = fields.Char(string="Sector Name")
    sectors_number = fields.Integer(string="Sector Number")
    sector_state = fields.Many2one('zakat.state', 'State')
    states_sec = fields.One2many('local.states.sectors', 'local_state', string="")

    _sql_constraints = [
        ('name', 'unique(name)', _('The Sector name must not be repeated')),
        ('number', 'unique(sectors_number)', _('The Sector number must not be repeated')),
    ]

    @api.model
    @api.constrains('states_sec')
    def local_state_norepeat(self):
        sectors = self.env['zakat.sectors'].search([('id', '!=', self.id)])
        lstates_in_sectors = []
        if sectors:
            for rec in sectors:
                for r in rec.states_sec:
                    lstates_in_sectors.append(r.sector_local_states.id)
            for re in self.states_sec:
                if re.sector_local_states.id in lstates_in_sectors:
                    raise ValidationError(_('There is a Local state already added to another sector'))
                else:
                    True

                    # zakat.sectors

    @api.multi
    @api.constrains('name')
    def _validate_name(self):
        for rec in self:
            if rec.name.isalpha() or ' ' in rec.name:
                return True
            else:
                raise ValidationError(_('The Name You Entered Is Not Valid'))

    @api.multi
    @api.constrains('sectors_number')
    def _positive(self):
        for record in self:
            if record.sectors_number <= 0:
                raise ValidationError(_('Sector Number Must Be Greater Than Zero'))
        return True


class LocalState(models.Model):
    _name = 'zakat.local.state'
    _order = 'create_date desc'

    _sql_constraints = [
        ('name', 'unique(name)', _('The local state name must not be repeated')),
        ('number', 'unique(local_state_number)', _('The local state number must not be repeated')),
    ]
    name = fields.Char(string="Local State Name")
    local_state_number = fields.Char(string="Local State Number")
    state_id = fields.Many2one('zakat.state', 'State', ondelete="restrict")
    admin_unit_ids = fields.One2many('zakat.admin.unit', 'local_state_id')
    sector_id = fields.Many2one('zakat.sectors', 'Sectors', store=True, ondelete="restrict")
    poor_percentage = fields.Float("Poor Percentage")
    company_id = fields.Many2one('res.company', string="Company", ondelete='restrict')

    @api.constrains('poor_percentage')
    def _per(self):
        for rec in self:
            if rec.poor_percentage < 0 or rec.poor_percentage > 100:
                raise ValidationError(_("Percentage Can\'t Be Less Than Zero Or More Than One Hundred"))
            else:
                return True

    @api.constrains('local_state_number', 'name')
    def fields_check(self):
        num_pattern = re.compile(r'\d', re.I | re.M)
        white_space = re.compile(r'^\s')
        if not re.match("^[0-9]*$", self.local_state_number.replace(" ", "")):
            raise ValidationError(_('Local State Number Field must be number'))
        if self.local_state_number.replace(" ", "") != self.local_state_number:
            raise ValidationError(_('Local State Number Field must be number'))
        if self.local_state_number == '0':
            raise exceptions.ValidationError(_("Local State Number Cannot Be Zero"))
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Local State name Field must be Literal'))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        """ Returns a list of tupples containing id, name, as internally it is called {def name_get}
            result format: {[(id, name), (id, name), ...]}
        """
        if self._context.get('loacl_states_ids', []):
            state_plan = self.env['dzc1.health.insurance.plan'].resolve_2many_commands('loacl_states_ids',
                                                                                       self._context.get(
                                                                                           'loacl_states_ids', []))
            args.append(('id', 'not in',
                         [isinstance(d['loacl_states_id'], tuple) and d['loacl_states_id'][0] or d['loacl_states_id']
                          for d in state_plan]))
        if self._context.get('states_sec', []):
            sector = self.env['zakat.sectors'].resolve_2many_commands('states_sec',
                                                                      self._context.get(
                                                                          'states_sec', []))
            args.append(('id', 'not in',
                         [isinstance(d['sector_local_states'], tuple) and d['sector_local_states'][0] or d[
                             'sector_local_states']
                          for d in sector]))
        return super(LocalState, self).name_search(name, args=args, operator=operator, limit=limit)


class AdministrativeUnit(models.Model):
    _name = 'zakat.admin.unit'
    _order = 'create_date desc'
    _rec_name = 'name'

    _sql_constraints = [
        ('name', 'unique(name)', _('The administrative unit name must not be repeated')),
        ('number', 'unique(admin_unit_number)', _('The administrative unit number must not be repeated')),
    ]
    name = fields.Char(string="Administrative Unit Name", required=True)
    admin_unit_number = fields.Char(string="Administrative Unit Number", required=True)
    local_state_id = fields.Many2one('zakat.local.state', 'Local State', ondelete="restrict", required=True)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')

    @api.constrains('admin_unit_number', 'name')
    def fields_check(self):
        if not re.match("^[0-9]*$", self.admin_unit_number.replace(" ", "")):
            raise ValidationError(_('Administrative Unit Number Field must be number'))
        if self.admin_unit_number.replace(" ", "") != self.admin_unit_number:
            raise ValidationError(_('Administrative Unit Number Field must be number'))
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Administrative Unit name Field must be Literal'))
        if self.admin_unit_number == '0':
            raise exceptions.ValidationError(_("Administrative Unit Number Cannot Be Zero"))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        """ Returns a list of tupples containing id, name, as internally it is called {def name_get}
            result format: {[(id, name), (id, name), ...]}
        """

        if self._context.get('admin_ids', []):
            state_plan = self.env['orphang.rantee.planning'].resolve_2many_commands('sector_ids',
                                                                                    self._context.get('admin_ids', []))
            args.append(('id', 'not in',
                         [isinstance(d['unit_of_adminstrative_id'], tuple) and d['unit_of_adminstrative_id'][0] or d[
                             'unit_of_adminstrative_id']
                          for d in state_plan]))

        return super(AdministrativeUnit, self).name_search(name, args=args, operator=operator, limit=limit)


###########################

class organizations(models.Model):
    _name = 'dzc2.organizations'
    _order = 'create_date desc'

    name = fields.Char(string='Organization Name', required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    channel_type = fields.Selection([('fageer', 'Fageer'),
                                     ('dawa', 'Dawa'), ('fe_sabeel', 'Fe Sabeel Allah')
                                        , ('projects', 'Projects')], string="Channel Type")
    date = fields.Date('Date Of Registration')
    activity = fields.Selection([('social', 'Social'), ('dawee', 'Dawee')])
    support_type = fields.Selection([('emergency', 'Emergency'), ('periodic', 'Periodic')])
    address = fields.Char('Address')
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Sorry! Organization Name Must Be Unique .')]
    journal_id = fields.Many2one('account.journal', string='Journal ID', company_dependent=True)
    property_analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",
                                                   company_dependent=True)
    property_account_id = fields.Many2one('account.account', string='Account ID', company_dependent=True)

    @api.constrains('name', 'address')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.address.replace(" ", "")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.address.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))


class State(models.Model):
    _name = 'zakat.country'


######################################################
#
#  General Zakat Chamber  Settings
#  Accounting - Per Company
#
########################################################
class ZakatResCompany(models.Model):
    _inherit = 'res.company'

    property_basal_drainage_account_id = fields.Many2one('account.account', ondelete="restrict",
                                                         string="Basal Drainage Account",
                                                         company_dependent=True)
    property_basal_drainage_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                                  string="Basal Drainage Analytic Account",
                                                                  company_dependent=True)
    property_basal_drainage_journal = fields.Many2one('account.journal', ondelete="restrict",
                                                      string="Basal Drainage Journal",
                                                      company_dependent=True)
    property_ibanalsabil_account_id = fields.Many2one('account.account', ondelete="restrict",
                                                      string="Iban Alsabil Account",
                                                      company_dependent=True)
    property_ibanalsabil_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                               string="Iban Alsabil Analytic Account",
                                                               company_dependent=True)
    ibanalsabil_journal = fields.Many2one('account.journal', ondelete="restrict", string="Iban Alsabil Journal",
                                          company_dependent=True)
    property_fesabeelallah_account_id = fields.Many2one('account.account', ondelete="restrict",
                                                        string="Iban Alsabil Account",
                                                        company_dependent=True)
    property_fesabeelallah_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                                 string="Iban Alsabil Analytic Account",
                                                                 company_dependent=True)
    fesabeelallah_journal = fields.Many2one('account.journal', ondelete="restrict", string="Iban Alsabil Journal",
                                            company_dependent=True)

    ncms_integration = fields.Boolean('Medical Commission Integration', default=False)

    health_ins_integration = fields.Boolean('Health Insurance Integration', default=False)


class ZakatSettings(models.TransientModel):
    _name = 'zakat.settings'

    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.user.company_id)
    property_basal_drainage_account_id = fields.Many2one('account.account', ondelete="restrict",
                                                         string="Basal Drainage Account",
                                                         company_dependent=True)
    property_basal_drainage_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                                  string="Basal Drainage Analytic Account",
                                                                  company_dependent=True)
    property_basal_drainage_journal = fields.Many2one('account.journal', ondelete="restrict",
                                                      string="Basal Drainage Journal",
                                                      company_dependent=True)
    property_ibanalsabil_account_id = fields.Many2one('account.account', ondelete="restrict",
                                                      string="Iban Alsabil Account",
                                                      company_dependent=True)
    property_ibanalsabil_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                               string="Iban Alsabil Analytic Account",
                                                               company_dependent=True)
    ibanalsabil_journal = fields.Many2one('account.journal', ondelete="restrict", string="Iban Alsabil Journal",
                                          company_dependent=True)
    property_fesabeelallah_account_id = fields.Many2one('account.account', ondelete="restrict",
                                                        string="Iban Alsabil Account",
                                                        company_dependent=True)
    property_fesabeelallah_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                                 string="Iban Alsabil Analytic Account",
                                                                 company_dependent=True)
    fesabeelallah_journal = fields.Many2one('account.journal', ondelete="restrict", string="Iban Alsabil Journal",
                                            company_dependent=True)

    property_prisoners_account_id = fields.Many2one('account.account', ondelete="restrict", string="Prisoners Account",
                                                    company_dependent=True)
    property_prisoners_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                             string="Prisoners Analytic Account",
                                                             company_dependent=True)
    property_prisoners_journal = fields.Many2one('account.journal', ondelete="restrict", string="Prisoners Journal",
                                                 company_dependent=True)
    ncms_integration = fields.Boolean('Medical Commission Integration', default=False)
    health_ins_integration = fields.Boolean('Health Insurance Integration', default=False)

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        self.property_basal_drainage_account_id = company.property_basal_drainage_account_id
        self.property_basal_drainage_analytic_account_id = company.property_basal_drainage_analytic_account_id
        self.property_basal_drainage_journal = company.property_basal_drainage_journal
        self.property_ibanalsabil_account_id = company.property_ibanalsabil_account_id
        self.property_ibanalsabil_analytic_account_id = company.property_ibanalsabil_analytic_account_id
        self.ibanalsabil_journal = company.ibanalsabil_journal
        self.property_fesabeelallah_account_id = company.property_fesabeelallah_account_id
        self.property_fesabeelallah_analytic_account_id = company.property_fesabeelallah_analytic_account_id
        self.fesabeelallah_journal = company.fesabeelallah_journal
        self.ncms_integration = company.ncms_integration
        self.health_ins_integration = company.health_ins_integration

    @api.one
    def set_company_values(self):
        company = self.company_id
        company.property_basal_drainage_account_id = self.property_basal_drainage_account_id
        company.property_basal_drainage_analytic_account_id = self.property_basal_drainage_analytic_account_id
        company.property_basal_drainage_journal = self.property_basal_drainage_journal
        company.property_ibanalsabil_account_id = self.property_ibanalsabil_account_id
        company.property_ibanalsabil_analytic_account_id = self.property_ibanalsabil_analytic_account_id
        company.ibanalsabil_journal = self.ibanalsabil_journal
        company.property_fesabeelallah_account_id = self.property_fesabeelallah_account_id
        company.property_fesabeelallah_analytic_account_id = self.property_fesabeelallah_analytic_account_id
        company.fesabeelallah_journal = self.fesabeelallah_journal
        company.ncms_integration = self.ncms_integration
        company.health_ins_integration = self.health_ins_integration


class Channels(models.Model):
    _name = 'zakat.channels'
    code = fields.Char(string='Ref')
    name = fields.Char(string='Channel Name')
    type = fields.Selection([('admin', 'Adminstrative'), ('holy', 'Holy')], string='Channel Type')
    analytic_account = fields.Many2one('account.analytic.account', 'Analytic Account')
    responsible = fields.Many2one('res.users', 'Responsible')
    parent = fields.Many2one('zakat.channels', 'Parent')

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.sequence.number_next_actual

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('basal.drainage.sequence') or '/'
        return super(Channels, self).create(vals)


class expensePortions(models.Model):
    _name = 'expense.portions'
    date = fields.Date(string="Date", default=datetime.today())
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    type = fields.Selection([('standard', 'Standard'), ('copy', 'Copy')], string="Type")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    portion_lines = fields.One2many(comodel_name='expese.portion.lines', inverse_name='ex', string="portions")
    state = fields.Selection([('draft', 'Draft'), ('valid', 'Valid'), ('cancle', 'Cancle')], string="Status",
                             default='draft')

    @api.one
    @api.constrains('company_id', 'date_from', 'date_to')
    def validate_company(self):
        expenses_portions = self.env['expense.portions'].search(
            [('company_id', '=', self.company_id.id), ('date_from', '<=', self.date_from),
             ('date_to', '>=', self.date_to), ('id', '!=', self.id)])
        if expenses_portions:
            raise exceptions.ValidationError(_('There is already a record for this company'))

    @api.one
    @api.constrains('portion_lines')
    def portions_validation(self):
        summ = 0.0
        for rec in self.portion_lines:
            summ += rec.portions
        if summ > 100:
            raise exceptions.ValidationError(_('Sorry! total portion can not  exceed 100%'))

    @api.constrains('date_from', 'date_to')
    def compare_date(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError(_("Sorry! Date From Must Be Before Date To ."))

    @api.model
    def create(self, vals):
        if vals['type'] == 'standard':
            standard_expenses = self.env['expense.portions'].search(
                [('type', '=', 'standard'), '&', ('date_from', '=', vals['date_from']),
                 ('date_to', '=', vals['date_to'])])
            if standard_expenses:
                raise exceptions.ValidationError(_('There is already a standard copy for this year'))
        else:
            True
        return super(expensePortions, self).create(vals)

    @api.multi
    def get_data(self):
        channels = self.env['zakat.channels'].search([])
        if not Channels:
            raise exceptions.ValidationError(_("You Must have Channels in Configuration!!"))
        else:
            channel_lines = {}
            for rec in channels:
                channel_lines = {}
                channel_lines = self.portion_lines.create({'channel_ids': rec.id})
                self.portion_lines += channel_lines

    @api.multi
    def action_valid(self):
        """
        Change state to valid
        :return:
        """

        self.write({'state': 'valid'})

    @api.multi
    def action_draft(self):
        """
        Change state to draft
        :return:
        """
        self.write({'state': 'draft'})

    @api.multi
    def action_cancel(self):
        """
        change state to cancel
        :return:
        """
        self.write({'state': 'cancel'})


class expencesPortionLines(models.Model):
    _name = 'expese.portion.lines'
    ex = fields.Many2one('expense.portions', string="Expences Portion")
    channel_ids = fields.Many2one('zakat.channels', string="Channels")
    portions = fields.Float(string="Portion")

    _sql_constraints = [('uniq_channel_id', 'unique(channel_ids,ex)',
                         _("Channel Must Not Be Repeated"))]
