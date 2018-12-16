# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime
from odoo import api , fields, models,_
from odoo.exceptions import Warning

class JobCancel(models.TransientModel):
    _name = "job.cancel.wiz"

    job_id = fields.Many2one("hr.job" , string="Job" ,required=True , domain="[('state', '=', 'approved')]")
    reason = fields.Text(string="Cancel Reason" , required=True)
    date = fields.Datetime(string="Date" ,required=True ,default=fields.Datetime.now)

    @api.multi
    def cancel_job(self):
        if self.job_id.no_of_employee:
            raise Warning(_("You can not cancel a job that contains employees"))
        else:
            self.job_id.write({'state':'cancel'})
            message = _("This job has been cancelled.<br/> Cancel Reason %s ") % (self.reason)
            self.job_id.message_post(body=message)
           
