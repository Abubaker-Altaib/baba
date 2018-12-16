# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    'name': "dzc_1",
    'author': "NCTR",
    'website': "http://www.nctr.sd",
    'summary': """Al-Faqir Channel""",

    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'zakat_base', 'stock'],

    # always loaded
    'data': [
        'security/dzc_1_security.xml',
        'security/ir.model.access.csv',
        'sequence/dzc1_seq.xml',

        'views/dzc1_view.xml',
                'views/health_insurance_planning_view.xml',

        'views/dzc_1_config_view.xml',


        'views/federal_treatment_view.xml',
        'views/orgnization_support_order.xml',
        'views/organization_renew_order_view.xml',
        'views/social_support_registration_order_view.xml',
        'views/orphan_registration_order.xml',
        'views/orphan_payment_view.xml',
        'views/basal_drainage_view.xml',
        'views/health_insurance_request.xml',
        'wizard/treatment_report.xml',
        'wizard/dzc_1_wizard_view.xml',
        'report/ratification_list_report_template.xml',
        'report/report_action.xml',
        'report/dzc_1_report_template.xml',

    ],
    # only loaded in demonstration mode

    'application': True,
    'installable': True,
}
