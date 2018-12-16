# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from osv import osv, fields
from tools.translate import _



class create_partial_picking_report(osv.osv_memory):
    """
    Report For Read partial Picking Which Created For Particular PO """
    _name = "create.partial.picking.report"
    _description = "partial Picking"
    _columns = {
                'purchase_order_ref': fields.many2one('purchase.order', 'Purchase order', readonly=True),
                'picking_id': fields.many2one('stock.picking', 'Stock Picking', ),
                'current_date': fields.date('Current Date', readonly=True),
                }
    
    _defaults = {
                'purchase_order_ref':lambda cr,uid,ids,context:context['active_id'],
                'current_date': lambda *a: time.strftime('%Y-%m-%d'),
                }
    
    
    
    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'purchase.order',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'create_partial_picking_report',
            'datas': datas,
            }

