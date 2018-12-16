
{
    'name': 'HR Granted Rights Module',
    'version': '1.0',
    'category': 'HR Holidays',
    'description': """This module For Granted the Rights From Employee has a approved holiday To Alternative Employee""",
    'author': 'ASH',
    'summary': 'Grant and Revoke Rights From Particular Employee',
    'depends': ['hr' , 'hr_holidays' , 'hr_mission'],
    'init_xml': [],
    'data': [
             'security/employee_group.xml',
             'security/ir.model.access.csv',
             'view/hr_granted_rights_view.xml',
             'data/rights_scheduler.xml',
             'sequence/grant_rights_order_sequence.xml',],
    'test': [],
    'demo': [],
    'installable': True,
    'active': False,
}
