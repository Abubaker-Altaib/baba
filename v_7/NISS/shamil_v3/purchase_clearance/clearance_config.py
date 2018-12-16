# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
import netsvc
import time
from tools.translate import _



class transporter_companies(osv.osv):
      
      DELIVERY_SELECTION = [
        ('air_freight', 'Air Freight'),
        ('sea_freight', 'Sea Freight'),
        ('free_zone','Free Zone'),
        ('land_freight', 'Land Freight'),
        ('halfa','Halfa'),
                         ]
      
      _name = "transporter.companies"
      _columns = {
         
         'name' : fields.char('Name Of Company',size=64),
         'english_name' : fields.char('English Name' ,  size=64 ,select=True),
         'ship_method':fields.selection(DELIVERY_SELECTION,'Bill By' ),
         'desc' : fields.text('Description'),
         'active' : fields.boolean("Active"),
             
                    }
      
      _defaults   = {
                'active' : True,          
                }
       
class bill_clearance_items(osv.osv):
      
      DELIVERY_SELECTION = [
        ('air_freight', 'Air Freight'),
        ('sea_freight', 'Sea Freight'),
        ('free_zone','Free Zone'),
        ('land_freight', 'Land Freight'),
        ('halfa','Halfa'),
                         ]
      
      _name = "bill.clearance.items"
      _columns = {
         
         'name' : fields.char('Name Of Item',size=32),
         'ship_method':fields.selection(DELIVERY_SELECTION,'Bill By' ),
         'active' : fields.boolean("Active"),
         'desc' : fields.text('Description'),
         
                    }
      _defaults   = {
                'active' : True,          
                }

class items_category(osv.osv):
      
    
      
      _name = "items.category"
      _columns = {
         
         'name' : fields.char('Name Of Item',size=32),
         'desc' : fields.text('Description'),
         'specifections_required':fields.boolean('Required Specifections',  help="This Field for determinate the item in this letter need specifections Letter or not"), 
         
                    }
      
      
      
class partner_ship_config(osv.osv):
      
      DELIVERY_SELECTION = [
        ('air_freight', 'Air Freight'),
        ('sea_freight', 'Sea Freight'),
        ('free_zone','Free Zone'),
        ('land_freight', 'Land Freight'),
        ('halfa','Halfa'),
                         ]
      
      _name = "partner.ship.config"
      _columns = {
         'name' : fields.char('Name',size=32),
         'ship_method':fields.selection(DELIVERY_SELECTION,'Bill By' ),
         'partner_id' : fields.many2one('res.partner' , 'Partner' ) ,
         
             
                    }
      _sql_constraints = [
        ('ship_method_uniq', 'unique(ship_method)', 'Location must Be holds one partner !'),
          ]
      
      
