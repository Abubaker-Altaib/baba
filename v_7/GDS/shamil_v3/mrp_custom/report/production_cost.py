# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import fields,osv,orm
import openerp.addons.decimal_precision as dp
import time 
import netsvc 

class production_cost(osv.Model):
    _name = "production.cost"
    _description = "Production cost"
    _auto = False
    _rec_name = 'begin'
    _columns = {

        'production_id': fields.many2one('mrp.production', 'Production Order', select=True,readonly=True),
        'product_id': fields.many2one('product.product', 'Product',readonly=True),
        'begin':fields.date('Start Date',readonly=True),
        'end':fields.date('End Date',readonly=True),
        'begin1':fields.function(lambda *a,**k:{}, method=True, type='date',string="Begin production date"),
        'end1':fields.function(lambda *a,**k:{}, method=True, type='date',string="End production date"),   
        'responsible': fields.many2one('res.users','Responsible',readonly=True),
        'company_id': fields.many2one('res.company','Company',readonly=True),
        'product_state': fields.char( 'Status', readonly=True),
        'manpower_cost': fields.float('Manpower Cost',readonly=True),
        'material_cost': fields.float('Material  Cost', digits_compute=dp.get_precision('Account'), readonly=True),
        'fixed_cost':    fields.float('Fixed Cost', digits_compute=dp.get_precision('Account'), readonly=True),
        'production_cost': fields.float('Total Production Cost', digits_compute=dp.get_precision('Account'), readonly=True),
        'routing_id': fields.many2one('mrp.routing', 'Parent Routing', select=True, ondelete='cascade',),
        'product_cost': fields.float('Product Cost',readonly=True),
        'main_product_qty': fields.float('Main Product',readonly=True),
        'second_product_qty': fields.float('Second Product',readonly=True),
        'production_percentage': fields.float('Production Percentage',readonly=True),
        'lost': fields.float('Lost',readonly=True),
        'main_material_qty': fields.float('Main Material',readonly=True),

    }

    _order = 'begin desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr,'production_cost')
        cr.execute("""
            create or replace view production_cost as (
               SELECT distinct
                  mrp.id as id, 
                  mrp.company_id as company_id, 
                  mrp.product_id as product_id,
                  mrp.id as production_id,
                  mrp.begin_production_date as begin,
                  mrp.end_production_date as end,
                  mrp.state as product_state , 
                  mrp.user_id as responsible,
                  mrp.products_total_cost as material_cost, 
                  mrp.total_fixed_cost as fixed_cost, 
                  mrp.manpower_cost as manpower_cost,
                  mrp.routing_id as routing_id,
                  mrp.total_production_cost as production_cost,
                  (select sum(product_qty) from stock_move where id in (select move_id from mrp_production_move_ids where production_id = mrp.id )and product_id = 66) as main_material_qty,
                  (mrp.products_total_cost+mrp.total_fixed_cost+mrp.manpower_cost)/ mrp.product_qty as product_cost,
                  (select sum(product_qty) from stock_move where production_id = mrp.id and  location_dest_id = 69) as lost ,
                  (select sum(product_qty) from stock_move where production_id = mrp.id and product_id = 58 and location_dest_id <> 69) as main_product_qty ,
                  (select sum(product_qty) from stock_move where production_id = mrp.id and product_id = 69) as second_product_qty,
                  (((select sum(product_qty) from stock_move where production_id = mrp.id and product_id = 58 and location_dest_id <> 69)+(select sum(product_qty) from stock_move where production_id = mrp.id and product_id = 69))/(select sum(product_qty) from stock_move where id in (select move_id from mrp_production_move_ids where production_id = mrp.id) and product_id = 66))*100 as production_percentage

                FROM 
                  public.mrp_production as mrp 
                group by mrp.id, mrp.product_id, mrp.begin_production_date, mrp.state, mrp.company_id ,mrp.user_id
                                                                )
        """)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
