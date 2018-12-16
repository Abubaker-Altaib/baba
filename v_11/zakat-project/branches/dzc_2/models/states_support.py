# -*- coding: utf-8 -*-

import re
import math
from datetime import datetime ,date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError
from odoo.exceptions import UserError


##############################################
# Process of Prepairing States Support
##############################################

class dzc_2PrepairingStatesSupport(models.Model):

    _name = 'dzc2.prepairing.states.support'
    """docstring for dzc_2PrepairingStatesSupport"""
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    code=fields.Char(string="Reference Number",readonly=True )
    name = fields.Char(string ="Description",copy=False)
    date_of_plan_ids = fields.Date(string="Date", default=datetime.today())
    duration_from  = fields.Date(string="Date From" ,copy=False)
    duration_to = fields.Date(string="Date To",copy=False)
    states_support = fields.One2many('dzc2.states.support','prepairing_support_id',string='States Support')
    amana_planned_support = fields.Float(string="Amana Planned Support Amount")
    amana_execute_support = fields.Float(string="Amana Excuted Support Amount")
    amana_remain_support = fields.Float(string="Amana Remaining Support Amount" ,compute="compute_amana_remain_amount")


    @api.multi
    @api.constrains('amana_execute_support','amana_planned_support')
    def amana_support_validation(self):
        for rec in self : 
            if rec.amana_planned_support <= 0:
                raise exceptions.ValidationError(_('Sorry! Amana Planned Support Amount Cannot Be 0 Or Minus '))
            if rec.amana_execute_support > self.amana_planned_support:
                raise exceptions.ValidationError(_('Sorry! Amana Excuted Support Amount Cannot Exceed Amana Planned Support Amount '))


    @api.onchange('amana_execute_support')
    def compute_amana_remain_amount(self):
        for rec in self : 
            rec.amana_remain_support = rec.amana_planned_support - rec.amana_execute_support 


    state = fields.Selection([('draft' , 'Draft') ,
     ('confirm' , 'Confirm') ,
      ('approve' , 'Approve') ,
       ('done' , 'Done') ,
        ('cancel' , 'Cancel')],string="Status" ,default='draft')


    @api.multi
    def confirm_action(self):
        self.env.context  = {'status_action' : True}

        self.write({'state': 'confirm'})

    @api.multi
    def approve_action(self):
        self.env.context  = {'status_action' : True}

        self.write({'state': 'approve'})

    @api.multi
    def done_action(self):
        self.env.context  = {'status_action' : True}
        if not self.states_support :
            raise exceptions.ValidationError(_("states support lines must not be empty in done state "))

        self.write({'state': 'done'})


    @api.multi
    def cancel_action(self):
        self.env.context  = {'status_action' : True}

        self.write({'state': 'cancel'})

    @api.multi
    def set_to_draft_action(self):
        self.env.context  = {'status_action' : True}
        self.write({'state': 'draft'})


    #************ SQL Constrains *********************#
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Sorry! Prepairing States Support Name Must Be Unique .')]



    # @api.constrains('duration_from','duration_to')
    # def compare_date(self):
    #     for rec in self:
    #         if rec.duration_to < rec.duration_from:
    #             raise ValidationError(_("Sorry! Begin Of Plan Date Must Be Before End Date ."))


    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)



    @api.constrains('name','states_support')
    def check_name(self):
        if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.name.replace(" ","")):
            raise ValidationError(_('Description Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("Description must not be spaces"))
        if self.state== 'done' :
            if len(self.states_support) == 0 :
                raise exceptions.ValidationError(_("states support lines cannot be empty"))
    


    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('done'):
                raise UserError(_('Sorry! You Cannot Delete Prepairing Support Plan in Done State.'))
        return models.Model.unlink(self)

    @api.multi
    def copy(self, default=None ):
        self.env.context  = {'skip_copy' : True}
        default = dict(default or {})

        default.update({'states_support':self.get_lines() })
       
        return super(dzc_2PrepairingStatesSupport, self).copy(default)


    @api.multi
    def get_lines(self):

        plan_line = []
        for d in self.states_support:
            plan_line +=  [(0, 6, {
            'state_ids': d.state_ids.id,
            'projects': d.projects.id,
            'plan_ids_amount': d.plan_ids_amount,})]
        return plan_line

    @api.model
    def create(self, vals):
        vals['code'] = self.sudo().env['ir.sequence'].sudo().next_by_code('dzc2.prepairing.states.sequence') or '/'
        if 'skip_copy' in self.env.context and self.env.context['skip_copy']:
            return super(dzc_2PrepairingStatesSupport, self).create(vals)
         
        plans = self.env['dzc2.prepairing.states.support'].search([('duration_from' , '>=', vals['duration_from']) , ('duration_to' ,'<=' , vals['duration_to'])])

        if plans:
            raise ValidationError(_('Sorry! You cannot make Plan  with same duration.'))
        if vals['duration_from'] > vals['duration_to']:
            raise ValidationError(_('Sorry! Begin Of Plan Date Must Be Before End Date ..'))
    
        return super(dzc_2PrepairingStatesSupport, self).create(vals)


    @api.multi
    def write(self , vals):

        if 'status_action' in self.env.context and self.env.context['status_action']:
            return super(dzc_2PrepairingStatesSupport, self).write(vals)
        
        plans = self.env['dzc2.prepairing.states.support'].search([('duration_from' , '>=', self.duration_from) , ('duration_to' ,'<=' , self.duration_to),('id','!=',self.id)])
        
        if plans:
            raise ValidationError(_('Sorry! You cannot make Plan  with same duration.'))
        

        if self.duration_from > self.duration_to:

            raise ValidationError(_('Sorry! Begin Of Plan Date Must Be Before End Date ..'))

        return super(dzc_2PrepairingStatesSupport, self).write(vals)


class dzc_2StatesSupport(models.Model):
    _name = 'dzc2.states.support'
    state_ids = fields.Many2one('zakat.state',string='State')
    projects = fields.Many2one('dzc2.project',string ='Projects',domain= [('is_basic','=',True)])
    plan_ids_amount = fields.Float(string="Planned Amount")
    excute_amount = fields.Float( string ="Executed Amount")
    remain_amount = fields.Float(string ="Remaining Amount" ,compute="remain_amount_comp")
    prepairing_support_id = fields.Many2one('dzc2.prepairing.states.support',string ='Field Label' )
    projects_request = fields.One2many('dzc2.project.request','prepairing_support',string='project request')
    

    _sql_constraints = [
        ('state_project_uniq', 'unique(state_ids,projects)',
         'Sorry! There are  Project Type that Repeated in the Same State')]


    @api.onchange('excute_amount','plan_ids_amount')
    def remain_amount_comp(self): 
            for rec in self:
                rec.remain_amount = rec.plan_ids_amount - rec.excute_amount


    @api.one
    @api.constrains('plan_ids_amount')
    def nonnigative_validation(self):
        for rec in self:
            if rec.plan_ids_amount<=0:
                 raise ValidationError(_("Sorry! Planned Amount Can Not Be Nigative Or Zero"))
