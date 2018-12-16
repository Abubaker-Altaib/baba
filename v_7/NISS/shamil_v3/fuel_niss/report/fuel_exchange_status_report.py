# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from openerp.tools.translate import _


def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class fuel_exchange_status_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):

        self.count = 0
        self.context = context
        super(fuel_exchange_status_report, self).__init__(
            cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
            'get_name': self._get_name,
            'set_count': self._set_count,
        })

    def _get_name(self, data):
        key = _(data)

        name = data
        if data:
            department_obj = self.pool.get('hr.department')
            name = department_obj.name_get_custom(self.cr, self.uid, [data])[0][1]
        return name

    def _to_arabic(self, data):
        key = _(data)
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module', '=', 'hr_custom_military'), ('type', '=', 'selection'), ('src', 'ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key

        return key

    def _get_lines(self, data):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        fuel_type = data['form']['fuel_type']
        fuel_exchange_status = data['form']['fuel_exchange_status']
        use = data['form']['use']
        vehicles_ids = data['form']['vehicles_ids']
        employees_ids = data['form']['employees_ids']
        company_id = data['form']['company_id']

        clouses = False

        if fuel_type:
            if clouses:
                clouses += " and fv.fuel_type='" + str(fuel_type) + "'"
            if not clouses:
                clouses = "fv.fuel_type='" + str(fuel_type) + "'"

        if fuel_exchange_status:
            if clouses:
                clouses += " and arch.fuel_exchange_status='" + \
                    str(fuel_exchange_status) + "'"
            if not clouses:
                clouses = "arch.fuel_exchange_status='" + \
                    str(fuel_exchange_status) + "'"

        if vehicles_ids:
            vehicles_ids += vehicles_ids
            vehicles_ids = tuple(vehicles_ids)
            if clouses:
                clouses += " and fv.id in " + str(vehicles_ids)
            if not clouses:
                clouses = " fv.id in " + str(vehicles_ids)

        if employees_ids:
            employees_ids += employees_ids
            employees_ids = tuple(employees_ids)
            if clouses:
                clouses += " and emp.id in " + str(employees_ids)
            if not clouses:
                clouses = " emp.id in " + str(employees_ids)

        if use:
            use = use[0]
            if clouses:
                clouses += " and use.id=" + str(use)
            if not clouses:
                clouses = " use.id=" + str(use)

        if company_id:
            company_id = company_id[0]
            if clouses:
                clouses += " and fv.company_id=" + str(company_id)
            if not clouses:
                clouses = " fv.company_id=" + str(company_id)

        if start_date:
            if clouses:
                clouses += " and arch.date>='" + str(start_date) + "'"
            if not clouses:
                clouses = " arch.date>='" + str(start_date) + "'"

        if end_date:
            if clouses:
                clouses += " and arch.date<='" + str(end_date) + "'"
            if not clouses:
                clouses = " arch.date<='" + str(end_date) + "'"

        readable_emp_ids = self.pool.get(
            'hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids and False:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in" + str(readable_emp_ids)
            if not clouses:
                clouses = "emp.in in" + str(readable_emp_ids)

        query = """select arch.fuel_exchange_status, fv.name vehicle_name, 
            fv.license_plate, model.name as model_name,
            fv.department_id, emp.name_related as emp_name, 
            emp.otherid, degree.name as degree_name, 
            use.name as use_name, arch.fuel_amount,
            reason.name as reason_name ,
            fv.fuel_type as fuel_type 
            from fuel_exchange_status_archive arch
            left join fleet_vehicle fv on (arch.vehicle_id = fv.id)
            left join hr_salary_degree degree on (fv.degree_id=degree.id)
            left join hr_employee emp on (fv.employee_id=emp.id)
            left join fleet_vehicle_model model on (fv.model_id = model.id)
            left join fleet_vehicle_use use on (fv.use = use.id)
            left join hr_department dep on (fv.department_id = dep.id)
            left join fuel_stop_reasons reason on (arch.fuel_stop_reason_id=reason.id)
                    """

        if clouses:
            query += "where " + clouses
        query += ""
        self.cr.execute(query)
        res = self.cr.dictfetchall()

        self.all_data = res

        return res

    def _get_count(self):
        self.count = self.count + 1
        return self.count

    def _set_count(self):
        self.count = 0
        return ''


report_sxw.report_sxw('report.fuel.fuel_exchange_status.report', 'fuel_exchange_status_archive',
                      'addons/fuel_niss/report/fuel_exchange_status_report.mako', parser=fuel_exchange_status_report, header=False)
