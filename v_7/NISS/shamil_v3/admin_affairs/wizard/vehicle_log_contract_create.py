# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
import openerp.addons.decimal_precision as dp
import time
import datetime

#-----------------------------------------
#   vehicle log contract create
#-----------------------------------------

class vehicle_log_contract_create(osv.osv_memory):
    _name = "vehicle.log.contract.create"

    _columns = {
        #'category': fields.selection([('insurance','Vehicle Insurance'),('license','Vehicle License')], 'Category',required=True),
    	#'insurance_type': fields.selection([('part', 'Third Part'),('all', 'All')],'Insurance Type'),
    	'vehicles_ids': fields.many2many('fleet.vehicle', 'fleet_vehicle_contract_create_vehicle', 'wiz_id', 'vehicle_id', string='Vehicles'),
    }

    def log_contract_create(self, cr, uid, ids, context={}):
        start=datetime.datetime.now()
        print"--------------------------------------Start At:",start
    	log_obj=self.pool.get('fleet.vehicle.log.contract')
    	log_line_obj=self.pool.get('fleet.vehicle.log.contract.line')
        if context == None:
            context ={}
        line_ids=[]
        lines=log_obj.browse(cr,uid,context['active_id']).line_ids
        for line in lines:
            line_ids.append(line.vehicle_id.id)
        for rec in self.browse(cr,uid,ids):
            for log in rec.vehicles_ids:
                if log.id not in line_ids:
                    cr.execute( """INSERT into fleet_vehicle_log_contract_line (fleet_contract_id,vehicle_id,model_id, vin_sn,license_plate,new_license_plate, driver,fuel_type,department_id, ownership, type ,status) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """ \
                        ,(context['active_id'],log.id,log.model_id.id,log.vin_sn,log.license_plate,log.license_plate,
                        (log.driver and log.driver.id) or (log.employee_id and log.employee_id.id) or None,
                        log.fuel_type,log.department_id and log.department_id.id or None,
                        log.ownership and log.ownership.id or None,log.type and log.type.id or None,log.status or None))
        end=datetime.datetime.now()
        print"--------------------------------------End At:",end
        print"--------------------------------------Procces:",end - start
        return True
