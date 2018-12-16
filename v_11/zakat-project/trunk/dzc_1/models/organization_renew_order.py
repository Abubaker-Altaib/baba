from odoo import fields, models,api, exceptions,_
import re
from odoo.exceptions import ValidationError, AccessError 
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


#################### Organization Renew Order #####################
class OrganizationsRenewOrder(models.Model):
    _name = 'dzc1.organization.renew.order'

    date = fields.Date(string="Date", default=datetime.today())
    name = fields.Char(string="Reference Number")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    oragnaztion_id = fields.Many2one('dzc2.organizations',string='Organization')
    program_name = fields.Char(string="Program Name" , size=250)
    approved_amount = fields.Float(string="Approved Amount")
    researcher_report = fields.Text(string=" ")
    almasaref_manager_comment = fields.Text(string="Almasaref Manager Comment")
    secretary_of_state_decision = fields.Text(string="Secretary of State Decision")
    executed_programs_ids = fields.One2many('dzc1.organization.executed.programs' , 'name' , string=" Executed programs")
    state = fields.Selection([('draft' , 'Draft') , ('confirm' ,'Confirm'),('approve' ,'Approve') ,('done' ,'Done'),('cancel' ,'Cancel')], string="Status" ,default="draft")
    vaucher_id = fields.Many2one('account.voucher')
    """
    Workflow states
    """
    @api.multi
    def confirm_action(self):
        if not self.executed_programs_ids:
            raise ValidationError(_('Please Insert Organization Executed Programs.'))
        else:
            self.write({'state': 'confirm'})

    @api.multi
    def cancel_action(self):
          self.write({'state': 'cancel'})

    @api.multi
    def approve_action(self):
          self.write({'state': 'approve'})

    @api.multi
    def done_action(self):
        if not self.oragnaztion_id.property_account_id.id:
                raise exceptions.ValidationError(_("There Is No Zakat Account Specified for this organization. "))
        elif not self.oragnaztion_id.journal_id.id:
                raise exceptions.ValidationError(_("There Is No Zakat Journal Specified for this organization."))
        else:

            organization_line = []
           
            organization_line +=  [(0, 6, {
            'name': self.oragnaztion_id.name,
            'account_id': self.oragnaztion_id.property_account_id.id,
            'quantity': 1,
            'name': _('Organization Support'),
            'price_unit': self.approved_amount,
            })]

            voucher = self.env['account.voucher'].create(
                {
                'name': '' ,
                'journal_id': self.oragnaztion_id.journal_id.id,
                'company_id': self.company_id.id,
                'pay_now': 'pay_later',
                'reference': self.oragnaztion_id.name,
                'voucher_type': 'purchase',
                'line_ids' :organization_line,
                })
            self.vaucher_id = voucher.id

        self.write({'state': 'done'})
    
    @api.multi
    def set_to_draft_action(self):
          self.write({'state': 'draft'})

    """
    unlinke can not be in done state
    """
    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(_('Sorry! You Cannot Delete Order In Not Draft State.'))
        return models.Model.unlink(self)

    """
    sequence of form (Reference)
    """
    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('dzc1.organization.renew.order.sequence') or '/'
        return super(OrganizationsRenewOrder, self).create(vals)
    """
    constrains in numbric fields
    """
    @api.constrains('approved_amount' )
    def validate_approved_amount(self):
       
        if self.approved_amount <= 0.0 :
            raise ValidationError(_('Sorry ! Approved Amount Can Not Be Negative or zero.'))
    
    @api.constrains('program_name')
    def program_name_validation(self):
        increment = 0
        if len(self.program_name) > 1 :
            for record in self.program_name[1:]:
                if record.isalpha() or record.isdigit():
                    increment +=1

                if increment == 0 :
                    raise ValidationError(_("Sorry! Program Name Field is Required And cannot start with special character ."))

        elif len(self.program_name) <= 1 and self.program_name[0] == ' ':
            raise ValidationError(_("Sorry! Program Name Field is Required And cannot start with special character ."))

############# Executed programs in organization ########
class OrganizationExecutedProgram(models.Model):
    _name = 'dzc1.organization.executed.programs'

    name = fields.Char(string="Program Name")
    no_of_people = fields.Integer(string="No Of People")
    cost = fields.Float(string="Cost")

    """
    numeric fields constrains
    """
    @api.constrains('cost' )
    def validate_cost(self):
       
        if self.cost <= 0.0 :
            raise ValidationError(_('Sorry ! Cost Can Not Be Negative or zero.'))
   
   
    @api.constrains('no_of_people' )
    def validate_no_of_peoplet(self):
       
        if self.no_of_people <= 0.0 :
            raise ValidationError(_('Sorry ! No of People Can Not Be Negative or zero.'))
        