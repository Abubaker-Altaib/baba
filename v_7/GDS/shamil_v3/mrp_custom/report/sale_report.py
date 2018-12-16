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

class sale_costs_report(osv.osv):
    _name = "sale.costs.report"
    _description = "Sale"
    _auto = False
    _columns = {

        'name': fields.many2one('product.product', 'Product',readonly=True),
        #'company_id': fields.many2one('res_company','Company',readonly=True),
        'mrp_qty': fields.float('Production Quantity',readonly=True),
        'mrp_amount': fields.float('Production Cost',readonly=True),
        'sale_qty': fields.float('Sale Quantity',readonly=True),
        'sale_amount': fields.float('Sale Cost',readonly=True),
        'sale_percentage': fields.float('Sale percentage',readonly=True),
        'profit_percentage': fields.float('Profit percentage',readonly=True),


    }

    
    def init(self, cr):
        tools.drop_view_if_exists(cr,'sale_costs_report')
        cr.execute("""
            create or replace view sale_costs_report as (
            select min(p.id) as id,p.name_template as name, 
            sum(total_production_cost) as mrp_amount, sum(mrp.product_qty) as mrp_qty,
            sum(price_unit*product_uom_qty) as sale_amount, sum(product_uom_qty) as sale_qty,
            sum(mrp.product_qty)/sum(product_uom_qty) as sale_percentage,
            (sum(price_unit*product_uom_qty)-sum(total_production_cost))/sum(total_production_cost) as profit_percentage
            from product_product p
            left join mrp_production mrp on (mrp.product_id = p.id)
            left join sale_order_line l on (l.product_id = p.id)
            where p.mrp is true
            group by p.id )""")

sale_costs_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
