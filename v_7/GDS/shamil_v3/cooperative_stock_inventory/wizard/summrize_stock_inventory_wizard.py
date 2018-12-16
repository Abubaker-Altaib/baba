# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class stock_all_inventory(osv.osv_memory):
    _name = "stock.all.inventory"
    _description = "Summrize Stock Inventory"
    _columns = {
        'Date_from': fields.date('Date From',required=True), 
        'Date_to': fields.date('Date To',required=True), 
        'location_id': fields.many2one('stock.location', 'location',),
        'state': fields.selection( (('draft', 'Draft'), ('cancel','Cancelled'), ('confirm','Confirmed'),('done', 'Done')), 'State'),
    }

    def onchange_date(self, cr, uid,ids,Date_from,Date_to,context=None):
        if Date_from and Date_to:
           if Date_from >= Date_to:
                 values={'Date_from':False,'Date_to':False,}
                 warning={'title': _('Warning'), 'message': _('The start date must be anterior to the end date.') }
                 return {'value':values,'warning':warning}
                 
        return {}

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'all_inventory',
            'datas': datas,
            }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
