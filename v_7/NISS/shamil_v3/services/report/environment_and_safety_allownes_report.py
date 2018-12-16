#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from datetime import timedelta,date

# Fuel plan report  
# Report to print Fuel plan in a specific month and year.

class environment_and_safety_allownes_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(environment_and_safety_allownes_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,

        })

    def _getdata(self,data):
        month = data['form']['month']
        year = data['form']['year'] 
        partner_id = data['form']['partner_id']
        
        if partner_id :
            self.cr.execute('''
                select
                a.name as archive_name , 
                a.date as date , 
                
                a.partner_id as partner_id,
                c.name as contract,
                l.cost_of_rent as cost_of_rent,
                l.amount_untaxed as amount_untaxed,
                l.amount_tax as amount_tax,
                l.amount_total as amount_total,
                l.deduct_days as deduct_days,
                l.deduct_amount as deduct_amount,
                l.percentage_rating as percentage_rating
                from services_contracts_archive a
                left join services_contracts_allowances_lines l on (a.id=l.env_allow_id_before_rate)
                left join environment_and_safety c on (l.contract_id = c.id)                
                left join res_partner r on (a.partner_id=r.id)
                where  a.month = %s and a.year=%s and a.partner_id= %s and a.state = 'done'
            order by a.name ''',(str(month),str(year),data['form']['partner_id'][0])) 
        if not partner_id:
            self.cr.execute('''
                select
                a.name as archive_name , 
                a.date as date , 
                c.name as contract,
                l.cost_of_rent as cost_of_rent,
                l.amount_untaxed as amount_untaxed,
                l.amount_tax as amount_tax,
                l.amount_total as amount_total,
                l.deduct_days as deduct_days,
                l.deduct_amount as deduct_amount,
                l.percentage_rating as percentage_rating
                from services_contracts_archive a
                left join services_contracts_allowances_lines l on (a.id=l.env_allow_id_before_rate)
                left join environment_and_safety c on (l.contract_id = c.id)                
                where  a.month = %s and a.year=%s and a.state = 'done'
            order by a.name ''',(str(month),str(year))) 
            
        res = self.cr.dictfetchall()            
        return res

report_sxw.report_sxw('report.environment.and.safety.allownes.report', 'services.contracts.archive', 'addons/services/report/environment_and_safety_allownes_report.rml' ,parser=environment_and_safety_allownes_report,header=False)