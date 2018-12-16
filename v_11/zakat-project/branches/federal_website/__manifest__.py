# -*- coding: utf-8 -*-
{
    'name': "Federal Treatment Website",

    'summary': """Federal Treatment Website""",

    'author': "NCTR",

    'website': "http://www.nctr.sd",

    'category': 'website',

    'version': 'FT_website V0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website','dzc_1','website_form'],

    # always loaded
    'data': [
    'views/ft_website_template.xml',
   
    ],
    'js': ['static/src/js/ft.js','static/src/js/ft.js'],
    'css':['static/src/css/sheet.css'],
    
    'application': True,
    'installable': True,
}
