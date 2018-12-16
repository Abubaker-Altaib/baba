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

class fuel_stock_report(report_sxw.rml_parse):
    """ To manage Incoming and outgoing of Fuel """
    #globals()['result'] = {'total': 0.0, 'total_remain':0.0, 'total_in':0.0, 'total_out': 0.0}
    globals()['total'] = 0.0
    globals()['total_in'] = 0.0
    globals()['total_out'] = 0.0
    globals()['total_remain'] = 0.0

    def __init__(self, cr, uid, name, context):
        super(fuel_stock_report, self).__init__(cr, uid, name, context)
        self.name = {'name':''}
        self.localcontext.update({
            'time': time,
            'outgoing_data': self.get_outgoing_data, 
            'both_data': self.get_outgoing_incoming_data,
            'total_data':self._total,
            'total_in':self._total_in,
            'total_out':self._total_out,
            'total_remain':self._total_remain,
            'get_bump': self._get_bump,
            
        })

        globals()['total'] = 0.0
        globals()['total_in'] = 0.0
        globals()['total_out'] = 0.0
        globals()['total_remain'] = 0.0
    def _get_bump(self, id):
        location_obj = self.pool.get('stock.location')
        return location_obj.read(self.cr, self.uid, [id],['name'])[0]['name']
    def get_outgoing_data(self,data,location):
        res = []
        globals()['total'] = 0.0
        location_id = location
        company_id = data['company_id'][0]
        date_from = data['date_from']
        date_to = data['date_to']
        product_id = data['product_id'] and data['product_id'][0] or False
        pick_type = data['pick_type']
        picking_obj = self.pool.get('stock.picking')
        stock_move_obj = self.pool.get('stock.move')

        conditions = " and pick.fuel_ok = True " 
        #conditions += pick_type == 'out' and " and pick.type = 'out' " or " and pick.type = 'in' "
        
        if company_id :
          conditions = conditions + " and pick.company_id=(%s)"%company_id 
        
        if location_id :
            if pick_type == 'out':
                conditions += " and (( pick.type = 'out' and move.location_id=(%s) ) or ( pick.type = 'in' and move.location_id=(%s) ) )"%(location_id,location_id)
            if pick_type == 'in':
                conditions += " and (( pick.type = 'out' and move.location_dest_id=(%s) ) or ( pick.type = 'in' and move.location_dest_id=(%s) ) )"%(location_id,location_id) 
          #conditions += pick_type == 'out' and " and move.location_id=(%s)"%location_id or " and move.location_dest_id=(%s)"%location_id

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
            x['qty_available'] = str(int(product.qty_available))
        
        return res


    def get_outgoing_incoming_data(self,data,location):
        res = []
        res2 = []

        res3 = []
        globals()['total'] = 0.0
        globals()['total_in'] = 0.0
        globals()['total_out'] = 0.0
        globals()['total_remain'] = 0.0
        
        location_id = location
        company_id = data['company_id'][0]
        date_from = data['date_from']
        date_to = data['date_to']
        product_id = data['product_id'] and data['product_id'][0] or False
        pick_type = data['pick_type']
        picking_obj = self.pool.get('stock.picking')
        stock_move_obj = self.pool.get('stock.move')

        conditions = " "
        conditions2 = " " 
        
        if company_id :
          conditions += " and pick.company_id=(%s)"%company_id 
          conditions2 += " and pick.company_id=(%s)"%company_id 
        
        if location_id :
            conditions += " and move.location_dest_id=(%s) "%(location_id,)
            conditions2 += " and move.location_id=(%s) "%(location_id,)
        if product_id :
            conditions += " and pdc.id=(%s)"%product_id
            conditions2 += " and pdc.id=(%s)"%product_id
        
        '''if department_id:
          conditions = conditions + " and pick.department_id=(%s)"%department_id'''
        
        self.cr.execute( """
            select pick.stock_in_type,pdc.fuel_type,sum(move.product_qty) as qty_in
            From stock_move move 
                left join stock_picking pick on (pick.id=move.picking_id)
                left join product_product pdc on (move.product_id=pdc.id)
                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                left join product_category cat on (p_temp.categ_id=cat.id)
            where to_char(pick.date,'YYYY-mm-dd')<=%s and pick.state = ('done') and pick.fuel_ok = True and pick.type = 'in'
            """ + conditions + """ group by pick.stock_in_type,pdc.fuel_type   order by pick.stock_in_type,pdc.fuel_type"""   ,(date_from,)) 
        before_res_in = self.cr.dictfetchall()


        self.cr.execute( """
            select pick.stock_in_type,pdc.fuel_type,
            sum(move.product_qty) as qty_in, p_temp.standard_price, sum( (move.product_qty*p_temp.standard_price) ) as sum_price
            From stock_move move 
                left join stock_picking pick on (pick.id=move.picking_id)
                left join product_product pdc on (move.product_id=pdc.id)
                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                left join product_category cat on (p_temp.categ_id=cat.id)       
            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) and pick.state = ('done') and pick.fuel_ok = True and pick.type = 'in'
            """ + conditions + """ group by pick.stock_in_type,pdc.fuel_type, p_temp.standard_price   order by pick.stock_in_type,pdc.fuel_type"""  ,(date_from,date_to)) 
        res_in = self.cr.dictfetchall()

        self.cr.execute( """
            select pdc.fuel_type, sum(move.product_qty) as qty_in, p_temp.standard_price, sum( (move.product_qty*p_temp.standard_price) ) as sum_price 
            From stock_move move 
                left join stock_picking pick on (pick.id=move.picking_id)
                left join product_product pdc on (move.product_id=pdc.id)
                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                left join product_category cat on (p_temp.categ_id=cat.id)
            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) and pick.state = ('done') and pick.fuel_ok = True and pick.type = 'in'
            """ + conditions + """ group by pdc.fuel_type, p_temp.standard_price""" ,(date_from,date_to)) 
        sum_res_in = self.cr.dictfetchall()




        self.cr.execute( """
            select out_type.name as out_type_name,pdc.fuel_type,sum(move.product_qty) as qty_out
            From stock_move move 
                left join stock_picking pick on (pick.id=move.picking_id)
                left join product_product pdc on (move.product_id=pdc.id)
                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                left join product_category cat on (p_temp.categ_id=cat.id)
                left join outgoing_fuel_type out_type on (pick.outgoing_fuel_type=out_type.id)
            where to_char(pick.date,'YYYY-mm-dd')<=%s   and pick.state = ('done') and pick.fuel_ok = True and pick.type = 'out' and out_type.evaporation_type = False
            """ + conditions2 + """ group by out_type.name,pdc.fuel_type   order by  out_type.name,pdc.fuel_type"""   ,(date_from,)) 
        before_res_out = self.cr.dictfetchall()


        self.cr.execute( """
            select out_type.name as out_type_name,pdc.fuel_type,
            sum(move.product_qty) as qty_out, p_temp.standard_price, sum( (move.product_qty*p_temp.standard_price) ) as sum_price 
            From stock_move move 
                left join stock_picking pick on (pick.id=move.picking_id)
                left join product_product pdc on (move.product_id=pdc.id)
                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                left join product_category cat on (p_temp.categ_id=cat.id)
                left join outgoing_fuel_type out_type on (pick.outgoing_fuel_type=out_type.id)
            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) and pick.state = ('done') and pick.fuel_ok = True and pick.type = 'out' and out_type.evaporation_type = False 
            """ + conditions2 + """ group by out_type.name,pdc.fuel_type, p_temp.standard_price   order by  out_type.name,pdc.fuel_type"""  ,(date_from,date_to)) 
        res_out = self.cr.dictfetchall()

        self.cr.execute( """
            select out_type.name as out_type_name,pdc.fuel_type,
            sum(move.product_qty) as qty_out, p_temp.standard_price, sum( (move.product_qty*p_temp.standard_price) ) as sum_price
            From stock_move move 
                left join stock_picking pick on (pick.id=move.picking_id)
                left join product_product pdc on (move.product_id=pdc.id)
                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                left join product_category cat on (p_temp.categ_id=cat.id)
                left join outgoing_fuel_type out_type on (pick.outgoing_fuel_type=out_type.id)
            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) and pick.state = ('done') and pick.fuel_ok = True and pick.type = 'out' and out_type.evaporation_type = True 
            """ + conditions2 + """ group by out_type.name,pdc.fuel_type, p_temp.standard_price   order by  out_type.name,pdc.fuel_type"""  ,(date_from,date_to)) 
        res_out_evaporation = self.cr.dictfetchall()

        self.cr.execute( """
            select pdc.fuel_type, sum(move.product_qty) as qty_out, p_temp.standard_price, sum( (move.product_qty*p_temp.standard_price) ) as sum_price 
            From stock_move move 
                left join stock_picking pick on (pick.id=move.picking_id)
                left join product_product pdc on (move.product_id=pdc.id)
                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                left join product_category cat on (p_temp.categ_id=cat.id)
                left join outgoing_fuel_type out_type on (pick.outgoing_fuel_type=out_type.id)
            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) and pick.state = ('done') and pick.fuel_ok = True and pick.type = 'out' and out_type.evaporation_type = False
            """ + conditions2 + """ group by pdc.fuel_type, p_temp.standard_price"""   ,(date_from,date_to)) 
        sum_res_out = self.cr.dictfetchall()

        remain = 0.0
        if sum_res_in:
            if 'qty_in'in sum_res_in[0] and sum_res_in[0]['qty_in']:
                remain += sum_res_in[0]['qty_in']
        if sum_res_out:
            if 'qty_out'in sum_res_out[0] and sum_res_out[0]['qty_out']:
                remain -= sum_res_out[0]['qty_out']

        
        remain_dict = {}
        for rec in res_in:
            remain_dict[rec['fuel_type']] = remain_dict.get(rec['fuel_type'], 0.0)
            remain_dict[rec['fuel_type']] += rec['qty_in']
        
        for rec in res_out:
            remain_dict[rec['fuel_type']] = remain_dict.get(rec['fuel_type'], 0.0)
            remain_dict[rec['fuel_type']] -= rec['qty_out']
        
        for rec in res_out_evaporation:
            remain_dict[rec['fuel_type']] = remain_dict.get(rec['fuel_type'], 0.0)
            remain_dict[rec['fuel_type']] -= rec['qty_out']
        
        #before convert to list
        remain_dict_b_l = remain_dict
        remain_dict = [{'name':x, 'net':remain_dict[x]} for x in remain_dict]

        for rec in remain_dict:

            self.cr.execute( """
            select p_temp.standard_price 
            From product_product pdc 
            left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
            where pdc.fuel_type='"""+rec['name']+"'" )
            standard_price = self.cr.dictfetchall()
            if standard_price:
                standard_price = standard_price[0]['standard_price']
                rec['standard_price'] = standard_price
                rec['sum_price'] = standard_price * rec['net']
            

        previous = 0.0
        if before_res_in:
            if 'qty_in'in before_res_in[0] and before_res_in[0]['qty_in']:
                previous += before_res_in[0]['qty_in']
        if before_res_out:
            if 'qty_out'in before_res_out[0] and before_res_out[0]['qty_out']:
                previous -= before_res_out[0]['qty_out']


        previous_dict = {}
        for rec in before_res_in:
            previous_dict[rec['fuel_type']] = previous_dict.get(rec['fuel_type'], 0.0)
            previous_dict[rec['fuel_type']] += rec['qty_in']
        
        for rec in before_res_out:
            previous_dict[rec['fuel_type']] = previous_dict.get(rec['fuel_type'], 0.0)
            previous_dict[rec['fuel_type']] -= rec['qty_out']
        
        previous_dict_b_l = previous_dict
        previous_dict = [{'name':x, 'net':previous_dict[x]} for x in previous_dict]


        all_sum_b_l = {}
        for rec in remain_dict_b_l:
            all_sum_b_l[rec] = all_sum_b_l.get(rec, 0.0)
            all_sum_b_l[rec] = remain_dict_b_l[rec]
            if rec in previous_dict_b_l:
                all_sum_b_l[rec] += previous_dict_b_l[rec]

        
        all_sum_b_l = [{'name':x, 'net':all_sum_b_l[x]} for x in all_sum_b_l]
        count = 1
        for i in res_in:
            i['count'] = count
            count += 1
        
        count = 1
        for i in res_out:
            i['count'] = count
            count += 1

        count = 1
        for i in res_out_evaporation:
            i['count'] = count
            count += 1

        return {'in': res_in,'sum_in': sum_res_in, 'out': res_out, 'evaporation': res_out_evaporation,'sum_out': sum_res_out,'remain':remain,'remain_dict':remain_dict, 'previous':previous,'previous_dict':previous_dict, 'sum':remain + previous, 'all_sum_b_l':all_sum_b_l}


    def _total(self,data):
        return int(globals()['total'])

    def _total_in(self,data):
        return int(globals()['total_in'])

    def _total_out(self,data):
        return int(globals()['total_out'])

    def _total_remain(self,data):
        return int(globals()['total_remain'])


    

report_sxw.report_sxw('report.fuel_stock_report','stock.picking','addons/fuel_niss/report/fuel_stock_report.rml',parser=fuel_stock_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
