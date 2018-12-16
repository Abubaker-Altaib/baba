from odoo import models, api,exceptions, _


class KhalwaSupportReport(models.AbstractModel):
    _name = 'dzc_4_5.khalwa_support_repport'

    @api.model
    def get_report_values(self, docids):
        docs = self.env['khalwa.support.order'].search([('id', '=', docids)])
        for x in docs:
            print ('==============================================',x.place_id.pre_support)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'khalwa.support.order',
            'docs': docs,

                    }
        return docargs
