# -*- coding: utf-8 -*-
#############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
#############################################################################

from openerp.osv import fields,osv
from tools.translate import _

class mrp_workcenter(osv.osv):
    """
    To manage mrp Workcenter inherit """

    _inherit = "mrp.workcenter"
    _columns={
           'product_id_move': fields.many2one('product.product', 'Move product', required=True),
            }
class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'mrp': fields.boolean('Production'),
        'main_material': fields.boolean('Main Material'),
        'main_product': fields.boolean('Main Product'),

     }

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _order = 'name'
    _columns={

        'image': fields.related('product_id', 'image', type='binary', relation='product.product', string='Image', store=True, readonly=True)

    }

    def calculate_cost(self, cr, uid, ids, context=None):
        """
        This method calculate the production order cost and show the cost in 
        recent_production_cost field.

        @param confirmation_id: The confirmation id  which is created  
        @return: Boolean True
        """
        #Calculating manpower total and unitary cost
        print">>>>>>>>>>>>>>>>>>6666666622222222222>>"
        for production in self.pool.get('mrp.production').browse(cr, uid, ids):
            manpower_cost = 0.0
            sum_products_cost = 0.0
            sum_fixed_cost = 0.0
            qty_finished_products = 0.0
            qty_consumed_products = 0.0

            #First of all, identify the main production product between all finished products
            main_product = False
            finished_products = production.move_created_ids  
            for fin_prod in finished_products:
                qty_finished_products +=fin_prod.product_qty
                if fin_prod.product_id.id == production.product_id.id:
                    main_product = fin_prod

            if not main_product:
                main_product = production
                
            result = {}

            #Manpower cost
            number_of_workers = len(production.production_manpower)
            
            for worker in production.production_manpower:
                if not worker.employee_id.product_id:
                    raise osv.except_osv(_('Warning!'), _('This worker does not have associated an "hour" product. Please, set it before continuing...'))
                manpower_cost += worker.employee_id.product_id.standard_price * worker.production_duration
            tot_production_manpower_cost = manpower_cost
            unit_manpower_cost = tot_production_manpower_cost / production.product_qty
                
            qty_finished_products = 0 
            for fin_prod in production.move_created_ids2:
                if fin_prod.product_id.id == production.product_id.id:
                    qty_finished_products +=fin_prod.product_qty
            if not qty_finished_products > 0:
                    raise osv.except_osv(_('Error!'), _('No existen productos finalizados en la orden de producción'))
                
            #Material cost ((list price consumed products * qty)/sum_qty)
            for consumed_product in production.move_lines2:
                sum_products_cost += consumed_product.product_id.standard_price * consumed_product.product_qty
                qty_consumed_products += consumed_product.product_qty
            tot_products_cost = sum_products_cost
            #if not qty_finished_products: qty_finished_products = qty_consumed_products
            unit_product_cost = tot_products_cost / qty_finished_products

            #Fixed costs (sum of all fixed costs)
            for fixed_cost in production.fixed_costs:
                sum_fixed_cost += fixed_cost.amount
                    
            unit_fixed_cost = sum_fixed_cost / qty_finished_products


            stock_before_producing = main_product.product_id.qty_available - qty_finished_products
            total_production_cost = tot_production_manpower_cost + tot_products_cost + sum_fixed_cost                
            unit_production_cost = (total_production_cost / qty_finished_products) + unit_fixed_cost + unit_manpower_cost
            new_product_standard_price =0
            if stock_before_producing + qty_finished_products != 0:
                new_product_standard_price = ((stock_before_producing * main_product.product_id.standard_price) + (unit_production_cost * qty_finished_products))/ (stock_before_producing + qty_finished_products)

            #Updates cost management fields for this production
            vals_production = {
                    'products_total_cost': tot_products_cost,
                    'manpower_cost': tot_production_manpower_cost,
                    'total_fixed_cost': sum_fixed_cost,
                    'total_production_cost': total_production_cost,
            }
            print"after me will write ",vals_production
            self.pool.get('mrp.production').write(cr, uid, [production.id], vals_production)

            # Create line for the unit production
            production_unit_cost_object = self.pool.get('mrp.production.unit.costs')
            cost_lines = production_unit_cost_object.search(cr, uid, [('production_id', '=',production.id),('product_id', '=',main_product.product_id.id)], context=context)
            if len(cost_lines) == 0:
                print"in if "
                vals_unit_costs = {
                    'production_id': production.id,
                    'product_id': main_product.product_id.id,
                    'unit_product_cost': unit_product_cost,
                    'manpower_unit_cost': unit_manpower_cost,
                    'unit_fixed_cost': unit_fixed_cost,
                    'unit_production_cost': unit_production_cost,
                    'new_standard_price': new_product_standard_price
                    }
                production_unit_cost_object.create(cr, uid, vals_unit_costs)
            else:
                updated_record = production_unit_cost_object.browse(cr, uid, cost_lines[0])
                updated_record.write({
                    'unit_product_cost': unit_product_cost,
                    'manpower_unit_cost': unit_manpower_cost,
                    'unit_fixed_cost': unit_fixed_cost,
                    'unit_production_cost': unit_production_cost,
                    'new_standard_price': new_product_standard_price
                    })
                

                
                
            #Finally we update product list_price and manpower fields accordingly
            # This is por compatibilty with new modules that must write tehe costs later
                
            # It depends of context if it musts write de average price in the product
            if not (context.get('skip_write') and context['skip_write']):
                   
                vals_product = {}
                if main_product.product_id.cost_method == 'average':
                    vals_product['standard_price'] = new_product_standard_price
                        
                # Cálculo de los precios medios para actualziar ficha de producto
                pm_manpower_cost=0 
                pm_fixed_cost=0
                pm_product_cost =0
                if stock_before_producing + qty_finished_products != 0 :
                    pm_manpower_cost = ((stock_before_producing * main_product.product_id.manpower_cost) + (unit_manpower_cost * qty_finished_products))/ (stock_before_producing + qty_finished_products)
                    pm_fixed_cost = ((stock_before_producing * main_product.product_id.other_prod_cost) + (unit_fixed_cost * qty_finished_products))/ (stock_before_producing + qty_finished_products)
                    pm_product_cost = ((stock_before_producing * main_product.product_id.other_prod_cost) + (unit_product_cost * qty_finished_products))/ (stock_before_producing + qty_finished_products)

                vals_product['manpower_cost'] = pm_manpower_cost
                vals_product['other_prod_cost'] = pm_fixed_cost
                vals_product['product_cost'] = pm_product_cost

                #self.pool.get('product.product').write(cr, uid, main_product.product_id.id, vals_product)
            return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
