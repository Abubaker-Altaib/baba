# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class stockCreateRequestion(models.TransientModel):
    _name = 'stock.requestion.create'

    picking_id = fields.Many2one('stock.picking')
    product_requesiton_ids = fields.One2many('stock.requestion.create.products','stock_create_id')
    


    @api.multi
    def action_confirm(self):
        self.ensure_one()

        lines = self.mapped('product_requesiton_ids')
        if lines.filtered(lambda line: line.initial_demand <= 0):
            raise UserError(_("Please Make Initial Demand for all Products More than zero"))

        products = [self.__create_products(m) for m in
                    self.product_requesiton_ids]

        if products:
            purchase_requisition = self.env['purchase.requisition'].create({
                'name': (_('Exchange Order From Picking') + str(self.picking_id.name)),
                'user_id': self.env.user.id,
                'type_id': 1,
                'ordering_date': fields.datetime.now(),
                'line_ids': products,
                'state': 'in_progress',
                'department_id':self.picking_id.department_id.id,
                'user_id': self.picking_id.user_id.id
            })
            self.picking_id.purchase_requisition_id = purchase_requisition.id
            self.picking_id.with_context(requistion_false=True)._show_purchase_button()
            self.picking_id.state = 'waiting_payment'
        return self.picking_id.with_context(requestion_create=False).create_purchase_requesetion()

    def __create_products(self, product):
        product_memory = (0, 6, {
            'product_id': product.product_id.id,
            'product_qty': product.initial_demand,
            'product_uom_id':product.product_id.uom_id.id
            #'stock_exchange_line': product.id,
            #'description': product.name,
        })
        return product_memory

class stockCreateRequestionProducts(models.TransientModel):
    _name = 'stock.requestion.create.products'

    product_id = fields.Many2one('product.product',required=1)
    initial_demand = fields.Integer(required=1)
    product_uom = fields.Many2one(related="product_id.uom_po_id")
    stock_create_id = fields.Many2one('stock.requestion.create')


