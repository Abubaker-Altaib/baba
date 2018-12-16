# -*- coding: utf-8 -*-
{
    'name': "dzc_6",

    'summary': """Garmeen Channel""",

    'author': "NCTR",

    'website': "http://www.nctr.sd",

    'category': 'Uncategorized',

    'version': 'dzc_6 V0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','dzc_1','stock'],

    # always loaded
    'data': [
    'views/dzc_6_config_view.xml',
    'views/garmeen_planning_view.xml',
    'views/garm_request.xml',
    'views/garmeen_committe.xml',
    'views/release_prisoners.xml',
    'sequence/dzc_6_seq.xml',
    'security/dzc_6_security.xml',
    'security/ir.model.access.csv',
    ],
    'application': True,
    'installable': True,

}
