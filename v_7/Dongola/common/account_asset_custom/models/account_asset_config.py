# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

from openerp.osv import fields, osv

class account_asset_config(osv.osv_memory):
    
    
    
    def _default_company(self, cr, uid, context=None):
        """Method that returns the defualt company of user.
           @return: Id of user's company
        """
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id
    
    
    
    _name = 'account.asset.config'
    _inherit = 'res.config.settings'      
    _columns = {
        
        
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'account_asset_id': fields.related('company_id' , 'account_asset_id', type='many2one' , relation='account.account', string='Asset Account',domain=[('type','=','other')]),
        'account_depreciation_id': fields.related('company_id' , 'account_depreciation_id' , type='many2one' , relation='account.account', string='Depreciation Account', domain=[('type','=','other')]),
        'account_expense_depreciation_id': fields.related('company_id' , 'account_expense_depreciation_id', type='many2one' , relation='account.account', string='Depr. Expense Account', domain=[('type','=','other')]),
        'journal_id': fields.related('company_id' , 'journal_id' ,  type='many2one' , relation='account.journal', string='Journal',),
          
          }

    

    _defaults = {
       'company_id': _default_company,
    }

    def create(self, cr, uid, values, context=None):
        id = super(account_asset_config, self).create(cr, uid, values, context)
        # Hack: to avoid some nasty bug, related fields are not written upon record creation.
        # Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [id], vals, context)
        return id

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """Method that updates related fields of the company.
           @param company_id: Id of company
           @return: Dictionary of values 
        """
        values = {}
        if company_id:
            print "In Function IF found onchange_company_id"
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            values = {
                'account_asset_id': company.account_asset_id.id,
                'account_depreciation_id':company.account_depreciation_id.id,
                'account_expense_depreciation_id': company.account_expense_depreciation_id.id,
                'journal_id':company.journal_id.id,
                
            }
        return {'value': values  }
    
    
    


class res_company(osv.Model):

    _inherit = 'res.company'

    _columns = {
              
        'account_asset_id': fields.many2one('account.account', 'Asset Account', domain=[('type','=','other')]),
        'account_depreciation_id': fields.many2one('account.account', 'Depreciation Account', domain=[('type','=','other')]),
        'account_expense_depreciation_id': fields.many2one('account.account', 'Depr. Expense Account',domain=[('type','=','other')]),
        'journal_id': fields.many2one('account.journal', 'Journal',),

               }

    