from odoo import api, fields, models, exceptions,_
from odoo.exceptions import UserError

class subject_wizard(models.TransientModel):
   
    _name = "subject.wizard"


    subject= fields.Char('Subject')
    
    def print_report(self, data):

        current_sale_order_id = data['active_id']
       
        self.ensure_one()
        [data] = self.read()

        datas = {
            'ids': [],
            'model': 'sale.order',
            'data': data,
            'current_sale_order_id':current_sale_order_id
        }
        return self.env.ref('crm_custom.action_invoice_details_print').report_action(self, data=datas)


