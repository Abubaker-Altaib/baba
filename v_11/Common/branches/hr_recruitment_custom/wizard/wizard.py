# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models, _


class JobNeedsAggregation(models.TransientModel):
    _name = "job.needs.grouping"

    plan_id = fields.Many2one('hr.recruitment.plan', string="Plan", required=True, domain=[
        ('state', '=', 'draft'), ('plan_type', '=', 'an_plan')])
    job_id = fields.Many2one("hr.job", string="Job")
    
    @api.onchange('plan_id')
    def onchange_plan_id(self):
        if self.plan_id:
            needs=[]
            for rec in self.plan_id.need_ids:
                if not rec.grouping_id and rec.state=='approve':
                    needs.append(rec.job_id.id)
            self.job_id = False
            return {'domain': {'job_id': [('id', 'in', needs)]}}

    def create_group_need(self, job_id):
        need_id = False
        needs = self.env['hr.recruitment.needs'].search([
            ('plan_id', '=', self.plan_id.id), ('state', '=', 'approve'),
            ('grouping_id', '=', False), ('job_id', '=', job_id)])
        if needs:
            grouping_id = self.env['hr.recruitment.needs.grouping'].search([('plan_id', '=', self.plan_id.id),('job_id', '=', job_id)])
            if not grouping_id:
                grouping_id = self.env['hr.recruitment.needs.grouping'].create({
                    'job_id': job_id,
                    'plan_id': self.plan_id.id,
                    'state': 'approve'
                })
            needs.write({'grouping_id':grouping_id.id})
            need_id = grouping_id.id
        return need_id
                
    def get_needs(self):
        needs =[]
        jobs = []
        if self.job_id:
            grouping_id = self.create_group_need(self.job_id.id)
            if grouping_id:
                needs.append(grouping_id)
        else:
            jobs = self.env['hr.recruitment.needs'].read_group([
                ('plan_id', '=', self.plan_id.id), ('state', '=', 'approve'),
                ('grouping_id', '=', False)], ['job_id'],['job_id'])
                
            for job in jobs :
                grouping_id = self.create_group_need(job['job_id'][0])
                if grouping_id:
                   needs.append(grouping_id)
                
        return {
            'name': _('Needs Grouping'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.recruitment.needs.grouping',
            'domain': [('id', 'in', needs)],
        }
        
