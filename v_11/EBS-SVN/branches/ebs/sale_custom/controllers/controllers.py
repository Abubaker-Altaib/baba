# -*- coding: utf-8 -*-
from odoo import http

# class SaleCustom(http.Controller):
#     @http.route('/sale_custom/sale_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_custom/sale_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_custom.listing', {
#             'root': '/sale_custom/sale_custom',
#             'objects': http.request.env['sale_custom.sale_custom'].search([]),
#         })

#     @http.route('/sale_custom/sale_custom/objects/<model("sale_custom.sale_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_custom.object', {
#             'object': obj
#         })