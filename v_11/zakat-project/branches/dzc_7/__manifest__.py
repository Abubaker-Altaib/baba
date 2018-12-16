# -*- coding: utf-8 -*-
{
    'name': "dzc_7",

    'summary': """Fe Sabeel Allah Channel""",

    'author': "NCTR",

    'website': "http://www.nctr.sd",

    'category': 'Uncategorized',

    'version': 'dzc_7 V0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','dzc_1','stock'],

    # always loaded
    'data': [
    'security/dzc_7_security.xml',
    'security/ir.model.access.csv',
    'views/dzc_7_config_view.xml',
    'views/maytr_family_support.xml',
    'views/dzc_7_view.xml',
    'sequence/dzc_7_seq.xml',
    ],
    'application': True,
    'installable': True,

}
