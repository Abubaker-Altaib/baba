from osv import fields, osv
import time

class payroll_listing(osv.osv_memory):
    _name = "payroll.listing"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months

    _columns = {
        'company_id': fields.many2many('res.company','hr_listing_company_rel','listing_id','company_id','Company',required=True),
        'payroll_ids': fields.many2many('hr.salary.scale', 'hr_listing_payroll_rel','listing','pay_id','Salary Scale',required=True),
	    'month': fields.selection(_get_months,'Month', required=True),
	    'year': fields.integer('year',required=True ),
		}
    def _get_companies(self, cr, uid, context=None): 
   
        return [self.pool.get('res.users').browse(cr,uid,uid).company_id.id]

    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
        'company_id': _get_companies,
		}


    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.payroll.main.archive',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'payroll.report',
            'datas': datas,
            }

payroll_listing()  		 
