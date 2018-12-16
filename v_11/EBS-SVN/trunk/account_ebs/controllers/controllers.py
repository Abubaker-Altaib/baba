# -*- coding: utf-8 -*-
from odoo import http

# class AccountEbs(http.Controller):
#     @http.route('/account_ebs/account_ebs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_ebs/account_ebs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_ebs.listing', {
#             'root': '/account_ebs/account_ebs',
#             'objects': http.request.env['account_ebs.account_ebs'].search([]),
#         })

#     @http.route('/account_ebs/account_ebs/objects/<model("account_ebs.account_ebs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_ebs.object', {
#             'object': obj
#         })