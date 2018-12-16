# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################



#from odoo.osv import  osv,orm
from odoo import api, fields, models, exceptions,_

class enrich_report_wiz(models.TransientModel):
    """ To manage enrich report wizard """
    _name = "enrich.report.wiz"

    _description = "Enrich Report Wizard"

    month= fields.Selection([(str(n),str(n)) for n in range(1,13)],'Month', required=True)
    year= fields.Integer('Year',size=32, required=True)
    company_id= fields.Many2one('res.company', 'Company', required= True, default=lambda self: self.env['res.company'].browse(self._uid).partner_id)
    payment_enrich= fields.Many2one('payment.enrich', 'Payment Enrich', required=True, ondelete='cascade')

    def print_report(self, data):

        self.ensure_one()

        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'payment.enrich',
            'form': data['payment_enrich']
        }
        return self.env.ref('enrich.enrich_report_action').report_action(self, data=datas)
