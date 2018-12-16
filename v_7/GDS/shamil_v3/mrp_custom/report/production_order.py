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
from openerp.osv import fields,osv

class production_order_report(osv.Model):
    _name = "production.order.report"
    _description = "Production Order Line"
    _auto = False

    _columns = {
        'production_id': fields.many2one('mrp.production', 'Production Order', select=True,readonly=True),
        #'production_line_id': fields.many2one('mrp.production.product.line', 'Material',readonly=True),
        'product_id': fields.many2one('product.product', 'Product',readonly=True),
        'quantity': fields.float('Quantity', readonly=True),


               }


    def init(self, cr):
        tools.drop_view_if_exists(cr, 'production_order_report')
        cr.execute("""
            create or replace view production_order_report as (
              SELECT 
		  mrp_production_product_line.id AS id, 
	          product_product.id AS product_id, 
	          mrp_production_product_line.production_id  AS production_id, 
		  mrp_production_product_line.product_qty AS quantity
		FROM 
		  public.product_product right join 
		  public.mrp_production_product_line on (product_product.id=mrp_production_product_line.product_id) 
                group by
                   mrp_production_product_line.id,product_product.id,mrp_production_product_line.production_id,mrp_production_product_line.product_qty
            )
        """)


