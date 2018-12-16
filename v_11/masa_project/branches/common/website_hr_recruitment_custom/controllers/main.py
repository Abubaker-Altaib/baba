# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.addons.website_form.controllers.main import WebsiteForm


class WebsiteHrRecruitmentCustom(WebsiteHrRecruitment):
   
    @http.route('/jobs/apply/<model("hr.job"):job>', type='http', auth="public", website=True)
    def jobs_apply(self, job, **kwargs):
        country = request.env['res.country']
        qualifications = request.env['hr.recruitment.degree']
        skill = request.env['hr.skills']
        Officialtime = request.env['resource.calendar']
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')
        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
            'country': country,
            'countries': country.get_website_hr_recruitment_countries(),
            'qualificationss':qualifications.get_website_hr_recruitment_degree(),
            'skills':skill.get_website_hr_recruitment_skill(),
            'Officialtimes':Officialtime.get_website_hr_recruitment_skill_resource_calendar(),
        })

    @http.route('/jobs/detail/<model("hr.job"):job>', type='http', auth="public", website=True)
    def jobs_detail(self, job, **kwargs):
        return request.render("website_hr_recruitment.detail", {
            'job':job,
            'main_object': job,
            'Skills':job.skills_ids,
            'Languages':job.lang_ids,
            'degree':job.get_website_hr_recruitment_Degree(),
        })


