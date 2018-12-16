# -*- coding: utf-8 -*-
from odoo import http

# class HrLoan(http.Controller):
#     @http.route('/hr_loan/hr_loan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_loan/hr_loan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_loan.listing', {
#             'root': '/hr_loan/hr_loan',
#             'objects': http.request.env['hr_loan.hr_loan'].search([]),
#         })

#     @http.route('/hr_loan/hr_loan/objects/<model("hr_loan.hr_loan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_loan.object', {
#             'object': obj
#         })