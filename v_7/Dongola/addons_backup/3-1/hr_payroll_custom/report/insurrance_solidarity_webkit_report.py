# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################
import datetime
import time

from openerp.osv import fields, osv, orm
from openerp.report.interface import report_rml
from openerp.report.interface import toxml
import mx
import time
from openerp.report import report_sxw
from openerp.tools import ustr
from openerp.tools.translate import _
from openerp.tools import to_xml

class insurrance_solidarity_webkit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(insurrance_solidarity_webkit, self).__init__(cr, uid, name, context)
        self.total={'d_total':0,'c_total':0,'counter':0,}      
        self.localcontext.update({       
            'main':self.get_main_work,
            'total':self.get_total,
        })

    def get_main_work(self,data):
        top_res=[]
        d_total=c_total=counter=0
        data['scale_ids'].append(0) 
        cluse=" ma.scale_id in "+str(tuple(data['scale_ids']))+" AND ma.year='"+str(data['year'])+"' AND ma.month='"+str(data['month'])+"' AND ada.allow_deduct_id= "+str(data['soli_insu_id'][0])
        if data['company_ids']:
            data['company_ids'].append(0)
            cluse += " AND ma.company_id in "+str(tuple(data['company_ids'])) 
        if data['dept_ids']:
            data['dept_ids'].append(0)
            cluse += " AND ma.department_id in "+str(tuple(data['dept_ids']))
        self.cr.execute('''
SELECT 
  SUM(ada.amount) AS amount, 
  COUNT(ada.id) AS count, 
  hd.name 
FROM 
  hr_allowance_deduction_archive ada
  LEFT JOIN hr_payroll_main_archive ma ON (ma.id = ada.main_arch_id)
  LEFT JOIN hr_department hd ON (hd.id = ma.department_id)
WHERE 
   ''' +cluse+''' GROUP BY hd.name ''') 

        result = self.cr.dictfetchall()
        if result :
            no=0
            types=self.pool.get('hr.allowance.deduction').browse(self.cr,self.uid,[data['soli_insu_id'][0]])[0]
            for rec in result:
                no+=1
                c_share=rec['amount']* data['factor']
                if types.type=='complex':
                    c_share=(rec['amount']*100) * data['factor']/100
                    #c_share=(rec['amount']*100/deduct.amount) * data['factor']/100 need to b checked
                dic={
                          'd_share':round(rec['amount'],2),
                          'c_share':round(c_share,2),
                          'count':rec['count'],
                          'share':round(rec['amount']+c_share,2),
                          'dep':rec['name'],
                          'no':no,}
                d_total+=rec['amount']
                c_total+=c_share
                counter+=rec['count']
                top_res.append(dic) 
            self.total={'d_total':round(d_total,2),'c_total':round(c_total,2),'counter':counter,}           
            return top_res

    def get_total(self):
         return self.total
  

report_sxw.report_sxw('report.insurrance.solidarity.webkit', 'hr.payroll.main.archive', 'hr_payroll_custom/report/insurrance_solidarity_webkit_report.mako', parser=insurrance_solidarity_webkit, header="False")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
