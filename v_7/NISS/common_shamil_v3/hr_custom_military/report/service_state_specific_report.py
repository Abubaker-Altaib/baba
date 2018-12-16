import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler


def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class service_state_specific(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(service_state_specific, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'department_h': self._get_department_h,
            'dep_h_len': self._get_dep_h_len,
            #'job_groups_len_by_one': self._get_job_groups_len_by_one,
            #'job_groups_data_by_one': self._get_job_groups_data_by_one,
        })

    def _get_all_len(self, data):
        self.emp_obj = self.pool.get('hr.employee')
        self.hr_department_cat_obj = self.pool.get('hr.department.cat')
        self.hr_department_obj = self.pool.get('hr.department')

        type = data['form']['type']


        self.cr.execute( "select id from hr_job where type='"+type+"'")
        service_state_ids = self.cr.fetchall()
        service_state_ids = [x[0] for x in service_state_ids]

        #good practice error
        service_state_ids += service_state_ids

        service_state_ids = set(service_state_ids)


        #self.cr.execute( "select id from hr_employee where service_state_id in"+service_state_ids)
        self.cr.execute( "select id from hr_employee")
        emp_ids = self.cr.fetchall()
        self.emp_ids = [x[0] for x in emp_ids]

        emps = self.emp_obj.browse(self.cr, self.uid, self.emp_ids)

        self.all_data = emps
        self.all_dep_ids = list(
            set([x.department_id.id for x in self.all_data]))

        hr_department_cat_ids = self.hr_department_cat_obj.search(self.cr, self.uid, [(
            'category_type', '=', 'corp')])

        hr_h_dep_ids = self.hr_department_obj.search(self.cr, self.uid, [(
            'cat_id', 'in', hr_department_cat_ids), ('parent_id','!=',False)])

        self.h_deps_ids = [x for x in self.all_dep_ids if x in hr_h_dep_ids]
        self.h_deps_ids = list(set(self.h_deps_ids))

        return len(emps)

    def _get_department_h(self):
        return self.hr_department_obj.browse(self.cr, self.uid, self.h_deps_ids)

    def _get_dep_h_len(self, dep_id):
        data = self.emp_obj.search(self.cr, self.uid, [('id', 'in', self.emp_ids), (
            'department_id', 'child_of', dep_id)])
        return len(data)

    def _get_job_groups_data_by_one(self, group_id):
        data = filter(lambda x: x.employee_id.parent_job_id.id ==
                      group_id, self.all_data)
        return data


report_sxw.report_sxw('report.service_state_specific.report', 'hr.employee',
                      'addons/hr_custom_military/report/service_state_specific_report.rml', parser=service_state_specific, header='internal landscape')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
