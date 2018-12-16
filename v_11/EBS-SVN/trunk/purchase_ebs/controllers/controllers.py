# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseEbs(http.Controller):
#     @http.route('/purchase_ebs/purchase_ebs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_ebs/purchase_ebs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_ebs.listing', {
#             'root': '/purchase_ebs/purchase_ebs',
#             'objects': http.request.env['purchase_ebs.purchase_ebs'].search([]),
#         })

#     @http.route('/purchase_ebs/purchase_ebs/objects/<model("purchase_ebs.purchase_ebs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_ebs.object', {
#             'object': obj
#         })