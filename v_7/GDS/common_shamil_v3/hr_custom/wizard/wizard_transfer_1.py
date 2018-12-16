

import wizard
import osv
import pooler


_transfer_form = '''<?xml version="1.0"?>
<form string=" Transfer Report">
    
    <field name="emp_id" colspan="4"/>
    
   <field name="company_id" colspan="4"/>
   
</form>'''

_transfer_fields = {
    'company_id': {'string':'Company', 'type':'many2one', 'relation': 'res.company', 'required':True},
    'emp_id': {'string':'Employee(s)', 'type':'many2many', 'relation': 'hr.employee', 'required':True,'domain':"[('service_terminated','=',False)]"},
   
}



class wiz_transfer_report_1(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_transfer_form, 'fields':_transfer_fields, 'state':[('end','Cancel'),('close','Report')]}
        },
        'close': {
            'actions': [],
            'result': {'type': 'print','report':'transfer.report.1', 'state':'end'}
        }
    }
wiz_transfer_report_1('transfer.report.1')
 
