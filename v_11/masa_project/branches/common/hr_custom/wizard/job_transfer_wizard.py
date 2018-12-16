##############################################################################
# -*- coding: utf-8 -*-
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import Warning

class HrJobTransfer(models.TransientModel):
    _name = "job.transfer.wiz"

    job_id = fields.Many2one('hr.job' , string="Job" ,required=True , domain="[('state', '=', 'approved')]")
    to_department_id = fields.Many2one('hr.department' , string="To Department" ,required=True)
    from_department_id = fields.Many2one('hr.department' , string="From Department" ,required=True)
    type = fields.Selection([
        ('with_emps','With Employees') ,
        ('without_emps','Without Employees')] ,string="Type" , default='without_emps')
    reason = fields.Text(string="Transfer Reason" ,required=True)
    date = fields.Datetime(string="Date" ,required=True ,default=fields.Datetime.now)

    @api.onchange('job_id')
    def onchange_job_id(self):
        if self.job_id:
           departments=[]
           for rec in self.job_id.department_ids:
                departments.append(rec.department_id.id)
           self.to_department_id = False
           self.from_department_id = False
           return {'domain': {'from_department_id': [('id', 'in', departments)],'to_department_id': [('j_type', '=', self.job_id.j_type)]}}

    @api.multi
    def transfer_job(self):
        from_rec = self.env['hr.job.department'].search([
            ('department_id', '=', self.from_department_id.id),('job_id','=',self.job_id.id)])
        if from_rec:
            if from_rec.no_of_employee and self.type == "without_emps":
                raise Warning(_("You can not transfer a job that contains employees without employee"))
            to_rec = self.env['hr.job.department'].search([
                ('department_id', '=', self.to_department_id.id),('job_id','=',self.job_id.id)])
            if to_rec:
                to_rec.write({'no_of_plan':to_rec.no_of_plan + from_rec.no_of_plan})
            else:
                self.env['hr.job.department'].create({
                    'department_id':self.to_department_id.id,
                    'job_id':self.job_id.id,
                    'no_of_plan':from_rec.no_of_plan
                })
            if self.type == "with_emps":
                 contract_ids = self.env['hr.contract'].search([('department_id','=',self.from_department_id.id),
                    ('job_id', '=', self.job_id.id),('state', 'in', ['draft', 'open', 'pending'])])
                 contract_ids.write({'department_id':self.to_department_id.id})
                 employee_ids = self.env['hr.employee'].search([('department_id','=',self.from_department_id.id),
                    ('job_id', '=', self.job_id.id)])
                 employee_ids.write({'department_id': self.to_department_id.id})
            from_rec.unlink()
            message = _("This job has been transfered from %s to %s.<br/> Transfer Reason %s ") % (self.from_department_id.name, self.to_department_id.name,self.reason)
            self.job_id.message_post(body=message)
        
        return True

