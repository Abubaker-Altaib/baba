# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from datetime import datetime
from tools.translate import _


class loan_candidates(osv.osv_memory):
    _name = "loan_candidates_wizard"

    _columns = {
        'loan_id': fields.many2one('hr.loan', string="Loan"),
        'num': fields.integer(string="Number of Candidates"),
    }

    def print_report(self, cr, uid, ids, context={}):
        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.loan_candidates.report', 'datas': data}
            
