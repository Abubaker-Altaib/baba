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
from odoo.report import report_sxw

class print_check_report_custom(report_sxw.rml_parse):  
    def __init__(self, cr, uid, name, context):
        super(print_check_report_custom, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'func': self.func,
            #'get_total': self.func_total,
            #'time': time,
        })
        self.context = context

    
    def func(self, object, form):
        #journal= self.env['account.journal'].browse(self.cr, self.uid, [form['journal_id'][0]])
        #journal_dim = journal.check_dimension
        #if journal_dim:
        date = str(form['date'])
        beneficiary = str(form['beneficiary'])
        amount = str(form['amount'])
        number = str(form['number'])
        font_size = form['font_size']
            
        date_dim = date.split(',')
        amount_dim = amount.split(',')
        number_dim = number.split(',')
        beneficiary_dim = beneficiary.split(',')

        result = []
        res = {
                'font': "font-size:"+str(font_size)+"px",
                'date': form['payment_date'],
                'partner': form['partner_name'],
                'amount': form['check_amount_in_words'],
                'number': form['amount_money'],
                'date_w': int(date_dim[0]), 
                'date_h': int(date_dim[1]), 
                'amount_w': int(amount_dim[0]), 
                'amount_h': int(amount_dim[1]), 
                'number_w': int(number_dim[0]),
                'number_h': int(number_dim[1]),
                'partner_w': int(beneficiary_dim[0]),
                'partner_h': int(beneficiary_dim[1]),   
        }
        result.append(res)
        return result
        #else:
        #    raise UserError(_("Please add check dimensions to the selected journal in order to print a check."))


class budget_report_custom(models.AbstractModel):
    _name = 'report.account_check_printing_custom.print_check_custom'
    _inherit = 'report.abstract_report'
    _template = 'account_check_printing_custom.print_check_custom'
    _wrapped_report_class = print_check_report_custom

# ---------------------------------------------------------
# Utils
# ---------------------------------------------------------

'''def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

def strToDatetime(strdate):
    return datetime.strptime(strdate, DEFAULT_SERVER_DATE_FORMAT)'''
 
    
   


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
