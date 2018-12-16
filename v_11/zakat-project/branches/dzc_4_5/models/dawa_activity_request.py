# -*- coding: utf-8 -*-

import re
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError 

class DawaActivityRequest(models.Model):
    _name = 'dawa.activity.request'

    name = fields.Char("Order Sequence")
    date = fields.Date(string="Order Date",default=datetime.today())
    axis_id_id = fields.Many2one('dawa.axis',string="Axis")
    activity_id = fields.Many2one('dawa.axis.sub')
    estimate_amount = fields.Float("Estimate Amount")
    partner_id = fields.Many2one('res.partner')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user,
                               ondelete='restrict')
    approve_amount = fields.Float("Approve Amount")
    description = fields.Text("Description")
    state_id = fields.Many2one('zakat.state')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approval', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], string="Status", default='draft')
    vaucher_id = fields.Many2one('account.voucher')
    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('name', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('dawa.activity.request.sequance') or '/'
        return super(DawaActivityRequest, self).create(vals)
    
    @api.multi
    def action_confirm(self):
        """
        Change State To Confirm
        :return:
        """
        self.write({'state': 'confirmed'})

    @api.multi
    def action_approve(self):
        """
        Change State To Approve
        :return:
        """
        if self.state == 'confirmed' and self.approve_amount <= 0.0:
            raise ValidationError(_("Approved Amount Cannot be zero or Negative"))
        else:
            self.write({'state': 'approval'})

    @api.multi
    def action_cancle(self):
        """
        Change State To Cancle
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def action_done(self):
        """
        Change State To Done
        :return:
        """
        plan_ids = self.env['dzc_4_5.dawa.activities.plan'].search(['&',('state_id' , '=' , self.state_id.id),('axis_id','=', self.axis_id_id.id),'&',('state','=','done') , ('year' ,'=', datetime.today().year)])
        for rec in plan_ids :
            rec.activities_ids.execute += 1
        
        axis_line = []
           
        axis_line +=  [(0, 6, {
        'name': self.axis_id_id.name,
        'account_id': self.activity_id.account.id,
        'quantity': 1,
        'partner_id':self.partner_id,
        'name': _('Dawa Activity Request'),
        'price_unit': self.approve_amount,
        })]

        voucher = self.env['account.voucher'].create(
                {
                'name': '' ,
                'partner_id':self.partner_id.id,
                'journal_id': self.axis_id_id.journal_id.id,
                'company_id': self.company_id.id,
                'pay_now': 'pay_later',
                'reference': self.axis_id_id.name,
                'voucher_type': 'purchase',
                'line_ids' :axis_line,
                })
        self.vaucher_id = voucher
        print('\n\n\n\n\n\n',self.vaucher_id,'\n\n\n\n\n\n\n')
        self.write({'state': 'done'})
    
    @api.multi
    def action_set_draft(self):
        """
        Change State To Draft
        :return:
        """
        self.write({'state': 'draft'})
    
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Can\'t Delete None Drafted Record"))
            else:
                return super(DawaActivityRequest, self).unlink()
    
    @api.constrains('estimate_amount','approve_amount')
    def _validate_numbers(self):
        for rec in self:
            if rec.estimate_amount:
                if rec.estimate_amount <= 0.0 :
                    raise exceptions.ValidationError(_('Estimated Amount Cannot be Zero or Less'))
            if rec.approve_amount:
                if rec.approve_amount <= 0.0 :
                    raise exceptions.ValidationError(_('Approved Amount Cannot be Zero or Less'))
    
    @api.constrains('description')
    def check_name(self):
        if self.description:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.description.replace(" ","")):
                raise ValidationError(_('Description Field must be Literal'))
            if self.description and (len(self.description.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Relative Name must not be spaces"))
