from odoo import models, api, _


class RatificationReport(models.AbstractModel):
    _name = 'report.zakat_base.ratification_list_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['zakat.ratification'].search([('id', 'in', docids)])
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zakat.ratification',
            'docs': docs,

                    }
        return docargs