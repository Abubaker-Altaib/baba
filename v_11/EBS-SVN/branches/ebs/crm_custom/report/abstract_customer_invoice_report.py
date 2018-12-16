import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CustomerInvoiceReport(models.AbstractModel):
    _name = 'report.crm_custom.template_customer_invoice_report'

    @api.model
    def get_report_values(self, docids, data):
   
        service_id = data['data']['service_id']
        center_id = data['data']['center_id']
        customer_id = data['data']['customer_id']
        state = data['data']['state']
        date_from = data['data']['date_from']
        date_to = data['data']['date_to']



        order_domain = [('customer_invoice','=',True)]

        if center_id:
            order_domain.append(('center_id', '=', center_id[0]))

        if customer_id:
            order_domain.append(('partner_id', '=', customer_id[0]))

        if state:
            order_domain.append(('state', '=', state))


        # rase Eror if date_from max
        if date_from and date_to:
            if date_from > date_to:
                raise UserError(_('Start Date must be equal to or less than Date To'))

        #print information with date_from 
        if date_from :
            order_domain.append(('date_order', '>=', date_from))

         #print information with date_to
        if date_to:
            order_domain.append(('date_order', '<=', date_to))

        #print information without date_from and date_to
        invoices = self.env['sale.order'].search(order_domain)
       
        invoices_line = []
        order_by_customer = []
        if service_id:
            invoices_line = self.env['sale.order.line'].search([('product_id','=',service_id[0]),
                                                                ('order_id','in',[g.id for g in invoices])])
            order_by_customer = list(set([g.order_id.partner_id.id for g in invoices_line]))

        else:
            invoices_line = self.env['sale.order.line'].search([
                                ('order_id','in',[g.id for g in invoices])])
            order_by_customer = list(set([g.partner_id.id for g in invoices]))
         
        upper = []
        for index in order_by_customer:
            inner = [g for g in invoices_line if g.order_id.partner_id.id == index]
            upper.append(inner)


        if service_id:
            docargs = {
                'doc_model': 'sale.order',
                'upper': upper,
                'user': 'user',
                'product_id': False,
                'service_id' : service_id[0]
            }

        else:
            docargs = {
                'doc_model': 'sale.order',
                'upper': upper,
                'user': 'user',
                'product_id': True,
                'service_id' : False
            }
        
        return docargs
