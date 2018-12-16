# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Online Jobs Custom',
    'category': 'Website',
    'summary': 'Job Descriptions And Application Forms',
    'description': "",
    'depends': ['website_hr_recruitment', 'hr_recruitment_custom'],
    'data': [
        'data/config_data_custom.xml',
        'views/website_hr_recruitment_templates_custom.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
