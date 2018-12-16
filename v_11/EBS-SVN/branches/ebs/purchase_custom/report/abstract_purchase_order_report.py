import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrderReport(models.AbstractModel):
    _name = 'report.purchase_custom.template_purchase_order_report'

    @api.model
    def get_report_values(self, docids, data):

        date_from = data['data']['date_from']
        date_to = data['data']['date_to']
        state = data['data']['state']
        vendor_id = data['data']['vendor_id']
        product_id = data['data']['product_id']
        dept_id = data['data']['dept_id']

        #init order domain
        order_domain = []

        if date_from:
            order_domain.append(('date_order', '>=', date_from))

        if date_to:
            order_domain.append(('date_order', '<=', date_to))

        if state:
            order_domain.append(('state', '=', state))
        else:
            order_domain.append(('state', 'not in',
                                 ('draft', 'sent', 'approve_rfq', 'approve', 'review', 'purchase_rfq', 'cancel_rfq','approve2')))

        if vendor_id:
            order_domain.append(('partner_id', '=', vendor_id[0]))

        if dept_id:
            order_domain.append(('department_id', '=', dept_id[0]))

        purchase_orders = self.env['purchase.order'].search(order_domain)

        check_list = []
        if product_id:
            for order in purchase_orders:
                check = False
                for line in order.order_line:
                    if line.product_id.id == product_id[0]:
                        check = True
                check_list.append(check)

        # if lang not arabic then don't set dir to rtl in report CSS
        lang = 'en'

        if self._context.get('lang', 'en')[0:2] != 'en':
            lang = 'ar'

        if product_id:

            docargs = {
                #   'doc_ids': self.ids,
                'doc_model': 'purchase.order',
                'docs': purchase_orders,
                'user': 'user',
                'check_list': check_list,
                'product_id': product_id[0],
                'date_from': date_from,
                'date_to': date_to,
                'lang': lang

            }
        else:
            docargs = {
                #   'doc_ids': self.ids,
                'doc_model': 'purchase.order',
                'docs': purchase_orders,
                'user': 'user',
                'date_from': date_from,
                'product_id': False,
                'date_to': date_to,
                'lang': lang

            }

        return docargs
