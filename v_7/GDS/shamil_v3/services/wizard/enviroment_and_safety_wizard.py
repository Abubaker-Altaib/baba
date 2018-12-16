# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

# enviroment and safety wizard Class
class enviroment_and_safty_wizard(osv.osv_memory):

    _name = "enviroment.safety.wizard"
    _description = "Enviroment and safety wizard"

    _columns = {
        'Date_from': fields.date('Date From', required=True), 
        'Date_to': fields.date('Date To', required=True),
        'partner_id':fields.many2one('res.partner', 'Partner'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'environment.and.safety',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enviroment_safety.report',
            'datas': datas,
            }
enviroment_and_safty_wizard()
    
