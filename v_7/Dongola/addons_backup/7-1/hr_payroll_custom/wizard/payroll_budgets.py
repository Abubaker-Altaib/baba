from osv import fields, osv
import time

class payroll_budget(osv.osv_memory):
    _name = "payroll.budget"

    _columns = {
            'year':fields.integer('Year', required=True),
            'margin':fields.integer('Margin', required=False),  
                }
    _defaults = {
        'year': int(time.strftime('%Y')),
        'margin' :1
		}
    def margin_default(self, cr, uid, data, context):
       return {'margin':1}

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr2.payroll',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'payroll.budgets',
            'datas': datas,
            }

payroll_budget()
