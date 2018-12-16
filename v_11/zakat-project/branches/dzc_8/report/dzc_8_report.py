from datetime import datetime
from odoo import models,fields,api, _


class Dzc8Report(models.AbstractModel):
    _name = 'report.dzc_8.iban_alsabil_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['zakat.dzc8'].search([('id', 'in', docids)])
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zakat.dzc8',
            'docs': docs,

                    }
        return docargs


class IbanAlsabilPayment(models.AbstractModel):
    _name = 'report.dzc_8.iban_alsabil_payment_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['zakat.dzc8.payment'].search([('id', 'in', docids)])
        date = datetime.strftime(datetime.today(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zakat.dzc8.payment',
            'docs': docs,
            'date': date,

                    }
        return docargs


class Dzc8TransportCompaniesReport(models.AbstractModel):
    _name = 'report.dzc_8.transport_companies_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['dzc8.transport.company'].search([('id', 'in', docids)])
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'dzc8.transport.company',
            'docs': docs,

                    }
        return docargs
