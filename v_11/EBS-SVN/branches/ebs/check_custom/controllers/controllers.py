# -*- coding: utf-8 -*-
from odoo import http

# class CheckCustom(http.Controller):
#     @http.route('/check_custom/check_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/check_custom/check_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('check_custom.listing', {
#             'root': '/check_custom/check_custom',
#             'objects': http.request.env['check_custom.check_custom'].search([]),
#         })

#     @http.route('/check_custom/check_custom/objects/<model("check_custom.check_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('check_custom.object', {
#             'object': obj
#         })