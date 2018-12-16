import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class CertificateQuotation(models.AbstractModel):
	_name = 'report.sale_custom.report_certificate_invoice'

	
	@api.model
	def get_report_values(self, docids, data):
	
		order_id=self.env['sale.order'].search([('id','=',data['context']['active_id'])])
 
		docargs = {
				'docs':order_id,
				
			}
		return docargs