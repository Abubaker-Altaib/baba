import time
from report import report_sxw
import calendar
import datetime
import pooler
import math

class additional_report_bank(report_sxw.rml_parse):
    globals()['total_net']=0.0
    globals()['no_data'] = False


    def __init__(self, cr, uid, name, context):
        super(additional_report_bank, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getShop,
            'line1':self._total,
            'line9':self._get_bank,
            'user':self._get_user,
            
        })
        globals()['total_net']=0.0
        globals()['no_data'] = False
    

    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name

    def _get_bank(self):
        bank_name_ids = self.pool.get('res.bank').search(self.cr,self.uid,[])
        bank_name1 = self.pool.get('res.bank').browse(self.cr,self.uid,bank_name_ids)
        bank_name_list = []
        bank_ids_list = []
        bank_name_list += [{'bank_name':x.name} for x in bank_name1]
        bank_id = bank_name_ids
        
        bank_ids = []
        for x in bank_name1:
            bank_ids.append({'bank_id':x.id,'bank_name':x.name})
        return bank_ids


    def _getShop(self,data,bank_id):
        #salary_scale_obj = self.pool.get('hr.salary.scale')
        #allowance_obj = self.pool.get('hr.allowance.deduction')
        globals()['total_net']=0.0
        res_data = {}
        top_result = []
        top_result2 = []
        globals()['total_net']=0.0
        globals()['no_data'] = False
        bank_id_list = self.pool.get('res.partner.bank').search(self.cr,self.uid,[('bank','=',bank_id)])
        
         
        #-------------------------------------------------------------------------------
            

            #if salary_sheet:
        self.cr.execute("SELECT hr_employee.id,rpb.acc_number AS employee_code, "\
                    "resource_resource.name AS employee_name,"\
                    "COALESCE(hr_additional_allowance_line.amounts_value,0) AS total "\
                    "FROM hr_additional_allowance_line "\
                    "left join hr_additional_allowance a on a.id = hr_additional_allowance_line.additional_allowance_id "\
                    "left join hr_employee ON (hr_additional_allowance_line.employee_id = hr_employee.id) "\
                    "LEFT JOIN hr_salary_degree deg on (deg.id= hr_employee.degree_id) "\
                    "left join res_partner_bank rpb ON (hr_employee.bank_account_id = rpb.id) "\
                    "join resource_resource ON (hr_employee.resource_id = resource_resource.id) "\
                    "WHERE a.id=%s "\
                    "and hr_employee.bank_account_id in %s " \
                    "order by deg.sequence, hr_employee.name_related" ,
                    (data.id,tuple(bank_id_list),))  

        res = self.cr.dictfetchall()
        i=0
        while (len(res) > i):
                        res_data = { 'no': i+1,
                                'employee_code': res[i]['employee_code'], #employee_code
                                'employee_name': res[i]['employee_name'],
                                'total': res[i]['total'],
                            }
                        globals()['total_net'] += res[i]['total']
                        top_result.append(res_data)
                        i+=1
        if top_result:
            top_result2.append(top_result)
        return top_result2

    def _total(self,data,bank_id):
        return globals()['total_net']

        
report_sxw.report_sxw('report.additional_bank', 'hr.additional.allowance', 'addons/hr_ntc_custom/report/additional_report_bank.rml' ,parser=additional_report_bank,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


