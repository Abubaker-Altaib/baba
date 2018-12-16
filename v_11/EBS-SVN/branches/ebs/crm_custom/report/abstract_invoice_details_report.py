import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InvoiceDetailsReport(models.AbstractModel):
    _name = 'report.crm_custom.template_invoice_details_report'

    @api.model
    def get_report_values(self, docids, data):

        order_id=self.env['sale.order'].search([('id','=',data['context']['active_id'])])
 
        docargs = {
                'docs':order_id,
                
            }
        return docargs