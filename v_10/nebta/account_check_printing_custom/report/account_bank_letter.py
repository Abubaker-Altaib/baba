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
from odoo.report import report_sxw

class account_bank_letter(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
      
        super(account_bank_letter, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_bank':self._get_bank,
            'get_name':self._get_name,
        })
        self.context = context;
    
    def set_context(self, objects, data, ids, report_type=None):
        objects = self.env['account.payment'].browse(self.cr, self.uid, self.context['active_id'])
        return super(account_bank_letter, self).set_context(objects, data, ids, report_type=report_type) 
    
    def _get_name(self, data):
        print'name>>>>>>>>>>>>>>>>>>>>>>',type(str(data['form']['name']))
        return str(data['form']['name'])

    def _get_bank(self, data):
        name = self.env['account.journal'].browse(self.cr, self.uid,[data['form']['journal_id'][0]]).name
        return _(name)


  

class budget_report_custom(models.AbstractModel):
    _name = 'report.account_check_printing_custom.bank_letter_report'
    _inherit = 'report.abstract_report'
    _template = 'account_check_printing_custom.bank_letter_report'
    _wrapped_report_class = account_bank_letter



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
