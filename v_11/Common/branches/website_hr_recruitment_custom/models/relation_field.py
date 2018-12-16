# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResCountry(models.Model):
    _inherit = 'res.country'

    def get_website_hr_recruitment_countries(self):
        return self.sudo().search([])


class RecruitmentDegree(models.Model):
    _inherit = 'hr.recruitment.degree'

    def get_website_hr_recruitment_degree(self):
        return self.sudo().search([])


class HrSkills(models.Model):
    _inherit = "hr.skills"

    def get_website_hr_recruitment_skill(self):
        return self.sudo().search([])

class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def get_website_hr_recruitment_skill_resource_calendar(self):
        return self.sudo().search([])

class HrJob(models.Model):
    _inherit = "hr.job"

    date_closed = fields.Date("Closed Date" )

    def get_website_hr_recruitment_Degree(self):
        degree = self.env['hr.recruitment.degree']
        return degree.search([('id','=', self.degree_ids.ids)],order='sequence',limit=1)
