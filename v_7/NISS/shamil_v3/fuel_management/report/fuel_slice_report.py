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

class fuel_slice_report(report_sxw.rml_parse):
    """ To manage vehicle report """

    def __init__(self, cr, uid, name, context):
        super(fuel_slice_report, self).__init__(cr, uid, name, context)
        self.total = {'record_ids':[]}
        self.page_break = {'count': 0}
        self.name = {'name':''}
        self.localcontext.update({
            'time': time,
            'record_list': self.get_record_name,
            'record_data': self.get_data,
            'selection': self.get_wiz_selection,
            'status': self.get_status,
            'page_break': self.get_page_break,
            'total_data': self.get_total_data,
        })


    def get_wiz_selection(self,data):
        res = []
        dicts = {}
        translation_obj = self.pool.get('ir.translation')
        process_type = {'modify': 'Modify','insert':'Insert'}

        key = data['process_type']
        if key:
            key = process_type[key]
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [])
            key = translation_recs and translation_recs[0]['value'] or key

        dicts['date_from'] = data['date_from']

        dicts['date_to'] = data['date_to']

        dicts['type'] = data['category_id'] and data['category_id'][1] or u'كل التصنيفات'
        
        dicts['year'] = data['year'] and data['year'] or u'كل الموديلات'
                
        dicts['department_id'] = data['department_id'] and data['department_id'][1] or u'كل الادارات'
        dicts['process_type'] = data['process_type'] and key or u'تعديل و ادخال'

        res.append(dicts)

        return res

    def get_record_name(self,data):
        record_ids = []
        record__tupel = []
        vehicle_fuel_slice_obj = self.pool.get('vehicle.fuel.slice')
        vehicle_obj = self.pool.get('fleet.vehicle')
        domain = []
        domain2 = []
        self.total = {'record_ids':[]}


        '''if data['vehicle_id']:
            domain.append(('id','in',[data['vehicle_id'][0]])) 
        else:'''
        domain += [('date','>=',data['date_from']),('date','<=',data['date_to']),('state','=','confirm')]
        if data['category_id']:
            domain.append(('type','in',[data['category_id'][0]]))

        if data['department_id']:
            department_ids = [data['department_id']]
            if data['included_department'] == True:
                domain.append(('department_id','child_of',[data['department_id'][0]]))
            else:
                domain.append(('department_id','in',[data['department_id'][0]]))


        if data['year']:
            domain.append(('year','in',[data['year']]))

        if data['process_type']:
            domain.append(('process_type','in',[data['process_type']]))

        
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
        record_ids = vehicle_fuel_slice_obj.search(self.cr, self.uid, domain)

        
        if vehicle_fuel_slice_obj:
                record__tupel.append((1, record_ids))
                self.total = {'record_ids':record_ids}
        return record__tupel


    def get_data(self,data):
        res =[]
        vehicle_ids = []
        vehicle__tupel = []
        res =[]
        vehicle_obj = self.pool.get('fleet.vehicle')
        translation_obj = self.pool.get('ir.translation')
        self.page_break = {'count': 0}


        if 'record' in data:
            self.total['record_ids'] = [data['record'].id]
        record_ids = self.total['record_ids']

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
            order_by += "fuel.date desc, fuel.id desc"



        vehicle_status = {'operation': 'Operational Use','internal':'Internal Use',
                            'supply_custody':'Supply Custody','disabled':'Disabled','off':'Off',
                            'custody': 'Custody','sold':'Sold','for_sale':'For Sale',
                            'removal': 'Removal','missing': 'Missing'}


        if record_ids:

            self.cr.execute("SELECT count(fuel.id) as count, fuel.vin_sn as vin_sn, fuel.license_plate as license_plate, fuel.fuel_slice as fuel_slice,"\
                            "fuel.machine_no as machine_no, fuel.year as year, fuel.fuel_type as fuel_type, dep.name as department_name, "\
                            "emp_res.name AS employee_name, emp_deg.name AS employee_degree,"\
                            "model.name AS model_name, cat.name as type "\
                            "FROM vehicle_fuel_slice fuel " \
                            #"FROM fleet_vehicle fleet,hr_employee emp,hr_employee driver,hr_salary_degree emp_deg,hr_salary_degree driver_deg, "\
                            #"hr_department dep,resource_resource emp_res,resource_resource driver_res,fleet_vehicle_model model,vehicle_category cat, " \
                            #"fleet_vehicle_use use, fleet_vehicle_ownership ownership " \
                            "left join fleet_vehicle fleet ON (fuel.vehicle_id = fleet.id) "\
                            "left join hr_employee emp ON (fuel.employee_id = emp.id) "\
                            "left join hr_salary_degree emp_deg on (emp_deg.id= fuel.degree_id) "\
                            "left join hr_department dep ON (fuel.department_id = dep.id) "\
                            "left join resource_resource emp_res ON (emp.resource_id = emp_res.id) "\
                            "left join fleet_vehicle_model model ON (fuel.model_id = model.id) "\
                            "left join vehicle_category cat ON (fuel.type = cat.id) "\
                            "WHERE fuel.id in %s " \
                            "group by fuel.id, fuel.vin_sn, fuel.license_plate, fuel.machine_no, fuel.year, fuel.fuel_type,dep.name," \
                            "emp_res.name, emp_deg.name,model.name, cat.name, dep.id,model.id " \
                            "order by " + order_by + "", (tuple(record_ids),) )  


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
        if self.page_break['count'] == 8 and i == 8:
            self.page_break['count'] = 13
        elif self.page_break['count'] < 13:
            self.page_break['count'] += 1
        else:
            self.page_break['count'] = 0 

        return self.page_break


    

report_sxw.report_sxw('report.fuel_slice_report','fleet.vehicle','addons/fuel_management/report/fuel_slice_report.mako',parser=fuel_slice_report, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
