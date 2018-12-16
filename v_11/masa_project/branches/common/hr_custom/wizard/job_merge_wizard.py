# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import Warning

class HrJobMerge(models.TransientModel):
    _name = "job.merge.wiz"

    job_id = fields.Many2one('hr.job' , string="Job" , required=True , domain="[('state', '=', 'approved')]")
    to_job_id = fields.Many2one('hr.job' , string="Merge to" ,required=True , domain="[('state', '=', 'approved')]")
    type = fields.Selection([
        ('with_emps','With Employees') ,
        ('without_emps','Without Employees')] ,string="Type", default='without_emps')
    reason = fields.Text(string="Merge Reason", required=True)
    date = fields.Datetime(string="Date" ,required=True ,default=fields.Datetime.now)

    @api.multi
    def merge_job(self):
    
        if self.job_id.no_of_employee and self.type == "without_emps":
            raise Warning(_("You can not merge a job that contains employees"))
        else:
            self.job_id.write({'state':'merge'})
            message = _("This job has been Merged with %s.<br/> Merge Reason %s ") % (self.to_job_id.name, self.reason)
            self.job_id.message_post(body=message)
        job_rec = self.env['hr.job.department'].search([('job_id','=',self.job_id.id)])
        for  rec in job_rec:
            self.to_job_id.write({'expected_employees':self.to_job_id.expected_employees + rec.no_of_plan})
            merge_rec = self.env['hr.job.department'].search([
                ('department_id', '=', rec.department_id.id),('job_id','=',self.to_job_id.id)])
            if merge_rec:
                merge_rec.write({'no_of_plan':merge_rec.no_of_plan + rec.no_of_plan})
            else:
                self.env['hr.job.department'].create({
                    'department_id':rec.department_id.id,
                    'job_id':self.to_job_id.id,
                    'no_of_plan':rec.no_of_plan
                })
            
        if self.type == "with_emps":
            contract_ids = self.env['hr.contract'].search([('job_id', '=', self.job_id.id),
                ('state', 'in', ['draft', 'open', 'pending'])])
            contract_ids.write({'job_id':self.to_job_id.id})
            employee_ids = self.env['hr.employee'].search([('job_id', '=', self.job_id.id)])
            employee_ids.write({'job_id':self.to_job_id.id})
        return True
