# -*- coding: utf-8 -*-
from odoo import http

# class BaseCustom(http.Controller):
#     @http.route('/base_custom/base_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_custom/base_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_custom.listing', {
#             'root': '/base_custom/base_custom',
#             'objects': http.request.env['base_custom.base_custom'].search([]),
#         })

#     @http.route('/base_custom/base_custom/objects/<model("base_custom.base_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_custom.object', {
#             'object': obj
#         })