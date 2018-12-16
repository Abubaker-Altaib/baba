from odoo import api, fields, models, exceptions,_
from odoo.exceptions import UserError

# class certificate_invoice_wizard(models.TransientModel):
   
#     _name = "certificate.invoice.wizard"


#     subject= fields.Char('Subject')
    
#     def print_report(self, data):

#         current_sale_order_id = data['active_id']

#         self.ensure_one()
#         [data] = self.read()
      
#         datas = {
#             'ids': [],
#             'model': 'sale.order',
#             'data': data,
#             'current_sale_order_id':current_sale_order_id
#         }
#         return self.env.ref('sale_custom.action_certificate_invoice').report_action(self, data=datas)


