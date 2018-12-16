# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseCustom(http.Controller):
#     @http.route('/purchase_custom/purchase_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_custom/purchase_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_custom.listing', {
#             'root': '/purchase_custom/purchase_custom',
#             'objects': http.request.env['purchase_custom.purchase_custom'].search([]),
#         })

#     @http.route('/purchase_custom/purchase_custom/objects/<model("purchase_custom.purchase_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_custom.object', {
#             'object': obj
#         })