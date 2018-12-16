# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Image Attachment',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'Make Image Save As Attachment',
    'description': """

    """,
    'website': 'https://www.nctr.sd',
    'depends': [
        'hr','resource' , 'web'
    ],
    'data': [
    'views/image_view.xml',
    ],
    'js': [
        'static/src/js/image_attach.js',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
