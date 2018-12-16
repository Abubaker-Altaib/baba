# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from itertools import groupby
from operator import itemgetter

class maintenance_stock_report(report_sxw.rml_parse):
    """ To manage Incoming and outgoing of Fuel """
    #globals()['result'] = {'total': 0.0, 'total_remain':0.0, 'total_in':0.0, 'total_out': 0.0}
    globals()['total'] = 0.0
    globals()['total_in'] = 0.0
    globals()['total_out'] = 0.0
    globals()['total_remain'] = 0.0

    def __init__(self, cr, uid, name, context):
        super(maintenance_stock_report, self).__init__(cr, uid, name, context)
        self.name = {'name':''}
        self.localcontext.update({
            'time': time,
            'outgoing_data': self.get_outgoing_data, 
            'both_data': self.get_outgoing_incoming_data,
            'total_data':self._total,
            'total_in':self._total_in,
            'total_out':self._total_out,
            'total_remain':self._total_remain,
            
        })

        globals()['total'] = 0.0
        globals()['total_in'] = 0.0
        globals()['total_out'] = 0.0
        globals()['total_remain'] = 0.0

    def get_outgoing_data(self,data):
        res = []
        globals()['total'] = 0.0
        location_id = data['location_id'][0]
        company_id = data['company_id'][0]
        date_from = data['date_from']
        date_to = data['date_to']
        product_id = data['product_id'] and data['product_id'][0] or False
        pick_type = data['pick_type']
        picking_obj = self.pool.get('stock.picking')
        stock_move_obj = self.pool.get('stock.move')

        conditions = " and pick.maintenance = True " 
        #conditions += pick_type == 'out' and " and pick.type = 'out' " or " and pick.type = 'in' "
        
        if company_id :
          conditions = conditions + " and pick.company_id=(%s)"%company_id 
        
        if location_id :
            if pick_type == 'out':
                conditions += " and (( pick.type = 'out' and move.location_id=(%s) ) or ( pick.type = 'in' and move.location_id=(%s) ) )"%(location_id,location_id)
            if pick_type == 'in':
                conditions += " and (( pick.type = 'out' and move.location_dest_id=(%s) ) or ( pick.type = 'in' and move.location_dest_id=(%s) ) )"%(location_id,location_id) 
          #conditions += pick_type == 'out' and " and pick.location_id=(%s)"%location_id or " and pick.location_dest_id=(%s)"%location_id

        if product_id :
          conditions = conditions + " and pdc.id=(%s)"%product_id


        '''if department_id:
          conditions = conditions + " and pick.department_id=(%s)"%department_id'''
        self.cr.execute( """
            select            p_temp.name as product_name,
                                     pdc.default_code as code,

                                     pdc.id as product_id,
                                     p_temp.categ_id as cat_id,
                                     cat.name as cat_name,
                                     cast(sum(move.product_qty) as integer) as qty
                                     
                                     
                            From stock_move move 
                                left join stock_picking pick on (pick.id=move.picking_id)
                                left join stock_location loc on (loc.id=move.location_id)
                                left join product_product pdc on (move.product_id=pdc.id)
                                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                                left join product_category cat on (p_temp.categ_id=cat.id)


                            
                        where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s)   and pick.state = ('done') 
                       """ + conditions + """ group by pdc.id,p_temp.name ,p_temp.categ_id, cat.name order by qty   """  ,(date_from,date_to)) 
        
        res = self.cr.dictfetchall()
        
        count = 0
        for x in res:
            count += 1
            x['count'] = count
            globals()['total'] += x['qty']
            # to get remaining quantity
            c = {}
            c['location'] = location_id
            c['from_date'] = date_from
            c['to_date'] = date_to
            product = self.pool.get('product.product').browse(self.cr, self.uid, x['product_id'], context=c)
            x['qty_available'] = int(product.qty_available)
        
        return res


    def get_outgoing_incoming_data(self,data):
        res = []
        res2 = []

        res3 = []
        globals()['total'] = 0.0
        globals()['total_in'] = 0.0
        globals()['total_out'] = 0.0
        globals()['total_remain'] = 0.0
        
        location_id = data['location_id'][0]
        company_id = data['company_id'][0]
        date_from = data['date_from']
        date_to = data['date_to']
        product_id = data['product_id'] and data['product_id'][0] or False
        pick_type = data['pick_type']
        picking_obj = self.pool.get('stock.picking')
        stock_move_obj = self.pool.get('stock.move')

        conditions = " and pick.maintenance = True "
        conditions2 = " and pick.maintenance = True " 
        
        if company_id :
          conditions += " and pick.company_id=(%s)"%company_id 
          conditions2 += " and pick.company_id=(%s)"%company_id 
        
        if location_id :
          conditions += " and (( pick.type = 'out' and move.location_id=(%s) ) or ( pick.type = 'in' and move.location_id=(%s) ) )"%(location_id,location_id)
          conditions2 += " and (( pick.type = 'out' and move.location_dest_id=(%s) ) or ( pick.type = 'in' and move.location_dest_id=(%s) ) )"%(location_id,location_id)
          #conditions += " and pick.location_id=(%s)"%location_id 
          #conditions2 += " and pick.location_dest_id=(%s)"%location_id 

        if product_id :
          conditions += " and pdc.id=(%s)"%product_id
          conditions2 += " and pdc.id=(%s)"%product_id


        '''if department_id:
          conditions = conditions + " and pick.department_id=(%s)"%department_id'''
        self.cr.execute( """
            select            p_temp.name as product_name,
                                     pdc.default_code as code,

                                     pdc.id as product_id,
                                     p_temp.categ_id as cat_id,
                                     cat.name as cat_name,
                                     cast(sum(move.product_qty) as integer) as qty_out
                                     
                                     
                            From stock_move move 
                                left join stock_picking pick on (pick.id=move.picking_id)
                                left join product_product pdc on (move.product_id=pdc.id)
                                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                                left join product_category cat on (p_temp.categ_id=cat.id)


                            
                        where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s)   and pick.state = ('done') 
                       """ + conditions + """ group by pdc.id,p_temp.name ,p_temp.categ_id, cat.name order by qty_out   """  ,(date_from,date_to)) 
        res = self.cr.dictfetchall()
        
        self.cr.execute( """
            select            p_temp.name as product_name,
                                     pdc.default_code as code,

                                     pdc.id as product_id,
                                     p_temp.categ_id as cat_id,
                                     cat.name as cat_name,
                                     cast(sum(move.product_qty) as integer) as qty_in
                                     
                                     
                            From stock_move move 
                                left join stock_picking pick on (pick.id=move.picking_id)
                                left join product_product pdc on (move.product_id=pdc.id)
                                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                                left join product_category cat on (p_temp.categ_id=cat.id)


                            
                        where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s)   and pick.state = ('done') 
                       """ + conditions2 + """ group by pdc.id,p_temp.name ,p_temp.categ_id, cat.name order by qty_in   """  ,(date_from,date_to)) 
        res2 = self.cr.dictfetchall()


        result = res + res2
        result = sorted(result, key=lambda x: x['product_id'])
        grouped_lines = dict((k, [v for v in itr]) for k, itr in groupby(result, itemgetter('product_id')))

        product_list = []
        count = 0

        for x in grouped_lines.keys():
            new_dict = {}
            count = 0
            for y in grouped_lines[x]:
                count += 1
                if count == 1:
                    new_dict = {
                            'product_name': y['product_name'],
                            'code': y['code'],
                            'cat_name': y['cat_name'],
                            'product_id': y['product_id']
                        }
                if 'qty_in' in y:
                    new_dict['qty_in'] = y['qty_in']

                if 'qty_out' in y:
                    new_dict['qty_out'] = y['qty_out']

            if new_dict:
                res3.append(new_dict)


        count = 0
        for x in res3:
            count += 1
            x['count'] = count
            x['qty_in'] = 'qty_in' in x and x['qty_in'] or 0.0
            x['qty_out'] = 'qty_out' in x and x['qty_out'] or 0.0
            globals()['total_in'] += x['qty_in']
            globals()['total_out'] += x['qty_out']
            # to get remaining quantity
            c = {}
            c['location'] = location_id
            c['from_date'] = date_from
            c['to_date'] = date_to
            product = self.pool.get('product.product').browse(self.cr, self.uid, x['product_id'], context=c)
            x['qty_available'] = int(product.qty_available)
            globals()['total_remain'] += product.qty_available
        
        return res3


    def _total(self,data):
        return int(globals()['total'])

    def _total_in(self,data):
        return int(globals()['total_in'])

    def _total_out(self,data):
        return int(globals()['total_out'])

    def _total_remain(self,data):
        return int(globals()['total_remain'])


    

report_sxw.report_sxw('report.maintenance_stock_report','stock.picking','addons/vehicles_maintenance/report/maintenance_stock_report.rml',parser=maintenance_stock_report, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
