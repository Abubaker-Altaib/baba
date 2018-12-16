# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "base custom Niss",
    "author" : "NCTR",
    "category": "Dependency",
    "description": """
    Adding the following Features:
    1. Add HQ boolean in company.

    """,
    "version" : "wafi-1.0",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    'data': [
            'base.xml',

        ],
    "depends" : ["base_setup","base_custom"],
    'test': [],
    'installable': True,
    'active': False,

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
