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
from itertools import groupby
from operator import itemgetter
import math 

class total_vehicle_report(report_sxw.rml_parse):
    """ To manage vehicle report """

    def __init__(self, cr, uid, name, context):
        super(total_vehicle_report, self).__init__(cr, uid, name, context)
        self.total = {'vehicle_ids':[], 'headers':[], 'data':[], 'datas':[]}
        self.name = {'name':''}
        self.sum = 0
        self.page_break = {'count': 0}
        self.header_break = {'count': 0}
        self.data_break = {'count': 0}
        self.localcontext.update({
            'time': time,
            'math': math.ceil,
            'vehicle_list': self.get_vehicle_name,
            'vehicle_data': self.get_headers,
            'page_break': self.get_page_break,
            'header_break': self.get_header_break,
            'data_break': self.get_data_break,
            'header_count': self.get_header_count,
            'data_count': self.get_data_count,
            'loop_num': self.get_num_of_loop,
            'get_sum':self.get_sum

        })



    def get_vehicle_name(self,data):
        vehicle_ids = []
        vehicle__tupel = []
        vehicle_obj = self.pool.get('fleet.vehicle')
        domain = []
        res = []
        header_list = []
        data_list = []
        self.total = {'vehicle_ids':[], 'headers':[]}
        self.sum = 0
       
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

        '''if data['ownership_id']:
            domain.append(('ownership','in',[data['ownership_id'][0]]))'''

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

        if data['status']:
                domain.append(('status','in',[data['status']]))

        if data['old_system_driver']:
                domain.append(('old_system_driver','ilike',data['old_system_driver']))

        order = ''
        if 'included_department' in data and data['included_department'] == True:
            order += 'department_id '
       
        '''if order:
            vehicle_ids = vehicle_obj.search(self.cr, self.uid, domain)
        
        else:'''
        vehicle_ids = vehicle_obj.search(self.cr, self.uid, domain)
        
        if vehicle_ids:
                vehicle__tupel.append((1, vehicle_ids))
                self.total = {'vehicle_ids':vehicle_ids}
                self.cr.execute("SELECT count(fleet.id) as count, model.modelname as model "\
                            "FROM fleet_vehicle fleet " \
                            #"left join vehicle_category cat ON (fleet.type = cat.id) "\
                            "left join fleet_vehicle_model model ON (fleet.model_id = model.id) "\
                            "WHERE fleet.id in %s " \
                            "group by model.modelname, fleet.model_id " , (tuple(vehicle_ids),) )  

                res = self.cr.dictfetchall()
                for x in res:
                    header_list.append(x['model'])
                    data_list.append([x])
                grouped_lines = dict((k, [v for v in itr]) for k, itr in groupby(res, itemgetter('model')))
                
                self.total['headers'] = header_list
                self.total['data'] = data_list
                total = 0
                for x in data_list:
                    total += x[0]['count']
                self.sum = total
                total = []
                self.total['datas'] = res

        return res



    def get_headers(self,data):
        return self.total


    def get_page_break(self, data):
        
        if self.page_break['count'] < 25:
            self.page_break['count'] += 1
        else:
            self.page_break['count'] = 0 

        return self.page_break


    def get_header_break(self, data):
        
        self.header_break['count'] += 1
        return [self.header_break]

    def get_header_count(self, data):
        return self.header_break['count']


    def get_data_break(self, data):
        
        self.data_break['count'] += 1
        return [self.data_break]

    def get_data_count(self, data):
        
        return self.data_break['count']

    def get_num_of_loop(self, data):
        count  = math.ceil(float(len(self.total['datas'])) / 17)
        return int(count)

    def get_sum(self):
        return self.sum

    

report_sxw.report_sxw('report.total_vehicle_number_report','fleet.vehicle','addons/admin_affairs/report/total_vehicle_number_report.mako',parser=total_vehicle_report, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
