# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    qualification_ids = fields.One2many('hr.employee.qualification','employee_id','Education')
    experience_ids = fields.One2many('hr.employee.experience','employee_id','Professional Experience')


class EmployeeQualification(models.Model):
    _name = 'hr.employee.qualification'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee','Employee',required=True,states={'validated': [('readonly', True)]})
    degree_id = fields.Many2one('hr.job.degree', "Qualification", ondelete="cascade",required=True,states={'validated': [('readonly', True)]})
    specialt_id= fields.Many2one('hr.specialst', "Specialt", ondelete="cascade",states={'validated': [('readonly', True)]})
    institute_id = fields.Char('Institutes', ondelete="cascade",required=True,states={'validated': [('readonly', True)]})
    score = fields.Selection([
            ('excellent','Excellent'),
            ('vgood','Very Good'),
            ('good','Good'),
            ('acceptable','Acceptable'),
            ],required=True,states={'validated': [('readonly', True)]})
    qualified_year = fields.Date(required=True,states={'validated': [('readonly', True)]})
    state =fields.Selection([
            ('draft','Draft'),
            ('validated','Validated'),],default="draft", required=True, readonly=True, copy=False)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'education_attachment_rel','attachment_id',
        string='Attachments',required=True,states={'validated': [('readonly', True)]})

    @api.model
    def create(self,vals):
        attachment_obj = self.env['ir.attachment']
        result = super(EmployeeQualification, self).create(vals)
        for resource in result:
            for source in resource.attachment_ids:
                if source:
                    attachment_id = attachment_obj.search([('id', '=',source.id)])
                    attachment_id.write({'res_id':result.id})
        return result

    @api.multi
    def write(self,vals):
        attachment_obj = self.env['ir.attachment']
        result = super(EmployeeQualification, self).write(vals)
        for resource in self:
            for source in resource.attachment_ids:
                if source:
                    attachment_id = attachment_obj.search([('id', '=',source.id)])
                    attachment_id.write({'res_id':self.id})
            for resource in self:
                attachment_ids = attachment_obj.search([('res_id', '=', self.id)])
                delete=[]
                for attachment in attachment_ids:
                    if attachment not in resource.attachment_ids:
                        delete.append(attachment)
                for attach in delete:
                    attach.unlink()
        return result

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def set_validated(self):
        if self.attachment_ids:
            self.write({'state': 'validated'})
        else:
            raise ValidationError(_("Please Attach Employee Qualification Document."))

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'hr.employee.qualification'), ('res_id', '=', self.id)]
        res['context'] = {'default_res_model': 'hr.employee.qualification', 'default_res_id': self.id}
        return res



class EmployeExperience(models.Model):
    _name = 'hr.employee.experience'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee','Employee',required=True,states={'validated': [('readonly', True)]})
    categ_id = fields.Many2one("hr.job.category" ,required=True, string="Job Category", readonly=True, states={'draft':[('readonly',False)]})
    job_id = fields.Many2one('hr.job','Job',required=True,states={'validated': [('readonly', True)]})
    location = fields.Char(states={'validated': [('readonly', True)]})
    from_date = fields.Date('Start Date',required=True,states={'validated': [('readonly', True)]})
    to_date = fields.Date('End Date',required=True,states={'validated': [('readonly', True)]})
    attachment_ids = fields.Many2many(
        'ir.attachment', 'profession_attachment_rel',
        'profession_id','attachment_id',
        string='Attachments',required=True,states={'validated': [('readonly', True)]})
    state = fields.Selection([
            ('draft','Draft'),
            ('validated','Validated'),],default="draft", required=True, readonly=True, copy=False)


    _sql_constraints = [
        ('to_date_greater', 'check(to_date > from_date)', 'Start Date of Professional Experience should be less than End Date!'),
        ]

    @api.model
    def create(self,vals):
        attachment_obj = self.env['ir.attachment']
        result = super(EmployeExperience, self).create(vals)
        for resource in result:
            for source in resource.attachment_ids:
                if source:
                    attachment_id = attachment_obj.search([('id', '=',source.id)])
                    attachment_id.write({'res_id':result.id})
        return result

    @api.multi
    def write(self,vals):
        attachment_obj = self.env['ir.attachment']
        result = super(EmployeExperience, self).write(vals)
        for resource in self:
            for source in resource.attachment_ids:
                if source:
                    attachment_id = attachment_obj.search([('id', '=',source.id)])
                    attachment_id.write({'res_id':self.id})

        for resource in self:
            attachment_ids = attachment_obj.search([('res_id', '=', self.id)])
            delete=[]
            for attachment in attachment_ids:
                if attachment not in resource.attachment_ids:
                    delete.append(attachment)

            for attach in delete:
                attach.unlink()
        return result

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def set_validated(self):
        if self.attachment_ids:
            self.write({'state': 'validated'})
        else:
            raise ValidationError(_("Please Attach Employee Experience Document."))

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'hr.employee.experience'),('res_id', '=', self.id)]
        res['context'] = {'default_res_model': 'hr.employee.experience', 'default_res_id': self.id}
        return res

    @api.constrains('from_date','to_date')
    def check_from_date(self):
        """
        This method is called when future Start date is entered.
        --------------------------------------------------------
        @param self : object pointer
        """
        date = fields.Datetime.now()
        if (self.from_date > date) or (self.to_date > date):
            raise ValidationError('Future Start Date or End Date in Professional experience is not acceptable!!')


class EmployeeSpecialt(models.Model):
    _name = "hr.specialst"

    name = fields.Char("Specialst",required=True)
    code = fields.Char("Code")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the specialst  must be unique!'),
    ]
