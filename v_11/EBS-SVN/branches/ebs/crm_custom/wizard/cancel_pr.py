from odoo import api, fields, models, exceptions,_
from odoo.exceptions import UserError

class cancel_pr(models.TransientModel):
   
    _name = "cancel.pr.wizard"


    cancel_reason= fields.Char('Cancel Reason' ,required='True')


    @api.multi
    def cancel_pr_button(self,data):
    	current_pr=self.env['purchase.requisition'].search([('id','=',data['active_id'])])

    	if current_pr :
    		current_pr.cancel_reson = self.cancel_reason
    		current_pr.state = 'cancel'

