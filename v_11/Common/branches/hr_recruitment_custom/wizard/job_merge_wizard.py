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
        self.env['hr.job.history'].create({
        'reasons':self.resone,
        'user_id':self.env.user.id,
        'cancel_date':self.date,
        'process':"Merge",
        'job_id':self.job_id.id,
        })
        if self.type == "with_emps":
            # self.job_id.department_id = self.department_id.id
            rec = self.env['hr.employee'].search([('job_id', '=', self.job_id.id)])
            for x in rec :
                x.job_id = self.to_job_id.id
            record = self.env['hr.contract'].search([('job_id', '=', self.job_id.id),('state', 'in', ['draft', 'open', 'pending'])])
            for y in record :
                y.job_id = self.to_job_id.id
            z = 0
            if self.job_id.department_ids:
                print("lkdsdsdjjasdh sdghsdhsgdhsdgshdgsdh dhdgshdgadhasdsadas dasdgsad g")
                rec = self.env['hr.job.department'].search([('job_id','=',self.job_id.id)])
                for a in rec:
                    # z = z + a.emp_no
                    if self.to_job_id.department_ids:
                        print("hgfhdgfdshfgshfgsfhgfhsdgfhsfgshfghsfghsdfghsgfhgfhfhsfgshfshfgsfgsdhfgsdhfsgdfhsdgfdshfgsdhfgsdhfgdshfgshfgsdhfgsdhfgsdhfgsdhfgdshfg")
                        # print("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz",z)
                        records = self.env['hr.job.department'].search(['|',('job_id','=',self.to_job_id.id),('department_id','=',a.department_id.id)])
                        print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj", records)
                        for h in records:
                            print("helllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllo")
                            if h.department_id == a.department_id:
                                # e = a.emp_no
                                # d = h.emp_no
                                # g = e + d
                                # h.emp_no = g
                                # a.unlink()
                                print("hhhhiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
                    record = self.env['hr.job'].search([('id','=',self.to_job_id.id)]).write({
                    'department_ids': [(0,0, {
                        'department_id':a.department_id.id,
                        'emp_no':a.emp_no,})]

                    })
                    print("jkjjssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",record)
                                # h.create({})
                                # h.emp_no = a.emp_no
                                # print("llllllllllllllllllllllllllllllllllllllkkkkkkkkkkkkkkkkkkkkklllllllllllllllllllllllllllkkkkkkkkkkkkkkkklklklklklk", g)
                    # else:
                    #     print("jkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
            else:
                self.job_id.write({'state':'cancel'})
            # y = record.emp_no
            # s = z+y
            # record.emp_no = s
            # print("llllllllllllllllllllllllllllllfffffffffffffffffffffffffffflllllllly",record.emp_no)

                # if self.job_id.no_of_employee:
                #     raise Warning(_("You can not cancel a job that contains employees"))
                # else:
                #     self.job_id.write({'state':'cancel'})
        else:
            if self.job_id.no_of_employee:
                raise Warning(_("You can not cancel a job that contains employees"))
            else:
                self.job_id.write({'state':'cancel'})
