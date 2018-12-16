

import time
import wizard
import datetime

form1 = '''<?xml version="1.0"?>
<form string="Select Company">
            
            <field name="company_id"/>
            
</form>'''

field1 = {
    
    'company_id': {'string':'Select Company', 'type':'many2one','relation':'res.company','required':'True'},
    
}

class wiz_emp_delegation(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':form1, 'fields':field1, 'state':[('end','Cancel'),('close','Report')]}
        },
        'close': {
            'actions': [],
            'result': {'type': 'print','report':'emp1.delegation', 'state':'end'}
        }
    }
wiz_emp_delegation('employee.delegation')
 
