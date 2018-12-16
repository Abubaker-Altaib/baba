# -*- coding: utf-8 -*-
{
    'name': "dzc_2",

    'summary': """Almsakeen ‫‪channel""",

    'author': "NCTR",

    'website': "http://www.nctr.sd",

    'category': 'Uncategorized',

    'version': 'dzc_2 V0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'zakat_base', 'dzc_1'],

    # always loaded
    'data': [
        'security/dzc_2_security.xml',
        'security/ir.model.access.csv',
        'sequence/dzc2_seq.xml',
        'views/states_support_view.xml',
        'views/dzc_2_config_view.xml',
        'views/project_planing_view.xml',
        'views/project_request_view.xml',
        'wizard/state_per_rep_view.xml',
        'report/report_action.xml',
        'report/state_per_report_template.xml',

    ],
    'application': True,
    'installable': True,

}
