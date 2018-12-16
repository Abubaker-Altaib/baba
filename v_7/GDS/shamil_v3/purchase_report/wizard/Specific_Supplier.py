# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class Specific_Supplier(osv.osv_memory):
    _name = "specific.supplier"
    _description = "Specific Supplier wizard"
    _columns = {
        'Date_from': fields.date('Date From',required=True), 
        'Date_to': fields.date('Date To',required=True), 
        'partner_name': fields.many2one('res.partner', 'Partner',required=True, ),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'Specific_Supplier.report',
            'datas': datas,
            }
Specific_Supplier()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
