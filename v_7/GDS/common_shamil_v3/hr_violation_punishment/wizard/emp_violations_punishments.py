
from osv import fields, osv
import time

class emp_violations_punishments(osv.osv_memory):

    months = [
           ('01', '01'),
           ('02', '02'),
	   ('03', '03'),
	   ('04', '04'),
           ('05', '05'),
           ('06', '06'),
           ('07', '07'),
           ('08', '08'),
           ('09', '09'),
           ('10', '10'),
           ('11', '11'),
           ('12', '12'),
	    ]
  
    _name = "emp.violations.punishments"
    _description = 'information about employees violations in spesific month'
    _columns = {
	         'year':fields.integer('Year',required=True),
		 'month':fields.selection(months,"Month",required=True), 
   		 }

    _defaults = {
        'year': int(time.strftime('%Y')),
		}
 
   
  
    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.employee.violation',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'emp.violations.punishments',
            'datas': datas,
            }

emp_violations_punishments()



    
    


