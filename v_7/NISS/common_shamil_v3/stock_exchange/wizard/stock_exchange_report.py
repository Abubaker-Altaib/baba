# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv,fields

class exchange_report(osv.osv_memory):
    _name = "exchange.report"
    _description = "Exchange Report"
    _columns = {
        'from_date': fields.date('From',required=True), 
        'to_date': fields.date('To',required=True), 
        'company_id': fields.many2one('res.company', 'Company',required=True ),
    }
    _defaults = {

        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'exchange.report', context=c),
    } 

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'exchange.order',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'exchange_report.reports',
            'datas': datas,
            }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
