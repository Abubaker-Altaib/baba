import time
from report import report_sxw
import calendar
import datetime
import pooler

class seniority_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(seniority_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line': self._get_data,
            'lines': self._get_lines,
            'all_lines': self._get_all_lines,
               })
        
        


#------------------------------- line----------------------------------   
    def _get_data(self,data):
        res=[]
        degree_obj=self.pool.get('hr.salary.degree')
        dept_obj=self.pool.get('hr.department')
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",data
        if data['type'] == 'degree':
            for degree in degree_obj.browse(self.cr, self.uid, data['degrees']):
                res.append(degree)
        if data['type'] == 'department':
            for dept in dept_obj.browse(self.cr, self.uid, data['departments']):
                res.append(dept)
        print">>>>>>>>>>>>>>>>>>>>>>>>>res",res
        return res
#------------------------------- lines----------------------------------   
    def _get_lines(self,data,line):
        res=[]
        seniority=self.pool.get('hr.employee.seniority')
        print"LLLLLLLLLLLLLLLLLLLLLLLLL",line
        if data['type'] == 'degree':
            degrees=seniority.search(self.cr , self.uid , [('degree_id' , '=' , line)])
            for degree in seniority.browse(self.cr, self.uid, degrees):
                res.append(degree)
        elif data['type'] == 'department':
            depts=seniority.search(self.cr , self.uid , [('department_id' , '=' , line)])
            for dept in seniority.browse(self.cr, self.uid, depts):
                res.append(dept)
        else:
            emps=seniority.search(self.cr , self.uid ,[])
            for emp in seniority.browse(self.cr, self.uid, emps):
                res.append(emp)
        print">>>>>>>>>>>>>>>>>>>.res",res
        return res

#-------------------------------all lines----------------------------------   
    def _get_all_lines(self,data):
        res=[]
        seniority=self.pool.get('hr.employee.seniority')
        emps=seniority.search(self.cr , self.uid ,[])
        for emp in seniority.browse(self.cr, self.uid, emps):
            res.append(emp)
        return res



report_sxw.report_sxw('report.seniority.report', 'hr.employee.seniority', 'addons/hr_custom_military/report/seniority_report.rml' ,parser=seniority_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
