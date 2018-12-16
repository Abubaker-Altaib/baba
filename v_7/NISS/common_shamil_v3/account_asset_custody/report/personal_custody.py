# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import pooler
import copy
from report import report_sxw
import pdb
import re
from osv import fields, osv
from openerp.tools.translate import _


class asset_custody_personal_reports(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(asset_custody_personal_reports, self).__init__(
            cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_data': self._get_data,
            'get_filters': self._get_filters,
            'get_name': self._get_name


        })

    def _get_filters(self, data):
        dep_obj = self.pool.get('hr.department')
        pro_obj = self.pool.get('product.product')
        office_obj = self.pool.get('office.office')
        type_obj = self.pool.get('product.category')
        result = []
        if data['department_id']:
            department = data['department_id'][1]

            result.append({

                'department': department.encode('utf-8'),

            })

        if data['product_id']:
            product = data['product_id'][1]
            result.append({

                'product': product.encode('utf-8'),

            })

        if data['cat_id']:
            cat = data['cat_id'][1]
            result.append({
                'cat': cat.encode('utf-8'),

            })

        if data['employee_id']:
            employee = data['employee_id'][1]
            result.append({
                'employee': employee.encode('utf-8'),
            })

        return result

    def _get_data(self, data):

        all_data = []
        #and c.state_rm = 'assigned' deprecated by add state column in the report
        self.cr.execute('''
                        SELECT c.state_rm ,c.request_date AS date ,c.executing_agency as agency ,p.name_template as product ,p.id as product_id \
                        ,pp.id as cat_id , pp.name as cat  ,
                        ppp.name_related as emp ,ppp.id as emp_id ,ppp.otherid as otherid , pppc.name as degree ,
                        pppp.id as dept_id , pppp.name as dept
                        FROM account_asset_asset c 
                        LEFT JOIN product_product p ON (c.product_id=p.id)
                        LEFT JOIN product_template pt ON (p.id=pt.id)
                        LEFT JOIN product_category pp ON (pt.categ_id=pp.id)
                        LEFT JOIN hr_employee ppp ON (c.employee_id=ppp.id)
                        LEFT JOIN hr_salary_degree pppc ON (ppp.degree_id=pppc.id)
                        LEFT JOIN hr_department pppp ON (ppp.department_id=pppp.id)
                        where
                        c.custody_type = 'personal' and state_rm='assigned'
                        order by 
                        dept_id,ppp.id,c.request_date
                        ''')

        all_data = self.cr.dictfetchall()

        all_data = [x for x in all_data if x['product_id']
                    != None and x['emp_id'] != None]

        if data['executing_agency']:
            all_data = [x for x in all_data if x['agency']
                        == data['executing_agency']]

        
        type_obj = self.pool.get('product.category')
        department_obj = self.pool.get('hr.department')
        # FILTERS

        if data['product_id']:
            all_data = [x for x in all_data if x['product_id']
                        == data['product_id'][0]]

        if data['cat_id']:
            cat_ids = type_obj.search(
                self.cr, self.uid, [('id', 'child_of', data['cat_id'][0])])

            all_data = [x for x in all_data if x['cat_id'] in cat_ids]

        if data['department_id']:
            department_ids = department_obj.search(
                self.cr, self.uid, [('id', 'child_of', data['department_id'][0])])

            all_data = [x for x in all_data if x['dept_id'] in department_ids]
        

        if data['employee_id']:
            all_data = [x for x in all_data if x['emp_id']
                        == data['employee_id'][0]]


        return all_data

    def _get_name(self, data):
        name = (data == 'tech' and 'فرع اﻹمداد الفني') or \
        (data == 'admin' and 'ادارة المهام') or \
        (data == 'arms' and 'ادارة السلاح') or \
        (data == 'draft' and 'جديد') or \
        (data == 'released' and 'مزالة') or \
        (data == 'assigned' and 'مسندة') or \
        (data == 'damage' and 'تالف') or ""
        return name


report_sxw.report_sxw('report.asset.custody.personal', 'asset.custody', 'addons/account_asset_custody/report/personal_custody.rml',
                      parser=asset_custody_personal_reports, header='custom landscape')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
