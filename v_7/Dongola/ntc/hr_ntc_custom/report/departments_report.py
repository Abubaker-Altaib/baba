from openerp.report import report_sxw


class department_pyramidal(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(department_pyramidal, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line': self._get_data,
        })

    def _get_data(self, data):
        departments_ids = data['form']['departments_ids']
        department_obj = self.pool.get('hr.department')
        employee_obj = self.pool.get('hr.employee')
        if not departments_ids:
            departments_ids = department_obj.search(
                self.cr, self.uid, [], context=self.context)

        departments_list = []
        counted_deps = []
        for department in department_obj.browse(self.cr, self.uid, departments_ids, context=self.context):
            line = {
                'name': department.name, 'category': department.cat_id.name,
                'manager': department.manager_id.name_related,
                'inner_departments': [], 'employees': []
            }
            inner_departments_ids = department_obj.search(
                self.cr, self.uid, [('id', 'child_of', department.id)], context=self.context)
            inner_departments = department_obj.read(
                self.cr, self.uid, inner_departments_ids, ['name'], context=self.context)
            inner_departments = filter(
                lambda x: x['id'] != department.id, inner_departments)
            inner_departments = [x['name'] for x in inner_departments]
            line['inner_departments'] = inner_departments

            employees_ids = employee_obj.search(self.cr, self.uid, [(
                'department_id', 'in', inner_departments_ids)], context=self.context)
            employees = employee_obj.read(self.cr, self.uid, employees_ids, [
                                          'name_related', 'department_id'], context=self.context)
            employees = [{'name': x['name_related'], 'department':x[
                'department_id'][1]} for x in employees]
            line['employees'] = employees
            
            departments_list.append(line)
        
        return departments_list

report_sxw.report_sxw('report.department.pyramidal', 'hr.department',
                      'addons/hr_ntc_custom/report/departments_report.rml',
                      parser=department_pyramidal, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
