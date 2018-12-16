# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime,date,timedelta
from report import report_sxw

class vehicle_report(report_sxw.rml_parse):
    """ To manage vehicle report """

    def __init__(self, cr, uid, name, context):
        super(vehicle_report, self).__init__(cr, uid, name, context)
        self.total = {'total_allowance':0.0, 'total_deduction':0.0,'total_loans':0.0,'net':0.0,
                      'allowances_tax':0.0,'tax':0.0,'zakat':0.0,'imprint':0.0}
        self.name = {'name':''}
        self.localcontext.update({
            'time': time,
            'category_list': self.get_category_name,
            'category_data': self.get_category,
            'model_list': self.get_model_name,
            'model_data': self.get_model,
            'year_list': self.get_year_name,
            'year_data': self.get_year,
            'use_list': self.get_use_name,
            'use_data': self.get_use,
            'ownership_list': self.get_ownership_name,
            'ownership_data': self.get_ownership,
            'status_list': self.get_status_name,
            'status_data': self.get_status,
            'department_list': self.get_department_name,
            'department_data': self.get_department,
            'degree_list': self.get_degree_name,
            'degree_data': self.get_degree,
        })

    def get_category_name(self,data):
        category_ids = []
        category__tupel = []
        if data['categories_ids']: 
            category_ids = data['categories_ids']
        else:
            category_ids = self.pool.get('vehicle.category').search(self.cr, self.uid, [])
        for x in self.pool.get('vehicle.category').browse(self.cr, self.uid, category_ids):
            vehicle_obj = self.pool.get('fleet.vehicle')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('type','in',[x.id])])
            if vehicle_ids:
                category__tupel.append((x.id, x.name.encode('utf-8'), vehicle_ids))
        
        return category__tupel


    def get_category(self,data, category__tupel):
        res =[]
        if category__tupel:
            res =[]
            vehicle_obj = self.pool.get('fleet.vehicle')
            translation_obj = self.pool.get('ir.translation')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('type','in',category__tupel)])
            count = 0
            vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}
            for rec in vehicle_obj.browse(self.cr, self.uid,vehicle_ids):
                key = rec.vehicle_status
                if key:
                    key = vehicle_status[key]
                    translation_ids = translation_obj.search(
                        self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                    translation_recs = translation_obj.read(
                        self.cr, self.uid, translation_ids, [])
                    key = translation_recs and translation_recs[0]['value'] or key

                emp_name = False
                degree_name = False
                if rec.employee_id:
                    emp_name = rec.employee_id.name.encode('utf-8')
                    degree_name = rec.employee_id.degree_id.name.encode('utf-8')

                elif rec.driver:
                    emp_name = rec.driver.name.encode('utf-8')
                    degree_name = rec.driver.degree_id.name.encode('utf-8')

                else:
                    #if rec.old_system_driver:
                    emp_name = rec.old_system_driver and rec.old_system_driver.encode('utf-8') or False
                    degree_name = rec.old_system_degree and rec.old_system_degree.encode('utf-8') or False

                count = count + 1
                '''new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'employee_name':rec.employee_id and rec.employee_id.name.encode('utf-8') or False,
                    'employee_name':emp_name,
                    #'driver_name': rec.driver_id and rec.driver_id.name.encode('utf-8') or False,
                    'driver_name': emp_name,
                    'degree_name': degree_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                    'year': rec.year or False,
                }'''
                new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'machine_no': rec.machine_no,
                    'year': rec.year,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'degree_name': rec.degree_id and rec.degree_id.name.encode('utf-8') or False,
                    'degree_name': degree_name,
                    'employee_name':emp_name,
                    'driver_name': emp_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                }
                res.append(new_dict)

            
        return res


    def get_model_name(self,data):
        models_ids = []
        model__tupel = []
        if data['models_ids']: 
            models_ids = data['models_ids']
        else:
            models_ids = self.pool.get('fleet.vehicle.model').search(self.cr, self.uid, [])
        for x in self.pool.get('fleet.vehicle.model').browse(self.cr, self.uid, models_ids):
            vehicle_obj = self.pool.get('fleet.vehicle')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('model_id','in',[x.id])])
            if vehicle_ids:
                model__tupel.append((x.id, x.name.encode('utf-8'), vehicle_ids))

        return model__tupel


    def get_model(self,data, model__tupel):
        res =[]
        if model__tupel:
            res =[]
            vehicle_obj = self.pool.get('fleet.vehicle')
            translation_obj = self.pool.get('ir.translation')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('model_id','in',model__tupel)])
            count = 0
            vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}
            for rec in vehicle_obj.browse(self.cr, self.uid,vehicle_ids):
                key = rec.vehicle_status
                if key:
                    key = vehicle_status[key]
                    translation_ids = translation_obj.search(
                        self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                    translation_recs = translation_obj.read(
                        self.cr, self.uid, translation_ids, [])
                    key = translation_recs and translation_recs[0]['value'] or key

                emp_name = False
                degree_name = False
                if rec.employee_id:
                    emp_name = rec.employee_id.name.encode('utf-8')
                    degree_name = rec.employee_id.degree_id.name.encode('utf-8')

                elif rec.driver:
                    emp_name = rec.driver.name.encode('utf-8')
                    degree_name = rec.driver.degree_id.name.encode('utf-8')

                else:
                    #if rec.old_system_driver:
                    emp_name = rec.old_system_driver and rec.old_system_driver.encode('utf-8') or False
                    degree_name = rec.old_system_degree and rec.old_system_degree.encode('utf-8') or False

                count = count + 1
                '''new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    #'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'employee_name':rec.employee_id and rec.employee_id.name.encode('utf-8') or False,
                    'employee_name': emp_name,
                    #'driver_name': rec.driver_id and rec.driver_id.name.encode('utf-8') or False,
                    'driver_name': emp_name,
                    'degree_name': degree_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                    'year': rec.year or False,
                }'''
                new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'machine_no': rec.machine_no,
                    'year': rec.year,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'degree_name': rec.degree_id and rec.degree_id.name.encode('utf-8') or False,
                    'degree_name': degree_name,
                    'employee_name':emp_name,
                    'driver_name': emp_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                }
                res.append(new_dict)
            
        return res

    ################ for Degree ########################


    def get_degree_name(self,data):
        degree_ids = []
        degree__tupel = []
        if data['degree_ids']: 
            degree_ids = data['degree_ids']
        else:
            degree_ids = self.pool.get('hr.salary.degree').search(self.cr, self.uid, [] ,order='sequence desc')
        for x in self.pool.get('hr.salary.degree').browse(self.cr, self.uid, degree_ids):
            vehicle_obj = self.pool.get('fleet.vehicle')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('degree_id','in',[x.id])])
            if vehicle_ids:
                degree__tupel.append((x.id, x.name.encode('utf-8'), vehicle_ids))

        return degree__tupel


    def get_degree(self,data, degree__tupel):
        res =[]
        if degree__tupel:
            res =[]
            vehicle_obj = self.pool.get('fleet.vehicle')
            translation_obj = self.pool.get('ir.translation')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('degree_id','in',degree__tupel)])
            count = 0
            vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}
            for rec in vehicle_obj.browse(self.cr, self.uid,vehicle_ids):
                key = rec.vehicle_status
                if key:
                    key = vehicle_status[key]
                    translation_ids = translation_obj.search(
                        self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                    translation_recs = translation_obj.read(
                        self.cr, self.uid, translation_ids, [])
                    key = translation_recs and translation_recs[0]['value'] or key

                emp_name = False
                degree_name = False
                if rec.employee_id:
                    emp_name = rec.employee_id.name.encode('utf-8')
                    degree_name = rec.employee_id.degree_id.name.encode('utf-8')

                elif rec.driver:
                    emp_name = rec.driver.name.encode('utf-8')
                    degree_name = rec.driver.degree_id.name.encode('utf-8')

                else:
                    #if rec.old_system_driver:
                    emp_name = rec.old_system_driver and rec.old_system_driver.encode('utf-8') or False
                    degree_name = rec.old_system_degree and rec.old_system_degree.encode('utf-8') or False

                count = count + 1
                '''new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    #'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'employee_name':rec.employee_id and rec.employee_id.name.encode('utf-8') or False,
                    'employee_name': emp_name,
                    #'driver_name': rec.driver_id and rec.driver_id.name.encode('utf-8') or False,
                    'driver_name': emp_name,
                    'degree_name': degree_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                    'year': rec.year or False,
                }'''
                new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'machine_no': rec.machine_no,
                    'year': rec.year,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'degree_name': rec.degree_id and rec.degree_id.name.encode('utf-8') or False,
                    'degree_name': degree_name,
                    'employee_name':emp_name,
                    'driver_name': emp_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                }
                res.append(new_dict)

            
        return res

    
    ################ for vehicle years ###################

    def get_year_name(self,data):
        
        years = []
        year_tuple = []
        if data['year']: 
            years = [ data['year'] ]
        else:
            years = [str(years) for years in range(int(datetime.now().year) + 1, 1970, -1)]
            
        for x in years:
            vehicle_obj = self.pool.get('fleet.vehicle')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('year','in',[x])])
            if vehicle_ids:
                year_tuple.append((x, x, vehicle_ids))

        return year_tuple


    def get_year(self,data, year_tuple):
        res =[]
        if year_tuple:
            res =[]
            vehicle_obj = self.pool.get('fleet.vehicle')
            translation_obj = self.pool.get('ir.translation')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('year','in',year_tuple)])
            count = 0
            vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}
            for rec in vehicle_obj.browse(self.cr, self.uid,vehicle_ids):
                key = rec.vehicle_status
                if key:
                    key = vehicle_status[key]
                    translation_ids = translation_obj.search(
                        self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                    translation_recs = translation_obj.read(
                        self.cr, self.uid, translation_ids, [])
                    key = translation_recs and translation_recs[0]['value'] or key

                emp_name = False
                degree_name = False
                if rec.employee_id:
                    emp_name = rec.employee_id.name.encode('utf-8')
                    degree_name = rec.employee_id.degree_id.name.encode('utf-8')

                elif rec.driver:
                    emp_name = rec.driver.name.encode('utf-8')
                    degree_name = rec.driver.degree_id.name.encode('utf-8')

                else:
                    #if rec.old_system_driver:
                    emp_name = rec.old_system_driver and rec.old_system_driver.encode('utf-8') or False
                    degree_name = rec.old_system_degree and rec.old_system_degree.encode('utf-8') or False

                count = count + 1
                '''new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'employee_name':rec.employee_id and rec.employee_id.name.encode('utf-8') or False,
                    'employee_name': emp_name,
                    #'driver_name': rec.driver_id and rec.driver_id.name.encode('utf-8') or False,
                    'driver_name': emp_name,
                    'degree_name': degree_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                    'year': rec.year or False,
                }'''
                new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'machine_no': rec.machine_no,
                    'year': rec.year,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'degree_name': rec.degree_id and rec.degree_id.name.encode('utf-8') or False,
                    'degree_name': degree_name,
                    'employee_name':emp_name,
                    'driver_name': emp_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                }
                res.append(new_dict)
            
        return res

    ################ for Vehicle Ownerships ####################

    def get_ownership_name(self,data):
        ownerships_ids = []
        ownership__tupel = []
        if data['ownerships_ids']: 
            ownerships_ids = data['ownerships_ids']
        else:
            ownerships_ids = self.pool.get('fleet.vehicle.ownership').search(self.cr, self.uid, [])
        for x in self.pool.get('fleet.vehicle.ownership').browse(self.cr, self.uid, ownerships_ids):
            vehicle_obj = self.pool.get('fleet.vehicle')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('ownership','in',[x.id])])
            if vehicle_ids:
                ownership__tupel.append((x.id, x.name.encode('utf-8'), vehicle_ids))

        return ownership__tupel


    def get_ownership(self,data, ownership__tupel):
        res =[]
        if ownership__tupel:
            vehicle_obj = self.pool.get('fleet.vehicle')
            translation_obj = self.pool.get('ir.translation')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('ownership','in',ownership__tupel)])
            count = 0
            vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}
            for rec in vehicle_obj.browse(self.cr, self.uid,vehicle_ids):
                key = rec.vehicle_status
                if key:
                    key = vehicle_status[key]
                    translation_ids = translation_obj.search(
                        self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                    translation_recs = translation_obj.read(
                        self.cr, self.uid, translation_ids, [])
                    key = translation_recs and translation_recs[0]['value'] or key

                emp_name = False
                degree_name = False
                if rec.employee_id:
                    emp_name = rec.employee_id.name.encode('utf-8')
                    degree_name = rec.employee_id.degree_id.name.encode('utf-8')

                elif rec.driver:
                    emp_name = rec.driver.name.encode('utf-8')
                    degree_name = rec.driver.degree_id.name.encode('utf-8')

                else:
                    #if rec.old_system_driver:
                    emp_name = rec.old_system_driver and rec.old_system_driver.encode('utf-8') or False
                    degree_name = rec.old_system_degree and rec.old_system_degree.encode('utf-8') or False

                count = count + 1
                '''new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    #'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'employee_name':rec.employee_id and rec.employee_id.name.encode('utf-8') or False,
                    'employee_name': emp_name,
                    #'driver_name': rec.driver_id and rec.driver_id.name.encode('utf-8') or False,
                    'driver_name': emp_name,
                    'degree_name': degree_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                    'year': rec.year or False,
                }'''
                new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'machine_no': rec.machine_no,
                    'year': rec.year,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'degree_name': rec.degree_id and rec.degree_id.name.encode('utf-8') or False,
                    'degree_name': degree_name,
                    'employee_name':emp_name,
                    'driver_name': emp_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                }
                res.append(new_dict)

            
        return res

        
    ################ for Vehicle Use ####################
    def get_use_name(self,data):
        uses_ids = []
        use__tupel = []
        if data['uses_ids']: 
            uses_ids = data['uses_ids']
        else:
            uses_ids = self.pool.get('fleet.vehicle.use').search(self.cr, self.uid, [])
        for x in self.pool.get('fleet.vehicle.use').browse(self.cr, self.uid, uses_ids):
            vehicle_obj = self.pool.get('fleet.vehicle')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('use','in',[x.id])])
            if vehicle_ids:
                use__tupel.append((x.id, x.name.encode('utf-8'), vehicle_ids))

        return use__tupel


    def get_use(self,data, use__tupel):
        res =[]
        if use__tupel:
            res =[]
            vehicle_obj = self.pool.get('fleet.vehicle')
            translation_obj = self.pool.get('ir.translation')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('use','in',use__tupel)])
            count = 0
            vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}
            for rec in vehicle_obj.browse(self.cr, self.uid,vehicle_ids):
                key = rec.vehicle_status
                if key:
                    key = vehicle_status[key]
                    translation_ids = translation_obj.search(
                        self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                    translation_recs = translation_obj.read(
                        self.cr, self.uid, translation_ids, [])
                    key = translation_recs and translation_recs[0]['value'] or key

                emp_name = False
                degree_name = False
                if rec.employee_id:
                    emp_name = rec.employee_id.name.encode('utf-8')
                    degree_name = rec.employee_id.degree_id.name.encode('utf-8')

                elif rec.driver:
                    emp_name = rec.driver.name.encode('utf-8')
                    degree_name = rec.driver.degree_id.name.encode('utf-8')

                else:
                    #if rec.old_system_driver:
                    emp_name = rec.old_system_driver and rec.old_system_driver.encode('utf-8') or False
                    degree_name = rec.old_system_degree and rec.old_system_degree.encode('utf-8') or False

                count = count + 1
                '''new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    #'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'employee_name':rec.employee_id and rec.employee_id.name.encode('utf-8') or False,
                    'employee_name': emp_name,
                    #'driver_name': rec.driver_id and rec.driver_id.name.encode('utf-8') or False,
                    'driver_name': emp_name,
                    'degree_name': degree_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                    'year': rec.year or False,
                }'''
                new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'machine_no': rec.machine_no,
                    'year': rec.year,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'degree_name': rec.degree_id and rec.degree_id.name.encode('utf-8') or False,
                    'degree_name': degree_name,
                    'employee_name':emp_name,
                    'driver_name': emp_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                }
                res.append(new_dict)
            
        return res


    ################ for Vehicle Department ####################
    def get_department_name(self,data):
        departments_ids = []
        department__tupel = []
        vehicle_obj = self.pool.get('fleet.vehicle')
        employee_obj = self.pool.get('hr.employee')
        if data['departments_ids']: 
            departments_ids = data['departments_ids']
            if data['included_department']:
                departments_ids = self.pool.get('hr.department').search(self.cr, self.uid, [('id','child_of',departments_ids)])

        else:
            departments_ids = self.pool.get('hr.department').search(self.cr, self.uid, [])
        for x in self.pool.get('hr.department').browse(self.cr, self.uid, departments_ids):
            domain = [('department_id','in',[x.id])]
            #emplyee_ids = employee_obj.search(self.cr, self.uid, [('department_id','in',[x.id]),('state','=','approved')])
            #if emplyee_ids:
            #    domain.append(('employee_id','in',emplyee_ids))
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, domain)
            #vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('department_id','in',[x.id])])
            if vehicle_ids:
                department__tupel.append((x.id, x.name.encode('utf-8'), vehicle_ids))
        return department__tupel


    def get_department(self,data, department__tupel):
        res =[]
        if department__tupel:
            res =[]
            vehicle_obj = self.pool.get('fleet.vehicle')
            employee_obj = self.pool.get('hr.employee')
            translation_obj = self.pool.get('ir.translation')
            domain = [('department_id','in',department__tupel)]
            #emplyee_ids = employee_obj.search(self.cr, self.uid, [('department_id','in',department__tupel),('state','=','approved')])
            #if emplyee_ids:
            #    domain = ['|', ('department_id','in',department__tupel),('employee_id','in',emplyee_ids)]
            #    #domain.append(('employee_id','in',emplyee_ids))
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, domain)
            count = 0
            vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}
            for rec in vehicle_obj.browse(self.cr, self.uid,vehicle_ids):
                key = rec.vehicle_status
                if key:
                    key = vehicle_status[key]
                    translation_ids = translation_obj.search(
                        self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                    translation_recs = translation_obj.read(
                        self.cr, self.uid, translation_ids, [])
                    key = translation_recs and translation_recs[0]['value'] or key

                emp_name = False
                degree_name = False
                if rec.employee_id:
                    emp_name = rec.employee_id.name.encode('utf-8')
                    degree_name = rec.employee_id.degree_id.name.encode('utf-8')

                elif rec.driver:
                    emp_name = rec.driver.name.encode('utf-8')
                    degree_name = rec.driver.degree_id.name.encode('utf-8')

                else:
                    #if rec.old_system_driver:
                    emp_name = rec.old_system_driver and rec.old_system_driver.encode('utf-8') or False
                    degree_name = rec.old_system_degree and rec.old_system_degree.encode('utf-8') or False

                count = count + 1
                '''new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'employee_name':rec.employee_id and rec.employee_id.name.encode('utf-8') or False,
                    'employee_name': emp_name,
                    #'driver_name': rec.driver_id and rec.driver_id.name.encode('utf-8') or False,
                    'driver_name': emp_name,
                    'degree_name': degree_name,
                    #'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                    'year': rec.year or False,
                }'''
                new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'machine_no': rec.machine_no,
                    'year': rec.year,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'degree_name': rec.degree_id and rec.degree_id.name.encode('utf-8') or False,
                    'degree_name': degree_name,
                    'employee_name':emp_name,
                    'driver_name': emp_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                }
                res.append(new_dict)
            
        return res


    ################ for Vehicle Status ####################
    def get_status_name(self,data):
        uses_ids = []
        status__tupel = []
        vehicle_obj = self.pool.get('fleet.vehicle')
        translation_obj = self.pool.get('ir.translation')
        vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}
        if data['vehicle_status']: 
            status = [data['vehicle_status']]
        else:
            status = vehicle_status.keys()
        for x in status:
            key = x
            if key:
                key = vehicle_status[key]
                translation_ids = translation_obj.search(
                    self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                translation_recs = translation_obj.read(
                    self.cr, self.uid, translation_ids, [])
                key = translation_recs and translation_recs[0]['value'] or key
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('vehicle_status','in',[x])])
            if vehicle_ids:
                status__tupel.append((x, key.encode('utf-8'), vehicle_ids))
        return status__tupel


    def get_status(self,data, status__tupel):
        res =[]
        if status__tupel:
            res =[]
            vehicle_obj = self.pool.get('fleet.vehicle')
            translation_obj = self.pool.get('ir.translation')
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('vehicle_status','in',status__tupel)])
            count = 0
            '''vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}'''
            for rec in vehicle_obj.browse(self.cr, self.uid,vehicle_ids):
                '''key = rec.vehicle_status
                if key:
                    key = vehicle_status[key]
                    translation_ids = translation_obj.search(
                        self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                    translation_recs = translation_obj.read(
                        self.cr, self.uid, translation_ids, [])
                    key = translation_recs and translation_recs[0]['value'] or key'''

                emp_name = False
                degree_name = False
                if rec.employee_id:
                    emp_name = rec.employee_id.name.encode('utf-8')
                    degree_name = rec.employee_id.degree_id.name.encode('utf-8')

                elif rec.driver:
                    emp_name = rec.driver.name.encode('utf-8')
                    degree_name = rec.driver.degree_id.name.encode('utf-8')

                else:
                    #if rec.old_system_driver:
                    emp_name = rec.old_system_driver and rec.old_system_driver.encode('utf-8') or False
                    degree_name = rec.old_system_degree and rec.old_system_degree.encode('utf-8') or False

                count = count + 1
                '''new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    #'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'employee_name':rec.employee_id and rec.employee_id.name.encode('utf-8') or False,
                    'employee_name': emp_name,
                    #'driver_name': rec.driver_id and rec.driver_id.name.encode('utf-8') or False,
                    'driver_name': emp_name,
                    'degree_name': degree_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                    'year': rec.year or False,
                }'''
                new_dict = {
                    'count': count,
                    'vin_sn': rec.vin_sn,
                    'license_plate': rec.license_plate,
                    'machine_no': rec.machine_no,
                    'year': rec.year,
                    'model_name': rec.model_id and rec.model_id.name.encode('utf-8') or False,
                    'type': rec.type and rec.type.name.encode('utf-8') or False,
                    #'vehicle_status': key and key.encode('utf-8') or rec.vehicle_status,
                    'use_name': rec.use and rec.use.name.encode('utf-8') or False,
                    'ownership_name': rec.ownership and rec.ownership.name.encode('utf-8') or False,
                    #'degree_name': rec.degree_id and rec.degree_id.name.encode('utf-8') or False,
                    'degree_name': degree_name,
                    'employee_name':emp_name,
                    'driver_name': emp_name,
                    'department_name': rec.department_id and rec.department_id.name.encode('utf-8') or False,
                }
                res.append(new_dict)
            
        return res



    ################ for Vehicle Under Department Custody ####################
    def get_department_custody_name(self,data):
        departments_ids = []
        department__tupel = []
        vehicle_obj = self.pool.get('fleet.vehicle')
        vehicle_move_obj = self.pool.get('vehicle.move')
        employee_obj = self.pool.get('hr.employee')
        if data['uses_ids']: 
            departments_ids = data['departments_ids']
        else:
            departments_ids = self.pool.get('hr.department').search(self.cr, self.uid, [])
        for x in self.pool.get('hr.department').browse(self.cr, self.uid, departments_ids):
            domain = [('department_id','in',[x.id])]
            emplyee_ids = employee_obj.search(self.cr, self.uid, [('department_id','in',[x.id]),('state','=','approved')])
            if emplyee_ids:
                domain.append(('employee_id','in',emplyee_ids))
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, domain)
            #vehicle_ids = vehicle_obj.search(self.cr, self.uid, [('department_id','in',[x.id])])
            move_ids = vehicle_move_obj.search(self.cr, self.uid, [('previous_department_id','in',[x.id]),])
            if vehicle_ids:
                department__tupel.append((x.id, x.name.encode('utf-8'), vehicle_ids))

        return department__tupel




    

report_sxw.report_sxw('report.vehicle_report','fleet.vehicle','addons/admin_affairs/report/vehicle_report.rml',parser=vehicle_report, header='internal landscape')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
