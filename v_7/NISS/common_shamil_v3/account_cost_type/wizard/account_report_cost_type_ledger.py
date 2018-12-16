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

class account_cost_type_ledger(osv.osv_memory):
    """
    This wizard will provide the cost type Ledger report by periods, between any two dates.
    """
    _name = 'account.cost.type.ledger'
    _inherit = 'account.common.partner.report'
    _description = 'Account Cost Type Ledger'

    _columns = {
        #'initial_balance': fields.boolean('Include initial balances',
        #                            help='It adds initial balance row on report which display previous sum amount of debit/credit/balance'),
        'reconcil': fields.boolean('Include Reconciled Entries', help='Consider reconciled entries'),
        'page_split': fields.boolean('One Cost Type Per Page', help='Display Ledger Report with One Cost Type per page'),
        'amount_currency': fields.boolean("With Currency", help="It adds the currency column if the currency is different then the company currency"),
        'account_ids': fields.many2many('account.account', 'report_account_cost_account_rel', 'report_account_id', 'account_id', 'Accounts'),

        'cost_type_ids': fields.many2many('account.cost.type', 'report_account_cost_rel', 'report_account_id', 'cost_type_id', 'Cost Types'),
     
        'cumulate_move': fields.boolean('Cumlate move balance'),

    }

    _defaults = {
       'reconcil': True,
       #'initial_balance': True,
       'page_split': False,
       'cumulate_move':True,

    }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, [ 'reconcil', 'page_split', 'amount_currency','account_ids', 'cost_type_ids','cumulate_move'])[0])

        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.cost.type.ledger',
                'datas': data,
        }
       

account_cost_type_ledger()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
