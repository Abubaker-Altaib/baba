# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class EnrichSummaryReport(models.AbstractModel):
    _name = 'report.enrich.view_enrich_report'

    @api.model
    def get_report_values(self, docids, data):
        
        cont=data['context']
        
        enrich_lines = self.env['payment.enrich.lines'].search([('id', '=', data['id'] )])
        user = self.env['res.users'].search([('id','=',cont['uid'])]).name
        print("dddddddddddddddddddddd",cont)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'payment.enrich.lines',
            'docs': enrich_lines,
            'user':user
            }
      
        return  docargs

    