# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
from tools.translate import _
import time
import datetime

#----------------------------------------
# Class product inherit
#----------------------------------------

class product_product(osv.osv):
    """
    To manage fuel products
    """
    def _check_unique_insesitive(self, cr, uid, ids, context=None):
        """ 
        Check uniqueness of product name.

        @return: Boolean of True or False
        """
        name = self.browse(cr, uid, ids[0], context=context).name
        if len(self.search(cr, uid, [('name','=ilike',name)],  context=context)) > 1:
            raise osv.except_osv(_('Constraint Error'), _("The Name Must Be Unique!"))
        return True

    def _check_cost(self, cr, uid, ids, context=None):
        """ 
        Check the value of product standard price,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        count = 0
        for product in self.browse(cr, uid, ids, context=context):
            if (product.standard_price <= 0):
                message = _("The Cost Must Be Greater Than Zero!")
                count += 1
        if count > 0 :
            raise osv.except_osv(_('ValidateError'), _(message))
        return True


    def check_unique_location_fuel_type(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.fuel_ok:
                idss = self.search(cr,uid, [('location', '=', rec.location.id),('fuel_type', '=', rec.fuel_type),('id','!=',rec.id)])
                if idss:
                    raise osv.except_osv(_('ERROR'), _('There is already Existed Fuel with the selected location and fuel type !') )
        return True

    _inherit = "product.product"

    _columns = {
        'fuel_ok': fields.boolean('Fuel Product', help="Determine This Product Is Fuel"),
        'fuel_type': fields.selection([('gasoline','Gasoline'),('diesel', 'Diesel'),('electric', 'Electric'), ('hybrid', 'Hybrid')],'Fuel type') ,
        'fuel_lines_ids': fields.one2many('fuel.product.lines', 'product_id', 'Rates'),
        'location': fields.many2one('vehicle.place', "Vehicle Place", required=True),
   }

    _sql_constraints = [
        ('location_uniq', 'unique(location,fuel_type)', _('there is another fuel type configured for this location.')),
    ]

    _constraints = [
        (_check_cost, '', ['']),
        (_check_unique_insesitive, '', ['']),
        (check_unique_location_fuel_type, '', [])
    ]

    def fuel_move_amount_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        """
        Scheduler to check the fuel product lines and reflect the amount
        @return True
        """
        fuel_ids = self.search(cr,uid,[('fuel_lines_ids','!=',False)])
        date=time.strftime('%Y-%m-%d')
        today = datetime.datetime.strptime(date,"%Y-%m-%d")
        for rec in self.browse(cr, uid, fuel_ids):
            for line in rec.fuel_lines_ids:
                amount_date = datetime.datetime.strptime(line.date,"%Y-%m-%d")
                if today.month == amount_date.month and today.year == amount_date.year:
                    self.write(cr, uid,[rec.id] ,{'standard_price':line.amount})
                    break
        return True


#----------------------------------------
# Salary Bonuses Lines 
#---------------------------------------- 
class fuel_product_lines(osv.osv):
    _name = "fuel.product.lines"


    _columns = {
        'date': fields.date('Date', select=True),
        'amount': fields.float('amount', digits=(12,6)),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    _order = "date desc"



    def check_amount(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.amount <= 0:
                raise osv.except_osv(_('Validater Error'), _('Amount should be more than Zero') )
        return True


    def check_unique_date(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            product_lines = self.search(cr,uid,[('product_id','=',rec.product_id.id),
                    ('date','=',rec.date),('id','!=',rec.id)],context)
            if product_lines:
                raise osv.except_osv(_('Validater Error'), _('Amount date should be unique per product') )
        return True


    _constraints = [
        (check_amount, '', []),
        (check_unique_date, '', []),
    ]
