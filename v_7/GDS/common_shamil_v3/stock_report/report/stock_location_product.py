# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

class stock_location_product_reports(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(stock_location_product_reports, self).__init__(cr, uid, name, context)
        self.price_total = 0.0
        self.grand_total = 0.0
        self.localcontext.update({
            'time': time,
            'lines':self.lines,
            'price_total': self._price_total,
            'grand_total_price':self._grand_total,
            'get_location':self.get_location,
            'product_get_report':self._product_get_report,
        })
    def _product_get_report(self, cr, uid, ids, product_ids=False,
            context=None, recursive=False):
        """ Finds the product quantities and price for particular location.
        @param product_ids: Ids of product
        @param recursive: True or False
        @return: Dictionary of values
        
        """
        if context is None:
            context = {}
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        products = product_obj.browse(cr, uid, product_ids, context=context)
        products_by_uom = {}
        products_by_id = {}
        for product in products:
            products_by_uom.setdefault(product.uom_id.id, [])
            products_by_uom[product.uom_id.id].append(product)
            products_by_id.setdefault(product.id, [])
            products_by_id[product.id] = product
        result = {}
        result['product'] = []
        for id in ids:
            quantity_total = 0.0
            total_price = 0.0
            for uom_id in products_by_uom.keys():
                from_date = context.get('from_date',False)
                to_date = context.get('to_date',False)
                fnc = location_obj._product_get
                if recursive:
                    fnc = location_obj._product_all_get
                ctx = context.copy()
                ctx['uom'] = uom_id
                ctx['to_date'] =from_date
                ctx['from_date'] =False
                qty = fnc(cr, uid, id, [x.id for x in products_by_uom[uom_id]],
                        context=ctx)
                for product_id in qty.keys():
                    incoming_qty=0.0
                    outgoing_qty=0.0
                    move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',id),('location_id','=',id),('state','=','done'),('type','!=',False),('product_id','=',product_id)], context=context)
 
                    if from_date and to_date:
                        move_ids = move_obj.search(cr, uid, [('id','in',move_ids),('date','>=',from_date),('date','<=',to_date)], context=context)
                    elif from_date:
                        move_ids = move_obj.search(cr, uid, [('id','in',move_ids),('date','>=',from_date)], context=context)
                    elif to_date:
                        move_ids = move_obj.search(cr, uid, [('id','in',move_ids),('date','<=',to_date)], context=context)
                    for move in move_obj.browse(cr, uid, move_ids, context=context):
                        if move.location_dest_id.id == id:
                            incoming_qty += uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)
                        else:
                            outgoing_qty += uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)
                    move = context.get('move','moved')
                    if move=='moved':
                        if incoming_qty==outgoing_qty==0.0:
                            continue
                    if move=='notmoved':
                        if incoming_qty or outgoing_qty != 0.0:
                            continue
                    product = products_by_id[product_id]
                    quantity_total += qty[product_id]
                    ctxx = context.copy()
                    ctxx.update({'to_date':False,'from_date':False})
                    qty_available=location_obj._product_get(cr, uid, id, [product_id], context=ctxx)[product_id] 

                    if incoming_qty==outgoing_qty==qty_available==0.0:
                        continue
                    prod_qty= qty[product_id]
                    if from_date==False:
                        prod_qty=0.0
                    # Compute based on pricetype
                    # Choose the right filed standard_price to read
                    amount_unit = product.price_get('standard_price', context=context)[product.id]
                    price =qty_available * amount_unit
                    total_price += price
                    result['product'].append({
                        'price': amount_unit,
                        'prod_name': product.name,
                        'code': product.default_code, # used by lot_overview_all report!
                        'uom': product.uom_id.name,
                        'prod_qty': prod_qty,
                        'price_value': price,
                        'incoming_qty': incoming_qty ,
                        'outgoing_qty': outgoing_qty ,
                        'qty_available':qty_available or 0.0,
                    
                    })
        result['total'] = quantity_total
        result['total_price'] = total_price
        return result

    def get_location(self,data):
        result = []
        location_obj = self.pool.get('stock.location')
        if data['form']['location_id']:
            location_id=data['form']['location_id'][0] 
            if data['form']['recursive']:
                location_ids = location_obj.search(self.cr, self.uid, [('location_id',
                             'child_of', [location_id])], order="id")
            else:
                location_ids = [location_id]
        else :
            location_ids = location_obj.search(self.cr, self.uid, [])
        result = location_obj.browse(self.cr,self.uid, location_ids)
        return result

    def lines(self, data,location_id):
        location_obj = self.pool.get('stock.location')
        res=self._product_get_report(self.cr, self.uid,[location_id], data['product_ids'],context=data['context'], recursive=False)
        res['location_name'] =location_obj.read(self.cr, self.uid, [location_id],['complete_name'])[0]['complete_name']
        self.price_total = 0.0
        self.price_total += res['total_price']
        self.grand_total += res['total_price']
        return [res]

    def _price_total(self):
        return self.price_total

    def _grand_total(self):
        return self.grand_total
               
report_sxw.report_sxw('report.stock.location.product2', 'product.product', 'addons/stock_report/report/stock_location_product.rml' ,parser=stock_location_product_reports ,header='custom landscape')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
