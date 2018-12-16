# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import decimal
from odoo import netsvc
from odoo import api ,models, fields, models
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp
from datetime import date, datetime
from odoo.tools import ustr, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import models

class bank_letter_report_custom(models.AbstractModel):
    _name = 'report.account_check_printing_custom.bank_letter_report'

    def _get_name(self, data):
        return str(data['form']['name'])

    def _get_bank(self, data):
        name = self.env['account.journal'].browse([data['form']['journal_id'][0]]).name
        return _(name)


    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        bank_letter_report = self.env['ir.actions.report']._get_report_from_name('account_check_printing_custom.bank_letter_report')
        bank_letters = self.env['account.payment'].browse(data['form']['payment_ids'])
        return {
            'doc_ids': self.ids,
            'doc_model': bank_letter_report.model,
            'docs': bank_letters,
            'get_bank':self._get_bank(data),
            'get_name':self._get_name(data),
        }




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
