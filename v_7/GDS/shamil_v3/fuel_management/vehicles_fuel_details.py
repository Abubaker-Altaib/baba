# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from osv import fields,osv
import time
import netsvc
from tools.translate import _
import decimal_precision as dp


class vehicles_fuel_details(osv.osv):
    """
    To manage fule details """

    _name = "vehicles.fuel.details"
    _description = 'vehicles fuel details'

    
    def create(self, cr, uid, vals, context=None):
        """
        Create new entry sequence for every new vehicles fuel details Record.

        @param vals: record to be created
        @return: return a result that create a new record in the database
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'vehicles.fuel.details')
        return super(vehicles_fuel_details, self).create(cr, uid, vals, context)
    
    def onchange_emp_id(self, cr, uid, ids, emp_id,context={}):
        """ 
        On change Employee name get Department
        @param emp_id: employee_id 
        @return: Dictionary of department values 
        """
        employee_obj = self.pool.get('hr.employee')
        employee = employee_obj.browse(cr, uid, [emp_id], context=context)[0]

        if not emp_id:
            return {'value':{'department_id': False,}}
        else:
            return {'value':{'department_id': employee.department_id.id}}

    
    FUEL_TYPE_SELECTION = [
    ('benzin', 'Benzin'),
    ('gasoline', 'Gasoline'),
 ]  

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the fuel details"),
    'date' : fields.date('Service date',required=True, readonly=True,),
    'emp_id' :fields.many2one('hr.employee', 'Employee',),
    'department_id':fields.many2one('hr.department', 'Department', ),
    'car': fields.many2one('fleet.vehicle', 'Car Name',required=True),
    'code': fields.related('car', 'license_plate', type='char', relation='fleet.vehicle', string='Car Number', readonly=True, store=True),  
    'notes': fields.text('Notes', size=512 ,),
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'fuel_details_lines':fields.one2many('fuel.details.lines', 'fuel_id' , 'Fuel Quantanties'),

    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'fuel details reference must be unique !'),
        ]
    
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'date': lambda *a: time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'vehicles.fuel.details', context=c),
                }



class fuel_details_lines(osv.osv):
    """
    To manage fule details for every line"""

    _name = "fuel.details.lines"
    _description = 'Type of Fuel and Qty'
       
    _columns = {
                'name': fields.char('Name', size=64 ,select=True,),
                'product_id': fields.many2one('product.product','Item',required=True),
                'product_qty': fields.float('Item Quantity', required=True, digits=(16,2)),
                'product_uom': fields.many2one('product.uom', 'Item UOM'),
                'fuel_id': fields.many2one('vehicles.fuel.details', 'Vehicles fuel details', ondelete='restrict'),
                'notes': fields.text('Notes', size=256 ,),

               }
    _sql_constraints = [
        ('produc_uniq', 'unique(fuel_id,product_id)', 'Fuel must be unique!'),
            ]  
    _defaults = {
                 'product_qty': 1.0
                 }  

    def product_id_change(self, cr, uid, ids,product):
        """
        On change product function to read the default name and UOM of product

        @param product: product_id 
        @return: Dictionary of product name and uom 
        """
        if product:
            prod= self.pool.get('product.product').browse(cr, uid,product)
            return {'value': { 'name':prod.name,'product_uom':prod.uom_po_id.id}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
