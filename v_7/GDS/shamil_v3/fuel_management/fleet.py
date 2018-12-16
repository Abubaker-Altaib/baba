# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import time
import netsvc
#----------------------------------------
# Class fleet vehicles
#----------------------------------------

class fleet_vehicle(osv.osv):
    """
    To manage fule operation with fleet vehicle """

    _inherit = "fleet.vehicle"

    def _check_fuel_qty(self, cr, uid, ids, context=None):
        """
        Conistrain function to check quantity. 

        @return: Bolean True or False
        """
        record = self.browse(cr, uid, ids[0], context=context)
        if record.monthly_plan == True and not record.fuel_lines:
            return False
        return True

    _columns = { 

        'fueltype':fields.property('product.product',type='many2one', relation='product.product',string='Product', method=True, 
            view_load=True,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
        'fuel_lines':fields.one2many('fuel.lines', 'car_fuel_id', 'Fuel', states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]},),
        'monthly_plan':fields.boolean('Included in Monthly Plan',states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
        'fueltankcap':fields.float('Fuel Tank Capacity',help="The unit of measurement Of Tank Capacity depends on the measuring unit of Car fuel" ,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),

}

    _defaults={
               'fueltype':False,
}
    _constraints = [
        (_check_fuel_qty, 
            'You must Insert Fuel Qty First . ',
            ['Fuel Details']),]



# fuel Lines

class fuel_lines(osv.osv):
    """
    To manage fule lines """
    _name = "fuel.lines"
    _description = 'Type of Fuel and Qty'


        
    _columns = {
                'name': fields.char('Name', size=64 ,select=True,),
                'product_id': fields.many2one('product.product','Fuel',required=True),
                'product_qty': fields.float('Fuel Quantity', digits=(16,2),required=True),
                'product_uom': fields.many2one('product.uom', 'Fuel UOM'),
                'car_fuel_id': fields.many2one('fleet.vehicle', 'Fuel', ondelete='restrict', invisible=True),
                
               }
    _sql_constraints = [
        ('product_uniq', 'unique(car_fuel_id)', 'Sorry you entered fuel two time You are not allow to do this.So we are going to delete the duplicts!'),
            ]  
    _defaults = {
                 'product_qty': 1.0
                 }  
    def product_id_change(self, cr, uid, ids,product):
       """
       On change product when you select Product the id send to this 
       method to read the default name and UOM of product.

       @param product: product_id 
       @return: return a result
       """
       if product:
           prod= self.pool.get('product.product').browse(cr, uid,product)
           return {'value': { 'name':prod.name,'product_uom':prod.uom_po_id.id}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:              
