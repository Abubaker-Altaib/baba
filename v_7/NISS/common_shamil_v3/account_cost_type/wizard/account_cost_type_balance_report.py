# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv

class account_cost_type_balance(osv.osv_memory):

    _inherit = 'account.common.report'
    _name = 'account.cost.type.balance'
    _description = 'Print Account Cost type Balance'
    _columns = {

        'account_ids': fields.many2many('account.account', 'account_common_cost_balance_account_rel', 'cost_bal_id', 'account_id', 'Accounts', required=True),

        'cost_type_ids': fields.many2many('account.cost.type', 'account_cost_balance_cost_rel', 'cost_bal_id', 'cost_type_id', 'Partners'),
    }
    
    def onchange_chart_id(self, cr, uid, ids, chart_account_id= -1, context=None):
        res = {}
        if chart_account_id:
            account_obj = self.pool.get('account.account')
            children = account_obj._get_children_and_consol(cr, uid, chart_account_id, context=context)
            company_id = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context).company_id.id
            res['value'] = {'company_id': company_id, 'acc_ids': account_obj.search(cr, uid, [('id', 'in', tuple(children)),('type','not in',('view','consolidation'))], context=context)}
        return res 

    def _print_report(self, cr, uid, ids, data, context=None):
        data['form'].update(self.read(cr, uid, ids, ['account_ids','cost_type_ids'])[0])
        res = {'datas':data,'type': 'ir.actions.report.xml', 'report_name': 'account.cost.type.balance'}
        return res
    

   
account_cost_type_balance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
