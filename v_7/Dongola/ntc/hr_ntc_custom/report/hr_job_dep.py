# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.report import report_sxw
from itertools import groupby
from operator import itemgetter
import time

class report_job_dep(report_sxw.rml_parse):

    globals()['total'] = 0
    globals()['available'] = 0
    globals()['curr_num'] = 0
    
    def __init__(self, cr, uid, name, context):
        super(report_job_dep, self).__init__(cr, uid, name, context)
        self.info = {'levels':0, 'company':'','title':''}
        self.localcontext.update({
            'main': self.create_xml,
            'parent':self.parent_dep,
            'child_dep': self.child_dep,
            'total': self._total,
            'user':self._get_user,
        })

        globals()['total'] = 0
        globals()['available'] = 0
        globals()['curr_num'] = 0


    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name


    def parent_dep(self, data):
        job_obj = self.pool.get('hr.job')
        employee_substitution_obj = self.pool.get('hr.employee.substitution')
        department_obj = self.pool.get('hr.department')
        department_cat_obj = self.pool.get('hr.department.cat')
        employee_obj = self.pool.get('hr.employee')
        departments_ids = data['department_ids']
        result = []

        if not departments_ids:
            cat_ids = department_cat_obj.search(self.cr, self.uid, [('category_type','=','high_dep')])
            cat_ids2 = department_cat_obj.search(self.cr, self.uid, [('category_type','=','general_dep')])
            departments_ids = department_obj.search(self.cr, self.uid, [('cat_id','in',cat_ids),('parent_id','!=',False)])
            departments_ids += department_obj.search(self.cr, self.uid, [('cat_id','in',cat_ids2),('parent_id','!=',False)])
        for department in department_obj.browse(self.cr, self.uid,departments_ids):
            name = (department.name).encode('utf-8')
            department.cat_id and (department.cat_id.name).encode('utf-8') or '-'
            parent = department.parent_id and (department.parent_id.name).encode('utf-8') or '-'
            no_job = 0
            cat = department.cat_id and (department.cat_id.name).encode('utf-8') or '-'
            job_list = []
            for x in department.job_ids:
                num = 0
                job_name = (x.name).encode('utf-8')
                degree_list = []
                degree_name = ''
                degree_name = ''
                for y in x.degree_ids:
                    if degree_name != '':
                        degree_name += '/'
                    degree_name += y.name.encode('utf-8')
                degree_list.append({'name':degree_name})
                for z in x.deparment_ids:
                    if z.department_id == department:
                        num += z.no_emp
                no_job += num
                job_list.append({'name':job_name,'degree_id':degree_list,'num':num})
            result.append({'rec':department,'name':name,'cat':cat,'parent':parent,'job':job_list,'no_job':no_job})
        return result


    def child_dep(self, data, rec,job_num):
        job_obj = self.pool.get('hr.job')
        employee_substitution_obj = self.pool.get('hr.employee.substitution')
        department_obj = self.pool.get('hr.department')
        department_cat_obj = self.pool.get('hr.department.cat')
        employee_obj = self.pool.get('hr.employee')
        departments_ids = data['department_ids']
        result = []
        res = []

        for department in rec.child_ids:
            if department.cat_id.category_type == 'general_dep':
                name = (department.name).encode('utf-8')
                cat = department.cat_id and (department.cat_id.name).encode('utf-8') or '-'
                parent = department.parent_id and (department.parent_id.name).encode('utf-8') or '-'
                no_job = 0
                job_list = []
                for x in department.job_ids:
                    job_name = (x.name).encode('utf-8')
                    degree_list = []
                    degree_name = ''
                    num = 0
                    degree_name = ''
                    for y in x.degree_ids:
                        if degree_name != '':
                            degree_name += '/'
                        degree_name += y.name.encode('utf-8')
                    degree_list.append({'name':degree_name})
                    for z in x.deparment_ids:
                        if z.department_id == department:
                            num += z.no_emp
                    no_job += num
                    job_num += no_job
                    job_list.append({'name':job_name,'degree_id':degree_list,'num':num})
                result.append({'rec':department,'name':name,'cat':cat,'parent':parent, 'job':job_list,'no_job':no_job,'total':job_num})
            else:
                dep_child = department_obj.search(self.cr,self.uid,[('id','child_of',department.id)])
                dep_child += [department.id]
                job_child = []
                for d1 in department_obj.browse(self.cr,self.uid,dep_child):
                    job_child += [d2 for d2 in d1.job_ids]
                name = (department.name).encode('utf-8')
                cat = department.cat_id and (department.cat_id.name).encode('utf-8') or '-'
                parent = department.parent_id and (department.parent_id.name).encode('utf-8') or '-'
                job_list = []
                no_job = 0
                """if len(department.job_ids) > 4:
                    print "-------------------department.job_ids[:4]", department.id,department.job_ids[:4], department.job_ids[5:]
                    for x in department.job_ids[:4]:
                        job_name = (x.name).encode('utf-8')
                        degree_list = []
                        degree_name = ''
                        num = 0
                        degree_name = ''
                        for y in x.degree_ids:
                            if degree_name != '':
                                degree_name += '/'
                            degree_name += y.name.encode('utf-8')
                        degree_list.append({'name':degree_name})
                        for z in x.deparment_ids:
                            if z.department_id == department:
                                num += z.no_emp
                        no_job += num
                        job_num += no_job
                        job_list.append({'name':job_name,'degree_id':degree_list,'num':num})
           
                    result.append({'rec':department,'name':name,'cat':cat,'parent':parent, 'job':job_list,'no_job':no_job,'total':job_num})

                    job_list = []
                    for x in department.job_ids[4:]:
                        job_name = (x.name).encode('utf-8')
                        degree_list = []
                        degree_name = ''
                        num = 0
                        degree_name = ''
                        for y in x.degree_ids:
                            if degree_name != '':
                                degree_name += '/'
                            degree_name += y.name.encode('utf-8')
                        degree_list.append({'name':degree_name})
                        for z in x.deparment_ids:
                            if z.department_id == department:
                                num += z.no_emp
                        no_job += num
                        job_num += no_job
                        job_list.append({'name':job_name,'degree_id':degree_list,'num':num})
                    
                    result.append({'rec':department,'name':name,'cat':cat,'parent':parent, 'job':job_list,'no_job':no_job,'total':job_num})

                else:"""
                #for x in department.job_ids:
                dep_child_ids = []
                dep_child_ids += [d3.id for d3 in department.child_ids]
                dep_child_ids += [department.id]
                for x in job_child:
                    job_name = (x.name).encode('utf-8')
                    degree_list = []
                    degree_name = ''
                    num = 0
                    degree_name = ''
                    for y in x.degree_ids:
                        if degree_name != '':
                            degree_name += '/'
                        degree_name += y.name.encode('utf-8')
                    degree_list.append({'name':degree_name})
                    for z in x.deparment_ids:
                        if z.department_id.id in dep_child_ids:
                            num += z.no_emp
                    no_job += num
                    job_num += no_job
                    job_list.append({'name':job_name,'degree_id':degree_list,'num':num})
                result.append({'rec':department,'name':name,'cat':cat,'parent':parent, 'job':job_list,'no_job':no_job,'total':job_num})
                
                '''for dep in department.child_ids:
                    name = (dep.name).encode('utf-8')
                    cat = dep.cat_id and (dep.cat_id.name).encode('utf-8') or '-'
                    parent = dep.parent_id and (dep.parent_id.name).encode('utf-8') or '-'
                    job_list = []
                    for x in dep.job_ids:
                        job_name = (x.name).encode('utf-8')
                        degree_list = []
                        degree_name = ''
                        for y in x.degree_ids:
                            degree_name = ''
                            degree_name += y.name
                            degree_list.append({'name':degree_name.encode('utf-8')})
                        job_list.append({'name':job_name,'degree_id':degree_list})
                    result.append({'rec':dep,'name':name,'cat':cat,'parent':parent, 'job':job_list})'''
        res.append(result)
        return result
        
                     



    def create_xml(self, data, rec):
        job_obj = self.pool.get('hr.job')
        employee_substitution_obj = self.pool.get('hr.employee.substitution')
        department_obj = self.pool.get('hr.department')
        department_cat_obj = self.pool.get('hr.department.cat')
        employee_obj = self.pool.get('hr.employee')
        departments_ids = data['departments_ids']
        result = []

        for department in rec.child_ids:
            if department.cat_id.category_type == 'general_dep':
                name = (department.name).encode('utf-8')
                cat = (department.cat_id.name).encode('utf-8')
                parent = (department.parent_id.name).encode('utf-8')
                job_list = []
                for x in department.job_ids:
                    job_name = (x.name).encode('utf-8')
                    degree_list = []
                    degree_name = ''
                    for y in x.degree_ids:
                        degree_name = ''
                        degree_name += y.name
                        degree_list.append({'name':degree_name.encode('utf-8')})
                    job_list.append({'name':job_name,'degree_id':degree_list})
                result.append({'rec':department,'name':name,'cat':cat,'parent':parent})
            else:
                name = (department.name).encode('utf-8')
                cat = (department.cat_id.name).encode('utf-8')
                parent = (department.parent_id.name).encode('utf-8')
                job_list = []
                for x in department.job_ids:
                    job_name = (x.name).encode('utf-8')
                    degree_list = []
                    degree_name = ''
                    for y in x.degree_ids:
                        degree_name = ''
                        degree_name += y.name
                        degree_list.append({'name':degree_name.encode('utf-8')})
                    job_list.append({'name':job_name,'degree_id':degree_list})
                result.append({'rec':department,'name':name,'cat':cat,'parent':parent})
                
                for dep in department.child_ids:
                    name = (department.name).encode('utf-8')
                    cat = (department.cat_id.name).encode('utf-8')
                    parent = (department.parent_id.name).encode('utf-8')
                    job_list = []
                    for x in department.job_ids:
                        job_name = (x.name).encode('utf-8')
                        degree_list = []
                        degree_name = ''
                        for y in x.degree_ids:
                            degree_name = ''
                            degree_name += y.name
                            degree_list.append({'name':degree_name.encode('utf-8')})
                        job_list.append({'name':job_name,'degree_id':degree_list})
                    result.append({'rec':department,'name':name,'cat':cat,'parent':parent})
                
        
            


        return result

    def _total(self,data):
        return {'total':globals()['total'], 'available':globals()['available'], 'curr_num' :globals()['curr_num']}


 
report_sxw.report_sxw('report.hr.department.job', 'hr.employee', 'addons/hr_ntc_custom/report/hr_job_dep.rml',parser=report_job_dep, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
