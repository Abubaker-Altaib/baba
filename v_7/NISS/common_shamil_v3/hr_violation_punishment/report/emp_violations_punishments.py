import time
from report import report_sxw
import calendar
import datetime
import pooler
from openerp.osv import fields, osv, orm

class emp_violations_punishments(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        super(emp_violations_punishments, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'all_len': self._get_all_len,
            'get_count': self._get_count,
            'lines': self._get_lines,
        })
    
    def _get_count(self):
        self.count = self.count + 1
        return self.count

    def _get_lines(self):
        return self.all_data
   
    def _get_all_len(self,data):


        employee_id = data['form']['employee_id']
        department_id = data['form']['department_id']

        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']

        company_id = data['form']['company_id']

        year = data['form']['year']

        month = data['form']['month']

        clouses = False

        if year:
            clouses = "to_char(m.violation_date,'YYYY')='"+str(year)+"'"

        if month:
            if clouses:
                clouses += " and to_char(m.violation_date,'mm')='"+str(month)+"'"
            if not clouses:
                clouses = " to_char(m.violation_date,'mm')='"+str(month)+"'"

        if employee_id:
            employee_id = employee_id[0]
            if clouses:
                clouses += "and m.employee_id="+str(employee_id)
            if not clouses:
                clouses += " m.employee_id="+str(employee_id)
            

        if department_id:
            department_id = department_id[0]
            if clouses:
                clouses += " and emp.department_id="+str(department_id)
            if not clouses:
                clouses = " emp.department_id="+str(department_id)

        
        if company_id:
            company_id = company_id[0]
            if clouses:
                clouses += " and m.company_id="+str(company_id)
            if not clouses:
                clouses += " m.company_id="+str(company_id)

        
        if job_id:
            job_id = job_id[0]
            if clouses:
                clouses += " and emp.job_id="+str(job_id)
            if not clouses:
                clouses = " emp.job_id="+str(job_id)

        
        if degree_id:
            degree_id = degree_id[0]
            if clouses:
                clouses += " and emp.degree_id="+str(degree_id)
            if not clouses:
                clouses = " emp.degree_id="+str(degree_id)
            
        readable_emp_ids = self.pool.get('hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in"+str(readable_emp_ids)
            if not clouses:
                clouses = "emp.in in"+str(readable_emp_ids) 



        query = """select r.name as employee,m.violation_date AS date,
                            m.violation_descr AS violation,m.decision_descr AS punishment,
                            m.penalty_amount AS penalty ,
                            emp.otherid,emp.name_related,
                            deg.name as deg_name,job.name as job_name, dep.name as dep_name 

                            FROM hr_employee_violation AS m 
                            left join hr_employee emp on (m.employee_id=emp.id) 
                            left join resource_resource AS r on (emp.resource_id=r.id)
                            left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                            left join hr_job job on(job.id = emp.job_id)
                            left join hr_department dep on(dep.id = emp.department_id)  """
        
        if clouses:
            query += "where "+clouses

        query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"
        self.cr.execute(query)
        res = self.cr.dictfetchall()

        if not res:
           raise osv.except_osv(('Sorry'), ('Their is No Violation in this Month'))
        self.all_data = res

        return len(res)



    
report_sxw.report_sxw('report.emp.violations.punishments','hr.employee.violation',
'hr_violation_punishment/report/emp_violations_punishments.mako',parser=emp_violations_punishments)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
