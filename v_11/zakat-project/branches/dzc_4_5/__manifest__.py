# -*- coding: utf-8 -*-
{
    'name': "dzc_4_5",

    'summary': """Dawa channel""",

    'author': "NCTR",

    'website': "http://www.nctr.sd",

    'category': 'Uncategorized',

    'version': 'dzc_4_5 V0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','dzc_1','stock'],

    # always loaded
    'data': [
    'security/dzc_4_5_security.xml',
    'security/ir.model.access.csv',
    'sequence/dzc4_5_seq.xml',
    'views/dzc_4_5_config_view.xml',
    'views/dawa_activities_plan_view.xml',
    'views/dawa_activity_request.xml',
    'views/dzc_4_5_view.xml',
    'report/report_action.xml',
    'report/report_templet.xml',
    ],
    'application': True,
    'installable': True,

}
