# -*- coding: utf-8 -*-
from odoo import http

# class StockCustom(http.Controller):
#     @http.route('/stock_custom/stock_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_custom/stock_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_custom.listing', {
#             'root': '/stock_custom/stock_custom',
#             'objects': http.request.env['stock_custom.stock_custom'].search([]),
#         })

#     @http.route('/stock_custom/stock_custom/objects/<model("stock_custom.stock_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_custom.object', {
#             'object': obj
#         })