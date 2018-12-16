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

class report_12c_niss(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_12c_niss, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal':self._get_qtytotal,
            'line':self._getShop,
            'serials':self._getSerials,
            'line2':self._getdata
        })
    def _getdata(self,pick):
        self.cr.execute("""
               select
                    (pr.name_template) as product_name,
                    (pr.default_code) as default_code,
                    (sm.product_qty) as quantity,
                    (sm.product_id) as product_id,
                    (sm.picking_id) as picking_id,
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

    def _getSerials(self, pick_id,product_id):
        serials=''
 
        result=[]
        asset_obj = self.pool.get('account.asset.asset') 
        log_obj = self.pool.get('asset.log')  
        log_ids=log_obj.search(self.cr, self.uid, [('picking_id','=',pick_id)])
 
           
        asset_ids=asset_obj.search(self.cr, self.uid, [('asset_log_ids','in',log_ids),('product_id','=',product_id)])
        for asset in  asset_obj.browse(self.cr,self.uid,asset_ids):
            serials=serials+" "+","+str(asset.serial)
        result.append({
                'serials': serials,      
                     })

        return result


report_sxw.report_sxw('report.report_12c_niss', 'stock.picking', 'addons/stock_niss/report/report_12c_niss.rml' ,parser=report_12c_niss,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
        
