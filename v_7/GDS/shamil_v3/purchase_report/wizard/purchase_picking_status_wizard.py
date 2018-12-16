# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class purchase_picking_status(osv.osv_memory):
    _name = "purchase.picking.status"
    _description = "Purchase Picking Status"

    STATE_SELECTION = [
        ('invoiced', 'تم انشاء الفاتورة'),
        ('2binvoiced', 'لم يتم انشاء فاتورة'),
    ]

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
        'state': fields.selection(STATE_SELECTION, 'State', help="The state of the contract.", select=True), 
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'po_status.report',
            'datas': datas,
            }
purchase_picking_status()
