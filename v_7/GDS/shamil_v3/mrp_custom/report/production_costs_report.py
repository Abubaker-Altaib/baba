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

class production_costs_report(osv.Model):
    _name = "production.costs.report"
    _description = "Production and costs"
    _auto = False
    _rec_name = 'begin'
    _columns = {

        'production_id': fields.many2one('mrp.production', 'Production Order', select=True,readonly=True),
        'product_id': fields.many2one('product.product', 'Product',readonly=True),
        'begin':fields.date('Start Date',readonly=True),
        'end':fields.date('End Date',readonly=True),
        'begin1':fields.function(lambda *a,**k:{}, method=True, type='date',string="Begin production date"),
        'end1':fields.function(lambda *a,**k:{}, method=True, type='date',string="End production date"),   
        'responsible': fields.many2one('res_users','Responsible',readonly=True),
        'company_id': fields.many2one('res_company','Company',readonly=True),
        'product_state': fields.char( 'Status', readonly=True),
        'manpower_cost': fields.float('Manpower Cost',readonly=True),
        'material_cost': fields.float('Material  Cost', digits_compute=dp.get_precision('Account'), readonly=True),
        'fixed_cost':    fields.float('Fixed Cost', digits_compute=dp.get_precision('Account'), readonly=True),
        'production_cost': fields.float('Total Production Cost', digits_compute=dp.get_precision('Account'), readonly=True),
        'routing_id': fields.many2one('mrp.routing', 'Parent Routing', select=True, ondelete='cascade',),


    }

    _order = 'begin desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr,'production_costs_report')
        cr.execute("""
            create or replace view production_costs_report as (
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
                  mrp.total_production_cost as production_cost 
                FROM 
                  public.mrp_production as mrp 
                group by mrp.id, mrp.product_id, mrp.begin_production_date, mrp.state, mrp.company_id ,mrp.user_id
                                                                )
        """)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
