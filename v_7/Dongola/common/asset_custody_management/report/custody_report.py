import time
from report import report_sxw

class custody_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(custody_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line' : self._getdata,
            'line2' : self._getdepartment_name,
        })
    
    def _getdepartment_name(self,data):
        department_id = data['form']['department_id']

        res = {}
        if department_id :

           self.cr.execute("""
                        select name as dept_name from hr_department where id=%s""",(department_id[0],))
        res = self.cr.dictfetchall()

        return res
                              
    def _getdata(self,data):
        conditions = "" 
        report_type = data['form']['report_type']
        category_company_id = data['form']['category_company_id']
        category_id = data['form']['category_id']
        version_id = data['form']['version_id']
        report_type = data['form']['report_type']
        custody_type = data['form']['custody_type']
        department_id = data['form']['department_id']
        with_childern = data['form']['with_childern']
        if category_company_id :
           conditions = conditions + " and c.category_company_id_id =(%s)"%category_company_id[0]
        if category_id :
           conditions = conditions + " and c.category_id =(%s)"%category_id[0]
        if version_id :
           conditions = conditions + " and c.version_id =(%s)"%version_id[0]

        if custody_type == 'in_stock' : 
           if report_type == 'sum' :

		   self.cr.execute("""
		       select                        
                              distinct comp.name as company_name,
                              count (c.version_id) as version_count,
                              cat.name as category_name,
                              vers.name as version_name



		                    from custody_custody c
		                        
		                         
		                        
                                       left join custody_company comp on (comp.id = c.category_company_id)
		                       left join custody_category cat on (cat.id = c.category_id )  
                                       left join custody_category_models vers on ( c.version_id = vers.id )
		                       where c.state in ('released' , 'new')
		         
	 
		     """ + conditions + " group by comp.name,vers.name,cat.name  order by comp.name,cat.name " )
           else :
                     self.cr.execute("""
		       select                        
                              distinct c.serial as serial,
                              comp.name as company_name,
                              cat.name as category_name,
                              vers.name as version_name



		                    from custody_custody c
		                        
		                         
		                        
                                       left join custody_company comp on (comp.id = c.category_company_id)
		                       left join custody_category cat on (cat.id = c.category_id )  
                                       left join custody_category_models vers on ( c.version_id = vers.id)

                                       
		                       where c.state in ('released' , 'new')
		         
	 
		     """ + conditions + "order by comp.name,cat.name " )

        else:
           if report_type == 'sum' : 
              self.cr.execute("""
		       select                        
                              distinct comp.name as company_name,
                              count (c.version_id) as version_count,
                              cat.name as category_name,
                              vers.name as version_name



		                    from custody_custody c
		                        
		                         
		                        
                                       left join custody_company comp on (comp.id = c.category_company_id)
		                       left join custody_category cat on (cat.id = c.category_id )  
                                       left join custody_category_models vers on ( c.version_id = vers.id)
		                       where c.state in ('assigned')
		         
	 
		     """ + conditions + " group by comp.name,vers.name,cat.name order by comp.name,cat.name" )
        


           else :
                    self.cr.execute("""
		       select                        
                              distinct c.serial as serial,
                              comp.name as company_name,
                              dept.name as department,
                              emp.name_related as employee,
                              cat.name as category_name,
                              vers.name as version_name



		                    from custody_custody c
		                        
		                         
		                        
                                       left join custody_company comp on (comp.id = c.category_company_id)
		                       left join custody_category cat on (cat.id = c.category_id )  
                                       left join custody_category_models vers on ( c.version_id = vers.id)
                                       left join hr_department dept on (dept.id = c.department_id)
                                       left join hr_employee emp on (c.current_employee = emp.id)
                                       
		                       where c.state in ('assigned')
		         
	 
		     """ + conditions + "  order by comp.name,cat.name " )

        res = self.cr.dictfetchall()

        return res
report_sxw.report_sxw('report.custody_report1', 'custody.custody', 'addons/asset_custody_management/report/custody_report.rml' ,parser=custody_report ,header=False )

