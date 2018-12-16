from odoo import fields, models,api, exceptions,_
import re
from odoo.exceptions import ValidationError, AccessError 
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


#################### Social Support registration Order #####################
class SocialSupportRegistrationOrder(models.Model):
    _name = 'social.support.registration.order'

    date = fields.Date(string="Order Date", default=datetime.today())
    code = fields.Char(string="Reference Number")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user,
                               ondelete='restrict')
    name = fields.Char(string="Subject Name" , size=256)
    type = fields.Selection([('new' , 'New') , ('replace' ,'Replace')],default='new')
    fageer_ids = fields.One2many('fageer.registration.order' , 'order_id' , string="Fageer Id")
    state = fields.Selection([('draft' , 'Draft') , ('confirm' ,'Confirm'),('done' ,'Done'),('cancel' ,'Cancel')], string="Status",default="draft")
    
    """
    Workflow
    """
    
    @api.multi
    def confirm_action(self):
          self.write({'state': 'confirm'})

    @api.multi
    def cancel_action(self):
          self.write({'state': 'cancel'})

    @api.multi
    def done_action(self):
        self.write({'state': 'done'})
        if self.type == 'new':
            self.fageer_ids.fageer_new_id.s_support = True
            self.fageer_ids.fageer_new_id.status = self.fageer_ids.status
            self.fageer_ids.fageer_new_id.social_amount = self.fageer_ids.amount
        elif self.type == 'replace':
            self.fageer_ids.fageer_new_id.s_support = True
            self.fageer_ids.fageer_new_id.status = self.fageer_ids.status
            self.fageer_ids.fageer_new_id.social_amount = self.fageer_ids.amount

            self.fageer_ids.fageer_old_id.s_support = False
            self.fageer_ids.fageer_old_id.status = False
            self.fageer_ids.fageer_old_id.social_amount = 0.0

    
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
        vals['code'] = self.env['ir.sequence'].next_by_code('social.support.registration.order.sequence') or '/'
        
        return super(SocialSupportRegistrationOrder, self).create(vals)
    
    """
    Constrains
    """
    @api.constrains('name')
    def name_validation(self):
        increment = 0
        if len(self.name) > 1 :
            for record in self.name[1:]:
                if record.isalpha() or record.isdigit():
                    increment +=1

                elif increment == 0 :
                    raise ValidationError(_("Sorry! Subject Name Field is Required and Must begin with Char ."))

        elif len(self.name) <= 1 and self.name[0] == ' ':
            raise ValidationError(_("Sorry! Subject Name Field is Required and Must begin with Char ."))



class FageerRegistrationOrder(models.Model):
    _name = 'fageer.registration.order'

    name = fields.Char()
    order_id = fields.Many2one('social.support.registration.order')
    fageer_new_id = fields.Many2one('zakat.aplication.form' , string="New Faqir")
    fageer_old_id = fields.Many2one('zakat.aplication.form' , string="Old Faqir")
    status = fields.Selection([ ('i_m', 'Imam & Muezzin'),('sheikh', 'Sheikh'),
    	('deaf', 'Deaf'),('blind', 'Blind'),
    	('di_physically', 'disabled Physically'),('m_h', 'Mentally Handicapped')])
    support_type = fields.Selection([('fixed' ,'Fixed') ,('not_fixed' ,'Not Fixed')],default="not_fixed")
    amount = fields.Float(compute="sup_amount", string="Amount", store=True,)

   
    @api.model
    def create(self,vals):
        if vals['support_type'] == 'not_fixed':
            vals['amount'] = vals['amount']
            if vals['amount'] <= 0.0:
                raise ValidationError(_('Sorry ! Amount Can Not Be Zero Or Negative .'))

        if vals['support_type'] != 'not_fixed':
            fixed_amount = self.env['zakat.guarantees'].search([('type' ,'=' ,'s_support')])
            if not fixed_amount:
                raise ValidationError(_('There is no social support in configuration'))
            vals['amount'] = fixed_amount.amount
        return super(FageerRegistrationOrder, self).create(vals)

    """
    Name Default value
    """
    @api.onchange('fageer_new_id')
    def _onchange_(self):
        self.name = self.fageer_new_id.name

    """
    Constrains
    """
    @api.constrains('amount')
    def amount_validation(self):
        if self.support_type == 'not_fixed':
            for record in self:
                if record.amount <= 0.0 :
                    raise ValidationError(_('Sorry ! Amount Can Not Be Zero Or Negative .'))