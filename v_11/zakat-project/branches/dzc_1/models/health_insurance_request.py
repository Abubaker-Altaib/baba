# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models,api, exceptions,_
import re
from odoo.exceptions import ValidationError, AccessError 
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.zakat_base.models import API_integration


class HealthInsuranceRequest(models.Model):
    _name = 'health.insurance.order'
    _order = 'create_date desc'

    name = fields.Char("Order Sequence")
    date = fields.Date(string="Order Date",default=datetime.today())
    subject_name = fields.Char(string='Subject Name')
    local_state_id = fields.Many2one('zakat.local.state', string='Local State')
    type_ = fields.Selection([('add', 'Add'),
                              ('renew', 'Renew'),
                              ('replace', 'Replace'),
                              ('add_to_exist', 'Add To Exist')])
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approval', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], string="Status", default='draft')
    beneficiaries_ids = fields.One2many('insurance.beneficiaries', 'insurance_id', string='Fuqaraa', ondelete="restrict")
    address_id = fields.Many2one('addresses','Address')
    @api.constrains('subject_name')
    def check_name(self):
        if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.subject_name.replace(" ","")):
            raise ValidationError(_('Subject Name Field must be Literal'))
        if self.subject_name and (len(self.subject_name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("Subject Name must not be spaces"))

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('name', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('orphan.registration.order.sequance') or '/'
        return super(HealthInsuranceRequest, self).create(vals)

    @api.multi
    def action_confirm(self):
        """
        Change State To Confirm
        :return:
        """
        if self.beneficiaries_ids:
            self.write({'state': 'confirmed'})
        else:
            raise exceptions.ValidationError(_('This Request Have No Fuqaraa'))

    @api.multi
    def action_approve(self):
        """
        Change State To Approve
        :return:
        """
        self.write({'state': 'approval'})
    
    @api.multi
    def action_cancle(self):
        """
        Change State To Cancle
        :return:
        """
        self.write({'state': 'cancel'})

    @api.one
    def action_done(self):
        """
        Change State To Done
        :return:
        """
        for rec in self.beneficiaries_ids:
            if self.type_ == 'add':
                if not rec.no_insurance:
                    raise exceptions.ValidationError(_('You must insert Insurance Number'))
                if not self.beneficiaries_ids.insurance_start_date:
                    raise exceptions.ValidationError(_('You must insert Insurance Start Date'))
        """
        ADD Actual Execute REQUEST TO PLAN  
        """
        plan_ids = self.env['localstates.health.insurance.plan'].search(['&',('loacl_states_id' , '=' , self.local_state_id.id),('insurance_plan_id.state','=','done') ,'&',('insurance_plan_id.duration_from' , '<=' , self.date),('insurance_plan_id.duration_to' , '>=' , self.date)])
        for rec in plan_ids :
            if self.type_ == 'add':
                for fgeer in self.beneficiaries_ids.fageer_new_id:
                    fgeer.write({'i_health': True})
                    fgeer.write({'insurance_type': 'zakat'})
        self.write({'state': 'done'})


    @api.multi
    def action_set_draft(self):
        """
        Change State To Draft
        :return:
        """
        self.write({'state': 'draft'})
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Can\'t Delete None Drafted Record"))
            else:
                return super(HealthInsuranceRequest, self).unlink()
        
    
class Beneficiaries(models.Model):
    _name = 'insurance.beneficiaries'
    _order = 'create_date desc'
    name = fields.Char(compute="onchange_name",store=True)
    insurance_id = fields.Many2one("health.insurance.order",ondelete="restrict")    
    fageer_id = fields.Many2one('zakat.aplication.form', string="Faqeer")
    fageer_new_id = fields.Many2one('zakat.aplication.form', string="New Faqeer")
    relative_id = fields.Char('Relative')
    type_ = fields.Selection(string='Type',related='insurance_id.type_',store=True)
    no_insurance = fields.Char(string='Number Of Insurance')
    insurance_start_date = fields.Date(string='Insurance Start Date')
    local_state_id = fields.Many2one(related='insurance_id.local_state_id', string='Local State')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approval', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], string="Status", default='draft')
    company_id = fields.Many2one("res.company", default=lambda self: self.env.user.company_id, string="Company",
                                 ondelete='cascade')

    valid_bnf = fields.Boolean(string="validation done")
    crt_bnf_id = fields.Char(string="Beneficiary Number")
    cart_bnf_name = fields.Char(string="Beneficiary Name")
    cart_cst_name = fields.Char(string="Service Provider Name")
    cart_sts = fields.Char(string="Status")
    health_integration = fields.Boolean(related="company_id.health_ins_integration")
    admin_unit_id = fields.Many2one(string='Administrative Unit', related='fageer_new_id.admin_unit_id', store=True, )

    @api.one
    @api.depends('type_')
    def onchange_name(self):
        if self.type_ == 'add':
            self.name = self.fageer_new_id.name
            # self.write({'name_req':self.project_conf}) 
        else:
            self.name = self.fageer_id.name

    @api.onchange('type_')
    def get_cont(self):
        for rec in self:
            rec.local_state_id = self._context.get('local_state', [])
            rec.type_ = self._context.get('type', [])
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Can\'t Delete None Drafted Record"))
            else:
                return super(Beneficiaries, self).unlink()
    
    @api.constrains('relative_id')
    def check_name(self):
        if self.relative_id:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.relative_id.replace(" ","")):
                raise ValidationError(_('Relative Name Field must be Literal'))
            if self.relative_id and (len(self.relative_id.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Relative Name must not be spaces"))

    
  #   @api.multi
  #   def complete_function(self):
  #       for rec in self:
  #           if not rec.insurance_start_date:
  #               raise ValidationError(_("There Is No Insurance Start Date In This Record"))
  #           if rec.type_ == 'add' or rec.type_ == 'replace':
  #               if not rec.no_insurance:
  #                   raise ValidationError(_("There Is No Insurance Number"))
  #               if rec.fageer_new_id:
  #                   rec.fageer_new_id.write({'insurance_start_date':rec.insurance_start_date})
  #                   rec.fageer_new_id.write({'no_insurance':rec.no_insurance})
  #                   rec.fageer_new_id.write({'i_health':True})
  #               if rec.type_ == 'replace':
  #                   rec.fageer_id.write({'insurance_start_date':False})
  #                   rec.fageer_id.write({'no_insurance':False})
  #                   rec.fageer_id.write({'i_health':False})
  #           if rec.type_ == 'renew':
  #               if rec.fageer_id:
  #                   rec.fageer_id.write({'insurance_start_date':rec.insurance_start_date})
  #           if rec.type_ == 'add_to_exist':
  #               if rec.fageer_id:
  #                   rec.fageer_id.family_ids.create({'name':rec.relative_id,
  #                   'fageer_id':rec.fageer_id.id})
  #                   print("\n\n\n\nnew name",rec.fageer_id.family_ids,"\n\n\n")
  #           rec.write({'state':'done'})


  # ################################# Insurance health integration part ############

    @api.one
    def complete_function(self):
        id = 0
        plans = self.env['dzc1.health.insurance.plan'].search(['&','&',('state' , '=', 'done') , ('duration_from' , '<=' , self.insurance_start_date), ('duration_to' , '>=' , self.insurance_start_date)])
        for plan in plans:
            for local_state in plan.loacl_states_ids:
                if self.insurance_id.type_ == 'add':
                    self.fageer_new_id.no_insurance = self.no_insurance
                    self.fageer_new_id.insurance_start_date = self.insurance_start_date
                    id = self.fageer_new_id.local_state_id.id
                else:
                    id = self.fageer_id.local_state_id.id
                    self.fageer_id.no_insurance = self.no_insurance
                    self.fageer_id.insurance_start_date = self.insurance_start_date
                if local_state.loacl_states_id.id == id:
                    local_state.actual_execute += 1

        self.write({'state':'done'})
  ################################# Insurance health integration part ############

    @api.multi
    def health_insurance_call(self):

        beneficiary_health_num = self.no_insurance

        service_user_id = '793'
        service_passowrd = '793'

       
        url = "http://196.29.166.236/YSINS_WCF_API/YSINS_API.svc/getBnfData/"+beneficiary_health_num+"/"+service_user_id+"/"+service_passowrd
        api = API_integration.APIIntegration()
        code = api.wcf_connection(url)
        import ast

        if code == 200:
            response = api.wcf_get(url)
            
            if "Err" in response:
                raise exceptions.ValidationError(_("Please Check Beneficiary number"))
            
            else:
                response = response.replace('[', '').replace(']', '')
                response = response.replace('{', '').replace('}', '')
                response = response.replace('\\', '')
                response = response.split(',')
                res = { x.split(':')[0]: x.split(':')[1] for x in response }

                self.valid_bnf = True

                self.crt_bnf_id = self.no_insurance
                bnf_n = res["\"bnfName\""]

                self.cart_bnf_name = bnf_n.replace('"' , ' ')
                cst_n = res["\"cstName\""]

                self.cart_cst_name = cst_n.replace('"' , ' ')
                sts_n = res["\"sts\""].replace('"' , ' ')

                sts = ""
                if sts_n == ' 1 ':
                    sts = "Active"
                
                else:
                    sts = "Inactive"

                self.cart_sts = sts

                # self.bnf_phone = res[0][3]

        if code == False:
            raise exceptions.ValidationError(_("Please Check Your Internet Connection"))
