# -*- coding: utf-8 -*-
#########################################################################################
#
#   
#    Copyright (C) 2011-2014 NCTR, Nile Center for Technology Research (<http://www.nctr.sd>).
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
###############################################################################################

{
    'name': 'Sudan - Accounting',
    'version': "1.1",
    'category': 'Localization/Account Charts',
    'description': """This is the base module to manage the accounting chart for Sudan in OpenERP with:
=================================================================================================
    - Chart of accounts
    - Tax structure
    - Currency of Sudan 
    - A few other adaptations""",

    'author': 'Nile Center For Technology Research (NCTR)',
    'website': 'http://www.nctr.sd',
    'depends': ['account','l10n_multilang'],
  
    'data': [
        'account_chart.xml',
        'account_tax.xml',
        'account_currency.xml',      
        'account_chart_template.xml',  
        'l10n_su_wizard.xml',     



    ],
    'demo': [ ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: