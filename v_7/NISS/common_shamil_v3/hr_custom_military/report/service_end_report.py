# -*- coding: utf-8 -*-

from report import report_sxw
import time
from datetime import datetime


class service_end_report(report_sxw.rml_parse):
    '''
    @return employee data in dictionary
    '''

    def get_record(self):
        res = []
        for i in self.pool.get('hr.employee').browse(self.cr, self.uid, self.context['active_ids']):
            res.append(i)
        return res

    def has_personal_custody(self, employee):
        self.cr.execute("""select employee_id from account_asset_asset where custody_type='personal' and state_rm='assigned' and employee_id = """ + str(employee.id))
        res_new = self.cr.dictfetchall()

        # self.cr.execute("""select employee_id from account_asset_asset where custody_type='personal' and state_rm='assigned' and employee_id = """ + str(employee.id))
        # res_old = self.cr.dictfetchall()

        if res_new:
            return True
        return False

    def has_un_processed_punish(self, employee):
        self.cr.execute("""select * from hr_employee_violation where state!='implement' and employee_id = """ + str(employee.id))
        res = self.cr.dictfetchall()
        if res:
            return True
        return False
    
    def has_vehicle(self, employee):
        self.cr.execute("""select * from fleet_vehicle where state='confirm' and employee_id = """ + str(employee.id))
        res = self.cr.dictfetchall()
        if res:
            return True
        return False
    
    def has_family(self, employee):
        self.cr.execute("""select * from hr_employee_family where state='approved' and employee_id = """ + str(employee.id))
        res = self.cr.dictfetchall()
        if res:
            return True
        return False
    
    def has_loans(self, employee):
        self.cr.execute("""select * from hr_employee_loan where state='paid' and employee_id = """ + str(employee.id))
        res = self.cr.dictfetchall()
        if res:
            return True
        return False

    def has_deduct(self, employee):
        self.cr.execute("""select * from hr_allowance_deduction_exception where end_date>='"""+str(time.strftime("%Y-%m-%d"))+"""' and employee_id = """ + str(employee.id))
        res = self.cr.dictfetchall()
        if res:
            return True
        return False

    def f_custody(self, employee):
        self.cr.execute("""select * from account_voucher_line line
        left join res_partner part on (line.res_partner_id=part.id)
        left join res_users us on (part.user_id = us.id) 
        left join resource_resource re on (re.user_id = us.id) 
        left join hr_employee emp on (emp.resource_id = re.id) 
        where line.custody=True and line.custody_state='not removed' and emp.id = """ + str(employee.id))
        res = self.cr.dictfetchall()
        if res:
            return True
        return False

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(service_end_report, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update(
            {'records': self.get_record, 'date': time.strftime("%Y-%m-%d"),
            'has_personal_custody': self.has_personal_custody,
            'has_un_processed_punish': self.has_un_processed_punish,
            'has_vehicle':self.has_vehicle,'has_family':self.has_family,
            'has_loans':self.has_loans,'has_deduct':self.has_deduct,
            'f_custody':self.f_custody})


report_sxw.report_sxw('report.employee_service_end_report', 'hr.employee',
                      'addons/hr_custom_military/report/service_end_report.mako', parser=service_end_report, header='internal landscape')
