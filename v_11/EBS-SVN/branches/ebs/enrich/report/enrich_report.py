# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class enrich_report(models.AbstractModel):
    """ To manage enrich report """
    _name = 'report.enrich.enrich_report_tamplate'

    @api.model
    def get_report_values(self, docids, data):

        payments = self.env['payment.enrich'].search([('id','=',data['form'][0])])

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'payment.enrich',
            'docs': payments,
            }
        return  docargs