from odoo import fields, models, api, exceptions, _
from datetime import datetime, timedelta
from datetime import date


class KhalwaSupportOrder(models.Model):
    _inherit = 'support.order'
    _name = 'dzc_7.support.order'
    state_id = fields.Many2one('zakat.state', 'State')
    products_ids = fields.One2many('support.products','sabeel_id',string="Products")

  
class SupportProducts(models.Model):
    _name="support.products"

    sabeel_id = fields.Many2one('dzc_7.support.order')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Integer(string='Product Quantity')

    @api.constrains('product_qty')
    def qty_validation(self):
        if self.product_qty <= 0:
            raise ValidationError(_("Product Quantity MUST be greater Than Zero"))

    @api.constrains('amount')
    def qty_validation(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount MUST be Greater Than Zero"))
