# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class stockBackOrder(models.TransientModel):
    _name = 'stock.backorder.create'

    picking_id = fields.Many2one('stock.picking')

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        return self.picking_id.with_context(backorder_create=False, requistion_false=True).validate_stock_backorder()

    @api.multi
    def action_no_backorder(self):
        self.ensure_one()
        return self.picking_id.with_context(backorder_create=False, requistion_false=True).validate_stock_no_backorder()