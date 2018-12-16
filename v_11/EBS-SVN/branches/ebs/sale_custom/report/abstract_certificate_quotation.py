import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CertificateQuotation(models.AbstractModel):
    _name = 'report.sale_custom.template_certificate_quotation'

    @api.model
    def get_report_values(self, docids, data):

        

        current_id = data['context']['active_id']

        current_certificate_lines=self.env['sale.order.line'].search([('order_id','=',current_id)])

        certificate_ids_list = []
        for line in current_certificate_lines :
        	certificate_ids_list.append(line.sale_certificate_id.id)

        
        certificate_ids = self.env['sale.certificate'].search([('id','in',certificate_ids_list)])

        current_sale_order = self.env['sale.order'].search([('id','=',current_id)])
       
        docargs = {
                'docs':current_certificate_lines,
                'certificate_ids':certificate_ids,
                'docss':current_sale_order 
               
                
            
            }
        
        return docargs