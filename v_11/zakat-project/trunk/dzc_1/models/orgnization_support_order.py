# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models,api, exceptions,_
import re
from odoo.exceptions import ValidationError, AccessError 
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

class OrgnizationSupportOrder(models.Model):
    _name="support.order"

    date = fields.Date(string="Order Date",default=datetime.today())
    name = fields.Char("Order Sequence")
    oragnaztion_id = fields.Many2one("dzc2.organizations" )
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    program_name = fields.Char("Program Name",size=250)
    program_area = fields.Char("Program Area")
    estimated_cost = fields.Char("Estimated Cost")
    approved_amount = fields.Char("Approved Amount")
    People = fields.Char("Number Of People")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    researcher_report = fields.Text("Researcher Report")
    almasaref_manager_comment = fields.Text("Almasaref Manager Comment")
    secretary_state_decision = fields.Text("Secretary of State Decision")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approval', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], string="Status", default='draft')
    vaucher_id = fields.Many2one('account.voucher')
    support_type = fields.Selection([('organization','Organization'),('khalwa','Khalwa'),('masjid','Masjid'),('worship','Place Of worship'),('house','Place House')],'Support Type')
    support_method = fields.Selection([('cash','Cash'),('material','Material')],'Support Method')
    type_ = fields.Selection([('emergency','Emergency'),('periodic','Periodic')])
    state_id = fields.Many2one('zakat.state')
    products = fields.One2many(comodel_name='organization.support.products', inverse_name='organization_id')

    

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('name', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('support.order.sequance') or '/'
        return super(OrgnizationSupportOrder, self).create(vals)

    @api.multi
    def action_confirm(self):
        """
        Change State To Done
        :return:
        """
        self.write({'state': 'confirmed'})
    
    @api.multi
    def action_approve(self):
        """
        Change State To Done
        :return:
        """
        self.write({'state': 'approval'})
    
    @api.multi
    def action_cancle(self):
        """
        Change State To Done
        :return:
        """         
        self.write({'state': 'cancel'})

    @api.multi
    def action_done(self):
        if self.support_method == 'cash':
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
                if self.oragnaztion_id:
                    self.oragnaztion_id.write({'support_type':self.type_})
                else:
                    raise exceptions.ValidationError(_("There Is No Organization Selected. "))   
        self.write({'state': 'done'})

    @api.multi
    def action_set_draft(self):
        """
        Change State To Done
        :return:
        """

        self.write({'state': 'draft'})
    
    @api.multi
    def unlink(self):
        # check field state: all should be clear before we can unlink a field:
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Can\'t Delete None Drafted Record"))
            else:
                return super(OrgnizationSupportOrder, self).unlink()
    
    @api.constrains('program_name', 'program_area','secretary_state_decision','researcher_report','almasaref_manager_comment')
    def check_name(self):
        if self.program_name:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.program_name.replace(" ","")):
                raise ValidationError(_('Program Name Field must be Literal'))
            if self.program_name and (len(self.program_name.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Program Name must not be spaces"))
        if self.program_area:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.program_area.replace(" ","")):
                raise ValidationError(_('Program Area Field must be Literal'))
            if self.program_area and (len(self.program_area.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Program Area must not be spaces"))
        if self.researcher_report:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.researcher_report.replace(" ","")):
                raise ValidationError(_('Researcher Report must be Literal'))
            if self.researcher_report and (len(self.researcher_report.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Researcher Report must not be spaces "))
        if self.almasaref_manager_comment:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.almasaref_manager_comment.replace(" ","")):
                raise ValidationError(_('Almasarif Manager Comment must be Literal'))
            if self.almasaref_manager_comment and (len(self.almasaref_manager_comment.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Almasarif Manager Comment must not be spaces "))
        if self.secretary_state_decision:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.secretary_state_decision.replace(" ","")):
                raise ValidationError(_('Secretary State Decision must be Literal'))
            if self.secretary_state_decision and (len(self.secretary_state_decision.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Secretary State Decision must not be spaces "))
    
   


    @api.constrains('approved_amount','estimated_cost','People')
    def validate_numbers(self):
        if not re.match("^[0-9]*$", self.approved_amount.replace(" ", "")):
            raise ValidationError(_('Approved amount Cannot be Zero or Less or special Characters'))
        if self.approved_amount.replace(" ", "") != self.approved_amount:
            raise ValidationError(_('Approved amount Cannot be Zero or Less'))
        if self.approved_amount == '0':
            raise exceptions.ValidationError(_("Approved amount Cannot be Zero or Less or special Characters"))

        if not re.match("^[0-9]*$", self.estimated_cost.replace(" ", "")):
            raise ValidationError(_('Estimated amount Cannot be Zero or Less'))
        if self.estimated_cost.replace(" ", "") != self.estimated_cost:
            raise ValidationError(_('Estimated amount Cannot be Zero or Less'))
        if self.estimated_cost == '0':
            raise exceptions.ValidationError(_("Estimated amount Cannot be Zero or Less or special Characters"))

        if not re.match("^[0-9]*$", self.People.replace(" ", "")):
            raise ValidationError(_('People amount Cannot be Zero or Less or special Characters'))
        if self.People.replace(" ", "") != self.People:
            raise ValidationError(_('People amount Cannot be Zero or Less or special Characters'))
        if self.People == '0':
            raise exceptions.ValidationError(_("People amount Cannot be Zero or Less or special Characters"))

        # for rec in self:
        #     if rec.approved_amount:
        #         if rec.approved_amount <= 0.0:
        #             raise exceptions.ValidationError(_("Approved amount Cannot be Zero or Less"))
        #     if rec.estimated_cost:
        #         if rec.estimated_cost <= 0.0:
        #             raise exceptions.ValidationError(_("Estimated Cost Cannot be Zero or Less"))
        #     if rec.People:
        #         if rec.People <=0:
        #             raise exceptions.ValidationError(_("People Number Cannot be Zero or Less"))


class OrgnizationProducts(models.Model):
    _name="organization.support.products"

    organization_id = fields.Many2one('support.order')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Integer(string='Product Quantity')

    @api.constrains('product_qty')
    def qty_validation(self):
        if self.product_qty <= 0:
            raise ValidationError(_("Product Quantity MUST be greater Than Zero"))

    @api.constrains('amount')
    def qty_validation(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount MUST be Greater Than Zero"))
