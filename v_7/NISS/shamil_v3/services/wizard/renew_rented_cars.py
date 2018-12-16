# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields
import time
from datetime import timedelta,date , datetime
from openerp.tools.translate import _

#----------------------------------------
#renew_rented_cars
#----------------------------------------
class renew_rented_cars(osv.osv_memory):

    _name = "renew.rented.cars"
    _columns = {
	    'company_id' : fields.many2one('res.company', 'Company',required=True),
#            'department_id':fields.many2one('hr.department', 'Department',required=True),
            'date_of_rent':fields.date('Date of Rent'),
            'date_of_return':fields.date('Date of Return',required=True),
    	    'car_ids': fields.many2many('fleet.vehicle', 'renew_rented_cars_link', 'renew_id', 'car_id', 'Cars'), 
   		 }
    _defaults = {
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'renew.rented.cars', context=c),
		}

    def renew(self,cr,uid,ids,context={}):
           """renew rented Cars for specific company for specific time .
           @return: Dictionary 
           """
           rented_obj = self.pool.get('rented.cars')
           vehicle_obj = self.pool.get('fleet.vehicle')
       	   for record in self.browse(cr,uid,ids,context=context):
       	   	for line in record.car_ids:
                        rented_record_id = rented_obj.search(cr, uid, [('car_id','=',line.id),('state','=','confirmed')], context=context)[0]
			if record.date_of_rent :
				update_record = rented_obj.write(cr, uid,rented_record_id ,{'date_of_rent':record.date_of_rent,'date_of_return':record.date_of_return})
			# if not date of rent inserted
			update_record = rented_obj.write(cr, uid,rented_record_id ,{'date_of_return':record.date_of_return})
                        #fleet_id = vehicle_obj.search(cr, uid, [('id','=',line.id)], context=context)[0]
			#update_car = vehicle_obj.write(cr, uid,fleet_id,{'status':'active'})
			update_car = cr.execute(""" update fleet_vehicle set status='active' where id=%s"""%line.id)



           return {}



