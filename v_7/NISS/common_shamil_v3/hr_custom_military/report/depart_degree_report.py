
# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class depart_degree_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        self.counter = 0
        super(depart_degree_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines':self.lines,
            'degrees':self.get_degrees,
            'departments':self.get_departments,
            'counter':self.get_counter,
            'get_count_degree':self.get_count_degree,
            'get_count_department_degree':self.get_count_department_degree,
            'get_count_all':self.get_count_all,
            'get_count_department':self.get_count_department,
            'sum_name':unicode('المجموع', 'utf-8')
        })
        
    def get_count_department(self, department):
        departments = filter(lambda x :x['department_id'][0] in self.child_deps[department], self.emps_names)
        return len(departments)

    def get_count_all(self):
        return len(self.emps_names)

    def get_count_degree(self, degree):
        degrees = filter(lambda x :x['degree_id'][0] ==  degree, self.emps_names)
        return len(degrees)

    def get_count_department_degree(self, department, degree):
        degrees = filter(lambda x :x['degree_id'][0] ==  degree and (x['department_id'][0] in self.child_deps[department]), self.emps_names)
        return len(degrees)

    def get_counter(self):
        self.counter += 1
        return self.counter

    def get_degrees(self):
        return self.degrees_names

    def get_departments(self):
        return self.departments_names

    def lines(self,data):
        scales_ids = data['form']['scales']
        departments_ids = data['form']['departments']
        scale_obj = self.pool.get('hr.salary.scale')
        department_obj = self.pool.get('hr.department')
        if not scales_ids:
            scales_ids = scale_obj.search(self.cr, self.uid, [])
        
        if not departments_ids:
            departments_ids = department_obj.search(self.cr, self.uid, [('cat_id.category_type','=','organization')])

        degrees_obj = self.pool.get('hr.salary.degree')
        degrees_ids = degrees_obj.search(self.cr, self.uid, [('payroll_id','in',scales_ids)])
        self.degrees_names = degrees_obj.read(self.cr, self.uid, degrees_ids, ['name'])

        self.departments_names = department_obj.read(self.cr, self.uid, departments_ids, ['name'])

        self.child_deps = {}
        all_deps = []
        for dep in departments_ids:
            self.child_deps[dep] = [dep]
            #add childs of a department
            self.child_deps[dep]+= department_obj.search(self.cr, self.uid, [('id','child_of',[dep])])
            all_deps+=self.child_deps[dep]
        emps_obj = self.pool.get('hr.employee')
        emps_ids = emps_obj.search(self.cr, self.uid, [('degree_id','in',degrees_ids),('department_id','in',all_deps) ])
        self.emps_names = emps_obj.read(self.cr, self.uid, emps_ids, ['department_id','degree_id'])

        return True
        


report_sxw.report_sxw('report.hr.depart_degree.report','hr.employee','addons/hr_custom_military/report/depart_degree_report.mako',parser=depart_degree_report,header=False)
