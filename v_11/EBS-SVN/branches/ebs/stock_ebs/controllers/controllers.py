# -*- coding: utf-8 -*-
from odoo import http

# class StockEbs(http.Controller):
#     @http.route('/stock_ebs/stock_ebs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_ebs/stock_ebs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_ebs.listing', {
#             'root': '/stock_ebs/stock_ebs',
#             'objects': http.request.env['stock_ebs.stock_ebs'].search([]),
#         })

#     @http.route('/stock_ebs/stock_ebs/objects/<model("stock_ebs.stock_ebs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_ebs.object', {
#             'object': obj
#         })