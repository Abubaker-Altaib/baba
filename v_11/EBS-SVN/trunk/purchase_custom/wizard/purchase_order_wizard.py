from odoo import api, fields, models, exceptions,_
from odoo.exceptions import UserError

class PurchaseOrderWizard(models.TransientModel):
    """ To manage enrich report wizard """
    _name = "purchase.order.wizard"


    date_from= fields.Date('Date From' , required=False)
    date_to= fields.Date('Date To' , required = False)
    state = fields.Selection([

                                ('to approve', 'Waiting for Service Manager'),
                                ('purchase', 'Waiting for General Manager'),
                                ('done_order', 'Done'),
                                ('done', 'Locked'),
                                ('cancel', 'Cancelled')

                ], string='State')

    vendor_id = fields.Many2one('res.partner','Vendor', domain="[('supplier','=',True)]")
    product_id = fields.Many2one('product.product','Product')
    dept_id = fields.Many2one('hr.department','Department')





    def print_report(self, data):

        if (self.date_from and self.date_to) and (self.date_from > self.date_to):
            raise UserError(_("Plz , Date From must always be greater than Date To. "))

        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'purchase.order',
            'data': data
        }
        return self.env.ref('purchase_custom.action_purchase_order_print').report_action(self, data=datas)


