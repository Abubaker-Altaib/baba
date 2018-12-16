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

class total_vehicle_report(report_sxw.rml_parse):
    """ To manage vehicle report """

    def __init__(self, cr, uid, name, context):
        super(total_vehicle_report, self).__init__(cr, uid, name, context)
        self.total = {'vehicle_ids':[]}
        self.page_break = {'count': 0}
        self.name = {'name':''}
        self.localcontext.update({
            'time': time,
            'vehicle_list': self.get_vehicle_name,
            'vehicle_data': self.get_vehicle,
            'selection': self.get_wiz_selection,
            'status': self.get_status,
            'page_break': self.get_page_break,
            'total_data': self.get_total_data,
        })


    def get_wiz_selection(self,data):
        res = []
        dicts = {}
        translation_obj = self.pool.get('ir.translation')
        vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}

        key = data['vehicle_status']
        if key:
            key = vehicle_status[key]
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [])
            key = translation_recs and translation_recs[0]['value'] or key

        dicts['vehicle_id'] = data['vehicle_id'] and u'بيانات مركبة معينة' or u'كل المركبات'
        dicts['type'] = data['category_id'] and data['category_id'][1] or u'كل التصنيفات'
        
        dicts['year'] = data['year'] and data['year'] or u'كل الموديلات'
        
        dicts['model_id'] = data['model_id'] and data['model_id'][1] or u'كل الماركات'
        
        dicts['department_id'] = data['department_id'] and data['department_id'][1] or u'كل الادارات'
        
        dicts['degree_id'] = data['degree_id'] and data['degree_id'][1] or u'كل الرتب'
        
        dicts['use_id'] = data['use_id'] and data['use_id'][1] or u'كل الاستخدامات'
        
        dicts['vehicle_status'] = data['vehicle_status'] and key or u'كل الحالات'

        dicts['employee_id'] = u'كل العضوية'

        if data['employee_id']:
            emp_rec = self.pool.get('hr.employee').browse(self.cr, self.uid, data['employee_id'][0])
            emp_name = emp_rec.name.encode('utf-8')
            dicts['employee_id'] = emp_name

        res.append(dicts)

        return res

    def get_vehicle_name(self,data):
        vehicle_ids = []
        vehicle__tupel = []
        vehicle_obj = self.pool.get('fleet.vehicle')
        domain = []
        self.total = {'vehicle_ids':[]}


        if data['vehicle_id']:
            domain.append(('id','in',[data['vehicle_id'][0]])) 
        else:
            if data['category_id']:
                domain.append(('type','in',[data['category_id'][0]]))

            if data['department_id']:
                department_ids = [data['department_id']]
                if data['included_department'] == True:
                    domain.append(('department_id','child_of',[data['department_id'][0]]))
                else:
                    domain.append(('department_id','in',[data['department_id'][0]]))

            if data['model_id']:
                domain.append(('model_id','in',[data['model_id'][0]]))

            if data['ownership_id']:
                domain.append(('ownership','in',[data['ownership_id'][0]]))

            if data['use_id']:
                domain.append(('use','in',[data['use_id'][0]]))

            if data['degree_id']:
                domain.append(('degree_id','in',[data['degree_id'][0]]))

            if data['year']:
                domain.append(('year','in',[data['year']]))

            if data['vehicle_status']:
                domain.append(('vehicle_status','in',[data['vehicle_status']]))

            if data['employee_id']:
                domain += ['|',('employee_id','in',[data['employee_id'][0]]),('driver','in',[data['employee_id'][0]]) ]
                #domain.append(('employee_id','in',[data['employee_id'][0]]))

            if data['brand_id'] :
                models_ids = []
                if data['models_ids']:
                    models_ids = data['models_ids']
                else:
                    models_ids = self.pool.get('fleet.vehicle.model').search(self.cr, self.uid, [('brand_id','in',[data['brand_id'][0]])])

                if models_ids:
                    domain.append(('model_id','in',models_ids))

            if data['status']:
                    domain.append(('status','in',[data['status']]))

            if data['old_system_driver']:
                    domain.append(('old_system_driver','ilike',data['old_system_driver']))

            if data['place_id']:
                domain.append(('location','in',[data['place_id'][0]]))

        order = ''
        '''if 'included_department' in data and data['included_department'] == True:
            order += 'department_id '
        if 'brand_id' in data and data['brand_id']:
            if not order:
                order += 'model_id '
            else:
                order += ', model_id '
        if order:
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, domain, order=order)
        
        else'''
        vehicle_ids = vehicle_obj.search(self.cr, self.uid, domain)
        
        if vehicle_ids:
                vehicle__tupel.append((1, vehicle_ids))
                self.total = {'vehicle_ids':vehicle_ids}
        return vehicle__tupel


    def get_vehicle(self,data):
        res =[]
        vehicle_ids = []
        vehicle__tupel = []
        res =[]
        vehicle_obj = self.pool.get('fleet.vehicle')
        translation_obj = self.pool.get('ir.translation')
        self.page_break = {'count': 0}


        if 'record' in data:
            self.total['vehicle_ids'] = [data['record'].id]
        vehicle_ids = self.total['vehicle_ids']

        domain = []

        order = ''
        order_by = ""
        '''if 'included_department' in data and data['included_department'] == True:
            order += 'department_id '
            order_by += "dep.id "
        if 'brand_id' in data and data['brand_id']:
            if not order:
                order += 'model_id '
                order_by += "model.id "
            else:
                order += ', model_id '
                order_by += " , model.id " '''
        if not order_by:
            order_by += "fleet.year desc"



        vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}


        if vehicle_ids:


            self.cr.execute("SELECT count(fleet.id) as count, fleet.vin_sn as vin_sn, fleet.license_plate as license_plate, fleet.vehicle_status as vehicle_status, "\
                            "fleet.old_system_driver as old_system_driver, fleet.old_system_degree as old_system_degree, "\
                            "fleet.machine_no as machine_no, fleet.year as year, fleet.fuel_type as fuel_type, dep.name as department_name, "\
                            "emp_res.name AS employee_name, driver_res.name AS driver_name,"\
                            "emp_deg.name AS employee_degree, driver_deg.name AS driver_degree,"\
                            "model.name AS model_name, cat.name as type, use.name as use_name, ownership.name as ownership_name, place.name as place_name "\
                            "FROM fleet_vehicle fleet " \
                            #"FROM fleet_vehicle fleet,hr_employee emp,hr_employee driver,hr_salary_degree emp_deg,hr_salary_degree driver_deg, "\
                            #"hr_department dep,resource_resource emp_res,resource_resource driver_res,fleet_vehicle_model model,vehicle_category cat, " \
                            #"fleet_vehicle_use use, fleet_vehicle_ownership ownership " \
                            "left join hr_employee emp ON (fleet.employee_id = emp.id) "\
                            "left join hr_employee driver ON (fleet.driver = driver.id) "\
                            "left join hr_salary_degree emp_deg on (emp_deg.id= emp.degree_id) "\
                            "left join hr_salary_degree driver_deg on (driver_deg.id= driver.degree_id) "\
                            "left join hr_department dep ON (fleet.department_id = dep.id) "\
                            "left join resource_resource emp_res ON (emp.resource_id = emp_res.id) "\
                            "left join resource_resource driver_res ON (driver.resource_id = driver_res.id) "\
                            "left join fleet_vehicle_model model ON (fleet.model_id = model.id) "\
                            "left join vehicle_category cat ON (fleet.type = cat.id) "\
                            "left join fleet_vehicle_use use ON (fleet.use = use.id) "\
                            "left join vehicle_place place ON (fleet.location = place.id) "\
                            "left join fleet_vehicle_ownership ownership ON (fleet.ownership = ownership.id) "\
                            "WHERE fleet.id in %s " \
                            "group by fleet.id, fleet.vin_sn, fleet.license_plate, fleet.old_system_driver,fleet.old_system_degree, fleet.vehicle_status,use.name, " \
                            "fleet.machine_no, fleet.year, fleet.fuel_type,dep.name,emp_res.name, driver_res.name, emp_deg.name,driver_deg.name,model.name, cat.name,ownership.name,dep.id,model.id, place.name " \
                            "order by " + order_by + "", (tuple(vehicle_ids),) )  

            res = self.cr.dictfetchall()
           
            
            
        return res

    def get_total_data(self,data):
        return self.total['vehicle_ids']

    def get_status(self,status):
        vehicle_obj = self.pool.get('fleet.vehicle')
        translation_obj = self.pool.get('ir.translation')

        vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}

        #key = line['vehicle_status']
        if status:
            status = vehicle_status[status]
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('src','=', status), ('lang', '=', 'ar_SY')])
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [])
            status = translation_recs and translation_recs[0]['value'] or status

        return status

    def get_page_break(self, data, i):
        if self.page_break['count'] == 11 and i == 11:
            self.page_break['count'] = 13
        elif self.page_break['count'] < 13:
            self.page_break['count'] += 1
        else:
            self.page_break['count'] = 0 

        return self.page_break


    

report_sxw.report_sxw('report.total_vehicle_report_menu','fleet.vehicle','addons/admin_affairs/report/total_vehicle_report.rml',parser=total_vehicle_report, header='internal landscape')
report_sxw.report_sxw('report.total_vehicle_report','fleet.vehicle','addons/admin_affairs/report/total_vehicle_report.mako',parser=total_vehicle_report, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
