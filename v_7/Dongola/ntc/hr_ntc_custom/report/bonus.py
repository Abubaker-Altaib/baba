# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw

class bonus_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bonus_report, self).__init__(cr, uid, name, context)
        self.total = {'total_allowance':0.0, 'total_deduction':0.0,'total_loans':0.0,'net':0.0,
                      'allowances_tax':0.0,'tax':0.0,'zakat':0.0,'imprint':0.0}
        self.name = {'name':''}
        self.localcontext.update({
            'time': time,
            'total':self.get_amount,
            'name': self.get_manager,
        })
    def get_amount(self,record):
        result = {}
        bouns_obj = self.pool.get('hr.salary.bonuses')
        degree_id = record.employee_id.degree_id.id
        bouns_id = bouns_obj.search(self.cr,self.uid,[('name','=',record.previous),('degree_id','=',degree_id)])
        amount1 = amount2 = 0
        if bouns_id:
            amount1 += bouns_obj.browse(self.cr,self.uid,bouns_id[0]).basic_salary
        result[0] = amount1
        amount2 += record.reference.basic_salary
        result[1] = amount2
        
        return result

    def get_manager(self,record):
        data_obj = self.pool.get('ir.model.data')
        result = []
        group_id = data_obj.get_object_reference(self.cr, self.uid,'base', 'group_hr_manager')
        self.cr.execute('SELECT g.uid as user_id ' \
                    'FROM public.res_groups_users_rel g ' \
                    'WHERE g.gid = %s', (group_id[1],) )
        user_group_ids = self.cr.dictfetchall()
        user_ids = [x['user_id'] for x in user_group_ids]
        if user_ids:
                user_ids.append(0)
                self.cr.execute('SELECT hr_employee.name_related as name, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                    'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                    'WHERE hr_employee.resource_id = resource_resource.id '\
                    'AND resource_resource.user_id = res_users.id '\
                    'AND res_users.partner_id = res_partner.id '\
                    'AND res_users.id in %s', (tuple(user_ids),) )
                res = self.cr.dictfetchall()
                result.append(res[0]['name'])
        
        return result
    

   
report_sxw.report_sxw('report.employee.bonus', 'hr.process.archive', 'addons/hr_ntc_custom/report/bonus.rml' ,parser=bonus_report, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



