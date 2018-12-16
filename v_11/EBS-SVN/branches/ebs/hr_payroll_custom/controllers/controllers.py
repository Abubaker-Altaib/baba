# -*- coding: utf-8 -*-
from odoo import http

# class PayrollCustom(http.Controller):
#     @http.route('/payroll_custom/payroll_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payroll_custom/payroll_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payroll_custom.listing', {
#             'root': '/payroll_custom/payroll_custom',
#             'objects': http.request.env['payroll_custom.payroll_custom'].search([]),
#         })

#     @http.route('/payroll_custom/payroll_custom/objects/<model("payroll_custom.payroll_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payroll_custom.object', {
#             'object': obj
#         })