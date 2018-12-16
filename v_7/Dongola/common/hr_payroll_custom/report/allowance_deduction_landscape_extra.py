# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import copy
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp.tools.safe_eval import safe_eval

class allowance_deduction_extra_landscape(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(allowance_deduction_extra_landscape, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process':self._process,  
            'user':self._get_user,  
        })

    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name

    def _process(self,data):
        row = []
        col = []
        sums = []
        loans= {}
        payroll_ids = data['payroll_ids'] and data['payroll_ids'] or self.pool.get('hr.salary.scale').search(self.cr,self.uid, [])
        dept_ids = data['dept_ids'] and data['dept_ids'] or self.pool.get('hr.department').search(self.cr,self.uid, [])
        degree_ids = data['degree_ids'] and data['degree_ids'] or self.pool.get('hr.salary.degree').search(self.cr,self.uid, [])
        domain = [('pay_sheet', '=', data['pay_sheet']), ('in_salary_sheet', '=', data['in_salary_sheet']),('name_type', '=', data['type'])]
        if data['allow_deduct_ids'] : domain.append(('id', 'in', data['allow_deduct_ids']))
        allw_deduct_ids = self.pool.get('hr.allowance.deduction').search(self.cr,self.uid, domain,limit=16)
        allow_deduct_ids = self.pool.get('hr.allowance.deduction').browse(self.cr,self.uid,allw_deduct_ids)
        emp_domain =  [('payroll_id', 'in', payroll_ids), ('department_id', 'in', dept_ids),('degree_id', 'in', degree_ids)]
        if data['employee_ids'] : emp_domain.append(('id', 'in', data['employee_ids']))
        employee_ids = self.pool.get('hr.employee').search(self.cr,self.uid, emp_domain)
        self.cr.execute(
            '''SELECT employee_id as emp, id as id FROM hr_payroll_main_archive WHERE month =%s and year =%s 
               and employee_id IN %s ''',(data['month'],data['year'],tuple(employee_ids))) 
        result = self.cr.dictfetchall()
        empl_ids = [ rec['emp'] for rec in result if result]
        main_arc_ids = [ rec['id'] for rec in result if result]
        emp_ids = self.pool.get('hr.employee').search(self.cr,self.uid, [('id', 'in', empl_ids)] ,order='degree_id, department_id desc')
        emp_recs = self.pool.get('hr.employee').browse(self.cr,self.uid, emp_ids)
        def get_loan( payment_type, main_arc_ids):
            self.cr.execute(
                '''SELECT sum(loan_arc.loan_amount) AS amount,
                loan_arc.employee_id AS employee
                FROM hr_loan_archive loan_arc
                JOIN hr_payroll_main_archive main_arc ON (loan_arc.main_arch_id=main_arc.id)
                WHERE loan_arc.payment_type IN %s and 
                loan_arc.main_arch_id IN %s  GROUP BY loan_arc.employee_id''',( tuple(payment_type), tuple(main_arc_ids))) 
            return self.cr.dictfetchall() 
        if data['display']=='detail': 
            col.append(u'الإجمالي') 
            if data['pay_sheet']== 'first' and data['type']=='allow': 
                name=u'المبلغ الاساسي'
                flag = 'fa'
            elif data['pay_sheet']== 'second' and data['type']=='allow': 
                name=u'ا.ح.ف.ا'  
                flag = 'sa'
            elif data['pay_sheet']== 'first' and data['type']=='deduct': 
                name=u'الضريبة'
                flag = 'fd'
            elif data['pay_sheet']== 'second' and data['type']=='deduct':
                name = u'ا.خ.ف.ا'
                flag = 'sd'
                payment_type = data['in_salary_sheet'] and ['salary','both'] or ['addendum','both']
                loans = dict([(r['employee'], r['amount']) for r in get_loan(payment_type, main_arc_ids)])
                col.append(u'سلفيات')
            self.cr.execute(
                '''SELECT adarc.amount AS amount,
                main_arc.employee_id AS employee, 
                adarc.allow_deduct_id AS allow_deduct
                FROM hr_allowance_deduction_archive adarc
                JOIN hr_payroll_main_archive main_arc ON (adarc.main_arch_id=main_arc.id)
                WHERE main_arc.month =%s and main_arc.year =%s 
                and main_arc.employee_id IN %s 
                and adarc.allow_deduct_id IN %s ''',(data['month'],data['year'],tuple(emp_ids),tuple(allw_deduct_ids))) 
            res = self.cr.dictfetchall()
            amounts = dict([((r['employee'],r['allow_deduct']), r['amount']) for r in res])
            for allow_deduct in allow_deduct_ids:
                col.append(allow_deduct.name)
                sums.append(0)
            col.append(name)
            f_column = self.get_first_col( main_arc_ids, flag)
        else:
            col.append(u'الصافي')
            col.append(u'الخصومات')
            col.append(u'الإستحقاقات')
        col.append(u'الموظف ')
        col.append(u'#')
        col.reverse()
        row.append(col)
        count = 0
        for emp in emp_recs:
            col=[]
            count+=1
            if data['display']=='detail':  
                col.append(0)
                if loans :  
                    amount= loans.get((emp.id), 0.0)
                    col.append(amount)
                for allow_deduct in allow_deduct_ids:
                    amount= amounts.get((emp.id,allow_deduct.id), 0.0)
                    col.append(amount)
                first_col = f_column.get((emp.id), 0.0)
                col.append(first_col)
                col[0]=sum(col)
            else: 
               main_id = self.pool.get('hr.payroll.main.archive').search(self.cr,self.uid, [('id', 'in', main_arc_ids),
                                                                                            ('employee_id', '=', emp.id)])
               main_rec = self.pool.get('hr.payroll.main.archive').browse(self.cr,self.uid, main_id[0])
               col.append(main_rec.total_allowance - main_rec.total_deduction)  
               col.append(main_rec.total_deduction)              
               col.append(main_rec.total_allowance)              
            col.append(emp.name)
            col.append(count)
            col.reverse()
            row.append(col)
        col = []
        col.append(u'#')
        col.append(u'الإجمالي ')
        for indx, rw in enumerate(copy.copy(row)[1:]):
            for inx, cl in enumerate(rw[2:]):
               if indx==0:col.append(cl)
               else:col[inx+2]+=cl
        row.append(col)
        return row

    def get_first_col(self, main_arc_ids, flag):
        def get_first_sheet(field, main_arc_ids):
            self.cr.execute(
                ''' SELECT '''+ field +''' AS basic_salary, employee_id AS employee FROM hr_payroll_main_archive  
                   WHERE id IN %s ''',(tuple(main_arc_ids),)) 
            res = self.cr.dictfetchall()
            return dict([(r['employee'], r['basic_salary']) for r in res])
        def get_second_sheet( ad_type, field, main_arc_ids):
            self.cr.execute(
               '''SELECT sum(adarc.amount) + main_arc.''' + field +''' AS amount,  
                    main_arc.employee_id AS employee
                    FROM hr_payroll_main_archive main_arc 
                    JOIN hr_allowance_deduction_archive adarc ON (adarc.main_arch_id = main_arc.id)
                    JOIN hr_allowance_deduction sett ON (adarc.allow_deduct_id = sett.id)
                    WHERE sett.pay_sheet ='first' and sett.name_type = %s and
                    main_arc.id IN %s GROUP BY employee_id, ''' + field +''' ''',(ad_type,tuple(main_arc_ids))) 
            res = self.cr.dictfetchall()
            return dict([(r['employee'], r['amount']) for r in res])
        if flag=='fa':
            return get_first_sheet('basic_salary', main_arc_ids)
        elif flag=='sa':
            return get_second_sheet('allow','basic_salary', main_arc_ids)
        elif flag=='fd':
            return get_first_sheet('tax', main_arc_ids)
        elif flag=='sd':
            return get_second_sheet('deduct', 'tax', main_arc_ids)

report_sxw.report_sxw('report.allowance.deduction.extra.landscape', 'hr.allowance.deduction.archive', 'hr_payroll_custom/report/allowance_deduction_landscape_extra.rml' ,parser=allowance_deduction_extra_landscape,header="internal landscape")
report_sxw.report_sxw('report.allowance.deduction.extra', 'hr.allowance.deduction.archive', 'hr_payroll_custom/report/allowance_deduction_extra.rml' ,parser=allowance_deduction_extra_landscape,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
