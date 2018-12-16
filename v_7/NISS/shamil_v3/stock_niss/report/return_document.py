# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp.osv import osv,fields,orm
from tools.translate import _

class return_document(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(return_document, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal':self._get_qtytotal,
            'line':self._getShop,
            'line2':self._getdata
        })
        self.context = context 
    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('stock.picking').browse(self.cr, self.uid, ids, self.context):
            if obj.state != 'done':             
               raise osv.except_osv(_('Error!'), _('You cannot open this report now , please recived this order firstly'))
        return super(return_document, self).set_context(objects, data, ids, report_type=report_type)
    def _getdata(self,pick):
        self.cr.execute("""
               select
                    (pr.name_template) as product_name,
                    (pr.default_code) as default_code,
                    (sm.product_qty) as quantity,
                    (u.name) as product_uom,
                    (ol.price_unit) as price_unit,
                    (pa.lang) as lang,
                    (pa.name) as partner_name
                    from stock_move sm
                    left join stock_picking sp on (sm.picking_id=sp.id and sm.state='done')
                    left join purchase_order po on (sp.purchase_id=po.id)
                    left join purchase_order_line ol on (po.id = ol.order_id and sm.product_id =ol.product_id)
                    left join product_uom u on (u.id = ol.product_uom)
                    left join product_product pr on (sm.product_id =pr.id)
                    left join res_partner pa on (po.partner_id =pa.id)          
                     where sp.id =%s
                  order by sm.id
        """%(pick,)) 
        res = self.cr.dictfetchall()
        return res

    def _get_qtytotal(self,move_lines):
        total = 0.0
        uom = move_lines[0].product_uom.name
        for move in move_lines:
            total+=move.product_qty
        return {'quantity':total,'uom':uom}

    def _getShop(self, ids):
        p = self.pool.get('stock.picking')
        pick_id=p.browse(self.cr, self.uid,[ids['id']])[0]
        picking_id = pick_id.id
        purchase_id = pick_id.purchase_id.id

        self.cr.execute('SELECT  number From account_invoice where id=%s'%(i)) 
        res = self.cr.dictfetchall()
        return True

report_sxw.report_sxw('report.return_document', 'stock.picking', 'addons/stock_niss/report/return_document.rml' ,parser=return_document,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
        
