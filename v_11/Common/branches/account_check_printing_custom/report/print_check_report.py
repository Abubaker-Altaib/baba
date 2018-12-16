# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
import decimal
from odoo import netsvc
from odoo import api ,models, fields
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp
from datetime import date, datetime
from odoo.tools import ustr, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, ValidationError

class print_check_report_custom(models.AbstractModel):
    _name = 'report.account_check_printing_custom.print_check_custom'
    def func(self, form):
        date = str(form['date'])
        beneficiary = str(form['beneficiary'])
        amount = str(form['amount'])
        number = str(form['number'])
        release_at = str(form['release_at'])
        description = str(form['description'])
        font_size = form['font_size']
            
        date_dim = date.split(',')
        amount_dim = amount.split(',')
        number_dim = number.split(',')
        beneficiary_dim = beneficiary.split(',')
        release_at_dim = release_at.split(',')
        description_dim = description.split(',')

        result = []
        res = {
                'font': "font-size:"+str(font_size)+"px",
                'date': form['payment_date'],
                'partner': form['partner_name'],
                'amount': form['check_amount_in_words'],
                'number': form['amount_money'],
                'release_at': form['release_at_name'],
                'description': form['description_name'],
                'date_w': int(date_dim[0]), 
                'date_h': int(date_dim[1]), 
                'amount_w': int(amount_dim[0]), 
                'amount_h': int(amount_dim[1]), 
                'number_w': int(number_dim[0]),
                'number_h': int(number_dim[1]),
                'partner_w': int(beneficiary_dim[0]),
                'partner_h': int(beneficiary_dim[1]),
                'release_at_w': int(release_at_dim[0]),
                'release_at_h': int(release_at_dim[1]),
                'description_w': int(description_dim[0]),
                'description_h': int(description_dim[1]),     
        }
        result.append(res)
        return result

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        print_report = self.env['ir.actions.report']._get_report_from_name('account_check_printing_custom.print_check_custom')
        payments = self.env['account.payment'].browse(self.ids)
        return {
            'doc_ids': self.ids,
            'doc_model': print_report.model,
            'docs': payments,
            'func': self.func(data['form']),
        }

 
    
   


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
