# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "Base Custom",
    "author" : "NCTR",
    "category": "Dependency",
    "description": """
    Adding the following Features:
    1. Convert the amount from numeric to text in arabic lang.
    2. Modify compute methond in res.currency model to get the rate from res.currency.rate according to date.
    """,
    "version" : "wafi-1.0",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    'data': [
        "base.xml",
        "res_config_view.xml",
        ],
    "depends" : ["base","base_setup",],
    'test': [],
    'installable': True,
    'active': False,
    'js' : [
        "static/src/js/dates.js",
    ],
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
