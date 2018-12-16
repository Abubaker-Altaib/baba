# -*- coding: utf-8 -*-
{
    'name': "dzc_8",

    'summary': """iiban alsabil ‫‪channel""",

    'author': "NCTR",

    'website': "http://www.nctr.sd",

    'category': 'Uncategorized',

    'version': 'dzc_8 V0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'zakat_base', 'account_check_printing'],

    # always loaded
    'data': [
        'security/dzc_8_security.xml',
        'sequence/dzc8_seq.xml',
        'report/iban_alsabil_report_template.xml',
        'report/report_action.xml',
        'views/dzc_8_view.xml',
        'views/dzc_8_config_view.xml',

    ],
    'application': True,
    'installable': True,

}
