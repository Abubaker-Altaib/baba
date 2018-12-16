# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv

#----------------------------------------
# Class product inherit
#----------------------------------------
class product_product(osv.osv):
    """
    To manage fule products """

    _inherit = "product.product"
    
    _columns = {
        'fuel_ok': fields.boolean('Fuel product', help="By checking the fuel field, you determine this product as fuel"),
        'fuel_type': fields.selection([('gasoline','Gasoline'),('petrol','Petrol')],'Fuel type') ,   
        'property_fuel_fixed': fields.property(
            'stock.location',
            type='many2one',
            relation='stock.location',
            string="Fuel fixed Location",
            view_load=True,
            domain=[('fuel_location','=',True),('usage','=','internal')],
            help="For the current product, this stock location will be used as the location for fixed fuel"),       
                
        'property_fuel_extra': fields.property(
            'stock.location',
            type='many2one',
            relation='stock.location',
            string="Fuel Extra Location",
            view_load=True,
            domain=[('fuel_location','=',True),('usage','=','internal')],
            help="For the current product, this stock location will be used as the location for extra fuel"),       
    
        'property_fuel_customer': fields.property(
            'stock.location',
            type='many2one',
            relation='stock.location',
            string="Fuel customer location",
            view_load=True,
            domain=[('usage','=','customer')],
            help="For the current product, this stock location will be used as output location for the fuel"),       
                }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
