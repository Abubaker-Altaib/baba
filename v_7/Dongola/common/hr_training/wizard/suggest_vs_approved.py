# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import fields, osv

class suggest_approved_compare(osv.osv_memory):
    _name = "suggest.approved.compare"

    _columns = {
        'plan_id' : fields.many2one('hr.training.plan', 'Plan', required=True),
        'traing_place': fields.selection((('inside', 'Inside'), ('outside', 'Outside')), 'Place',required=True,),
   		 }
    
    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.employee.training',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'suggest_vs_approved',
            'datas': datas,
            }
suggest_approved_compare()
