# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import UserError, ValidationError

class StrategicKpi(models.Model):
    _name ="strategic.kpi"
    _description="Strategic Kpi"
    _order = "sequence"

    name = fields.Char(string="Name",required=True)
    code = fields.Char(size=64, required=True, index=True)
    active = fields.Boolean(default=True)
    type = fields.Selection([
            ('strategic','Strategic'),
            ('executive','Executive'),],default="executive",required=True
            )
    measuring_unit=fields.Char(string="Measuring Unit",required=True)
    unit_type=fields.Selection([
            ('amount','Amount'),
            ('percentage','Percentage'),],default='amount',required=True
            )
    target_value= fields.Float(string="Target Value",required=True)
    actual_value= fields.Float(string="Actual Value",required=True)
    transformer= fields.Float(string="Transformer",required=True)
    residual= fields.Float(string="Residual",required=True,compute="_compute_residual")
    cal_method=fields.Selection([
            ('auto','Auto'),
            ('manual','Manual'),],default="manual",required=True
            )
    state=fields.Selection([
            ('draft','Draft'),
            ('inprogress','InProgress'),
            ('delayed','Delayed'),
            ('stumbling','Stumbling'),
            ('suspend','Suspend'),
            ('done','Done'),],default="draft",index=True, required=True, readonly=True, copy=False
            )
    sequence=fields.Integer(string='Sequence',required=True, copy=False)
    description=fields.Text(string='Description')
    Evaluation_management=fields.Text(string='Evaluation Management')
    Evaluation_senior_management=fields.Text(string='Evaluation Senior Management')
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    percentage=fields.Float(string="Percentage",compute="_compute_percentage",widgets='Percentage')
    date_start=fields.Date(string='Start date', index=True, required=True,copy=False)
    date_end=fields.Date(string='End date', index=True, required=True,copy=False)
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    executive_Plan_id=fields.Many2one('plan.excutive')
    task_ids = fields.One2many('plan.task', 'kpi_id', string='Tasks')

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def set_inprogress(self):
        self.write({'state': 'inprogress'})

    @api.multi
    def set_delayed(self):
        self.write({'state': 'delayed'})

    @api.multi
    def set_suspend(self):
        self.write({'state': 'suspend'})

    @api.multi
    def set_done(self):
        self.write({'state': 'done'})

    @api.multi
    def set_stumbling(self):
        self.write({'state': 'stumbling'})

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'strategic.kpi'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for strategic in self:
            strategic.attachment_number = attachment.get(strategic.id, 0)


    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'strategic.kpi'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'strategic.kpi', 'default_res_id': self.id}
        return res

    @api.one
    @api.depends('target_value','actual_value')
    def _compute_percentage(self):
        if self.target_value != 0:
            self.percentage=(self.actual_value/self.target_value)*100

    @api.one
    @api.depends('target_value','actual_value')
    def _compute_residual(self):
        if self.target_value != 0:
            self.residual=self.target_value-self.actual_value

    @api.multi
    @api.constrains('date_start','date_end')
    def _check_date_overlap(self):
        if self.date_start  and self.date_end:
            overlap_ids = self.search([('date_start','>',self.date_end),('date_end','<',self.date_start)])
            if overlap_ids:
                raise ValidationError(_(" End Date must be Greater than Start Date."))


    @api.multi
    def kpi_transformer(self):
        if self.residual>0:
            transformer_kpi=self.env['strategic.kpi'].search([
                    ('executive_Plan_id','=', self.executive_Plan_id.id),
                    ('date_start','>', self.date_end)],limit=1, order='date_start asc')
            if transformer_kpi:
                transformer_kpi.transformer=self.residual
                self.write({'state': 'done'})

class StrategicPartnerships(models.Model):
    _name = "strategic.partnerships"
    _description = "Strategic Partnerships"
    
    name = fields.Char(string="Name",required=True)
    code = fields.Char(size=64, required=True, index=True)
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)


class StrategicInitiatives(models.Model):
    _name = "strategic.initiatives"
    _description = "Strategic Initiatives"
    
    name = fields.Char(string="Name",required=True)
    code = fields.Char(size=64, required=True, index=True)
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)

