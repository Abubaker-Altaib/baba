# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time
from datetime import timedelta,date , datetime
from tools.translate import _

#----------------------------------------
#car operation wizard
#----------------------------------------
class car_operation_wizard(osv.osv_memory):

    _name = "car.operation.wizard"
         
    _columns = {
        'company_id' : fields.many2one('res.company', 'Company',required=True),
        'operation_type': fields.selection([('license','License'),('insurance','insurance')], 'License Type', required=True,), 
        'department_id': fields.many2one('hr.department', 'Department'),
        'operation_id':fields.many2one('car.operation', 'Car Operation'),
        'cars_ids': fields.many2many('fleet.vehicle', 'cars_wizard', 'wizard_id', 'car_id', 'Cars',), 
            }

    _defaults = {
                'operation_type':'license',
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'car.operation', context=c),
                }

    def update_car_operation(self,cr,uid,ids,context={}):
        """update car operation by adding cars in lines
           @return: Dictionary 
        """
        car_operation_obj = self.pool.get('car.operation')
        car_operation_line_obj = self.pool.get('car.operation.line')
        
        for record in self.browse(cr,uid,ids,context=context):
            license_car_lst = []
            operation_type = record.operation_type
            wizard_car_lst = [cars_id.id for cars_id in record.cars_ids]
            if operation_type == 'license':
                license_car_lst = [car_id.id for car_id in record.operation_id.car_ids]
            else:
                license_car_lst = [line.car_id.id for line in record.operation_id.operation_lines]  
            
            new_car_lst = [x for x in wizard_car_lst if x not in license_car_lst] 
            
            if not new_car_lst:
                raise osv.except_osv(_('Warring!'), _("All cars license are already created") )
            
            if operation_type == 'license':
                for car_id in new_car_lst:                      
                    car_operation_obj.write(cr, uid, [record.operation_id.id], {'car_ids': [(4,car_id )]})
            else:
                for car_id in new_car_lst:                      
                    car_operation_line_obj.create(cr,uid,{'operation_id':record.operation_id.id,
                                                          'car_id':car_id},context = context)
        return {}


