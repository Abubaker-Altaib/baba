# -*- coding: utf-8 -*-
##############################################################################
#
#    Saml2 Authentication for Odoo
#    Copyright (C) 2010-2015 XCG Consulting <http://odoo.consulting>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Report NO Download',
    'author': 'Alfadil',
    'depends': ['base', 'web', 'base_setup'],

    'data': [
        
    ],

    'js': ['static/src/js/text_layer_builder.js','static/src/js/pdfobject.min.js','static/src/js/print.min.js','static/src/js/docviewer.js','static/src/js/secure_script.js'],
    
    'installable': True,
    'auto_install': False,
}
