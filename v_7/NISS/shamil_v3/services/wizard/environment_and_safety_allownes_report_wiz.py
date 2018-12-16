
# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields
import time

class environment_and_safety_allownes_report_wiz(osv.osv_memory):

    _name = "environment.and.safety.allownes.report.wiz"
    _description = "Environment and Safety Allownes"

    def _get_months(self, cr, uid, context):
       months=[(str(n),str(n)) for n in range(1,13)]
       return months
     
    _columns = {
        'month': fields.selection(_get_months,'Month', select=True),
        'year': fields.integer('Year', size=32,),
        'partner_id':fields.many2one('res.partner', 'Partner'),
    }

    _defaults = {
        'year': int(time.strftime('%Y'))

                }
    
    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'services.contracts.archive',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'environment.and.safety.allownes.report',
            'datas': datas,
            }
environment_and_safety_allownes_report_wiz()
    
