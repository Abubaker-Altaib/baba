# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name" : "base custom extra",
    "author" : "NCTR",
    "category": "Dependency",
    "description": """
    Adding the following Features:
    1. skip workflow and security and csv files in particular module when upgrade it.

    """,
    "version" : "wafi-1.0",
    'website': 'http://www.nctr.sd',
    'init_xml': [],
    'data': [

        ],
    "depends" : ["base_setup","base_custom"],
    'test': [],
    'installable': True,
    'active': False,

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
