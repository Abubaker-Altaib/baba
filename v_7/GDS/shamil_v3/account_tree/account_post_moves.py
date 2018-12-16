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

import time
import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
from openerp import netsvc

class excel_data_move(osv.osv):
    _name = "excel.data.move"

    _columns = {
        'date': fields.date('date', required=True),
        'account_code': fields.char('account_code', size=154, required=True),
        'partner': fields.char('partner', size=154),
        'analytic': fields.char('analytic', size=154),
        'name': fields.char('name', size=154, ),
        'amount': fields.float('amount',),
        'account2': fields.char('Main Account', size=154),
        'chk': fields.char('Check', size=154),
        'type': fields.selection([('debit', 'debit'),('credit', 'credit'),], 'Account is:', required=True),
    }



class account_post(osv.osv_memory):
    _name = "account.post"
    def Post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        if 'active_ids' in context and context['active_ids']:
            wf_service = netsvc.LocalService("workflow")
            for rec in context['active_ids']:
                wf_service.trg_validate(uid, 'account.move', rec, 'completed', cr)
                wf_service.trg_validate(uid, 'account.move', rec, 'closed', cr)
                wf_service.trg_validate(uid, 'account.move', rec, 'button_post', cr)
        return {'type': 'ir.actions.act_window_close'}

class excel_post_move(osv.osv_memory):
    """
    Account move line reconcile wizard, it checks for the write off the reconcile entry or directly reconcile.
    """
    _name = 'excel.post.move'
    _columns = {

        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'account_id': fields.many2one('account.account', 'Account', required=True),
        'one': fields.boolean('Only one move'),
        'period_id': fields.many2one('account.period', 'Period'),
        'date': fields.date('date'),
    }
    def trans_rec_reconcile_full(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        voucher_id = False
        account_data = self.pool.get('excel.data.move')
        wiz = self.browse(cr, uid, ids, context)[0]
        if 'active_ids' in context and context['active_ids']:
            data = account_data.browse(cr, uid, context['active_ids'], context)
            total = 0
            if wiz.one:
                voucher_id  = 11446 
                            
            for rec in data:
                analytic_id = False
                partner_id = False
                pid = self.pool.get('account.period').find(cr, uid, rec.date, context=context) or False   
                account_id = self.pool.get('account.account').search(cr, uid, [('code', '=', rec.account_code)],context=context) 
                if not pid:  raise osv.except_osv(_('Error!'),_("No Period for id %s!")% (rec.id,))
                if not account_id:account_id =[3506]  #raise osv.except_osv(_('Error!'),_("there is no account for id %s !")% (rec.id,))   

                #if rec.analytic:
                     #analytic = self.pool.get('account.analytic.account').search(cr, uid, [('code', '=', rec.analytic)])  
                     #if not analytic:  raise osv.except_osv(_('Error!'),_("there is no analytic for id %s !")% (rec.id,))       
                     #if rec.type == 'debit':  analytic_id = analytic[0]     
                if rec.partner:
                     partner = self.pool.get('res.partner').search(cr, uid, [('code', '=', rec.partner)],context=context) 

                     if not partner: partner=[3] # raise osv.except_osv(_('Error!'),_("there is no partner for id %s !")% (rec.id,))       
                     #partner_id = partner[0]
                name = rec.chk
               
                voucher_id  = 12421 
                print"<<<<<<<<<<<<<<<<<<",account_id,"44444444444444444",partner               
                self.pool.get("account.voucher.line").create(cr, uid, {
                                                    'name':  rec.chk,
                                                    'voucher_id':  voucher_id,
                                                    'type': 'dr',
                                                    'res_partner_id': partner[0],
                                                    'account_id':  account_id[0],
                                                    'amount':  rec.amount ,
                                                    'analytic_account_id':530,
                                                    'custody':True,
                                                    'custody_state':'not removed',
                                                    'dest_approve':530,
                                                    
                                                    }, context)

           
        return {'type': 'ir.actions.act_window_close'}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
