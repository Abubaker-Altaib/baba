# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': 'Import Xls Bank Statement',
    'category': 'Accounting & Finance',
    'version': 'Maknoun',
    'description': '''
Module to import Xls bank statements.
======================================

This module allows you to import Xls Files in Odoo.
''',
    'author': "NCTR",
    'website': "http://www.nctr.sd",
    'depends': ['account_bank_statement_import', 'base_import'],
    'data': [
        'wizard/account_bank_statement_import_xls_views.xml',
        'views/account_bank_statement_import_templates.xml',
    ],
    'installable': True,
    'auto_install': True,
}
