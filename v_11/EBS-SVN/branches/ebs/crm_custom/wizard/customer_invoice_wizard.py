from odoo import api, fields, models, exceptions,_
from odoo.exceptions import UserError

class customer_invoice_wizard(models.TransientModel):
   
    _name = "customer.invoice.wizard"


    service_id= fields.Many2one('product.product','Service',domain="[('service','=',True)]" )
    center_id = fields.Many2one('sale.center','Center' , required = False)
    customer_id = fields.Many2one('res.partner','Customer', domain="[('customer','=',True)]")
    date_from =fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    state = fields.Selection([
        ('draft','Draft'),
        ('confirm','Waiting for Supervisor'),
        ('review','Waiting for Department Manager'),
        ('approve','Waiting for Accounting Administrator'),
        ('validate','Validated'),])
    

    def print_report(self, data):

        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'sale.order',
            'data': data
        }
        return self.env.ref('crm_custom.action_customer_invoice_print').report_action(self, data=datas)


