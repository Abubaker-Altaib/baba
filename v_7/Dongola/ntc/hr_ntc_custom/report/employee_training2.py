# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import datetime
import mx
from openerp.report import report_sxw


class employee_form2(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(employee_form2, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'user':self._get_user,
            'line':self._get_data
           })
        self.year = int(time.strftime('%Y'))

    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name


    def _get_data(self, data):
        row=[]
        col=[]
        qual= []
        ls = []
        ls1 = []
        ls2 = []
        num = 0
        scale_object = self.pool.get('hr.salary.scale')
        qual_object = self.pool.get('hr.qualification')
        qual_emp_object = self.pool.get('hr.employee.qualification')
        emp_object = self.pool.get('hr.employee')
        payroll_ids = data['payroll_ids']
        payroll_ids = not payroll_ids and scale_object.search(self.cr,self.uid,[]) or payroll_ids
        
        res=[]
        for x in data['qual_ids']:
            ls1 = []
            ls = []
            z = qual_object.browse(self.cr,self.uid,x)
            qual_idss = qual_object.search(self.cr,self.uid,[('parent_id','=',x)])
            ls2.append(qual_idss)
            for c in qual_object.browse(self.cr,self.uid,qual_idss):
                ls.append(c.name)
            ls1.append(z.name)
            ls1.append(ls)
            col.append(ls1)
        for x in [u'العدد الموجود حاليا',u'الدرجة الوظيفية',u'الرقم']:
            col.append(x)
        row.append(col)

        self.cr.execute(" select distinct d.name as degree_name, d.id as degree_id " 
        "from hr_salary_degree d "\
        "where d.payroll_id in %s",(tuple(payroll_ids),))

        res=self.cr.dictfetchall()
        for x in res:
            col = []
            num += 1
            list_emps = emp_object.search(self.cr,self.uid,[('degree_id','=',x['degree_id']),('state','!=','refuse')])
            count = len(list_emps)
            for a in ls2:
                l1 =[]
                v1 = 0
                for a1 in a:

                    v = qual_emp_object.search(self.cr,self.uid,[('employee_id','in',list_emps),('emp_qual_id','=',a1)])
                    v1 = v and len(v) or 0
                    l1.append(v1)
                col.append(['#',l1])
            col.append(count)
            col.append(x['degree_name'])
            col.append(num)
            row.append(col)


            
        return row

        

report_sxw.report_sxw('report.training.employee_two', 'hr.employee', 'addons/hr_ntc_custom/report/employee_training2.mako' ,parser=employee_form2 ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
