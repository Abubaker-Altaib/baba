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
        'account_code': fields.char('account_code', size=154, required=True),
        'partner': fields.char('partner', size=154),
        'analytic': fields.char('analytic', size=154),
        'name': fields.char('name', size=154, ),
        'debit': fields.float('debit',),
        'credit': fields.float('credit',),
        'account2': fields.char('Main Account', size=154),
        'chk': fields.char('Check', size=154),
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

        move_id = False
        account_data = self.pool.get('excel.data.move')
        wiz = self.browse(cr, uid, ids, context)[0]
        if 'active_ids' in context and context['active_ids']:
            data = account_data.browse(cr, uid, context['active_ids'], context)
            total = 0
            
            move_id  = self.pool.get("account.move").create(cr, uid, {
                                                    'journal_id': wiz.journal_id.id,
                                                    'period_id':wiz.period_id.id ,
                                                    'date':  wiz.date
                                                    }, context)
            for rec in data:
                analytic_id = False
                partner_id = False
                pid = self.pool.get('account.period').find(cr, uid, wiz.date, context=context) or False   
                account_id = self.pool.get('account.account').search(cr, uid, [('code', '=', rec.account_code)])             
                if not pid:  raise osv.except_osv(_('Error!'),_("No Period for id %s!")% (rec.id,))
                if not account_id:  raise osv.except_osv(_('Error!'),_("there is no account for id %s !")% (rec.id,))
                #if rec.analytic:
                     #analytic = self.pool.get('account.analytic.account').search(cr, uid, [('code', '=', rec.analytic)])  
                     #if not analytic:  raise osv.except_osv(_('Error!'),_("there is no analytic for id %s !")% (rec.id,))       
                     #if rec.type == 'debit':  analytic_id = analytic[0]     
                if rec.partner:
                     partner = self.pool.get('res.partner').search(cr, uid, [('id', '=', rec.partner)])  
                     if not partner:
                         raise osv.except_osv(_('Error!'),_("there is no partner for id %s !")% (rec.id,))       
                     partner_id = partner[0]
                #if wiz.one: total +=rec.type == 'debit' and rec.amount or -rec.amount 
                name = rec.name
                
                self.pool.get("account.move.line").create(cr, uid, {
                                                    'journal_id': wiz.journal_id.id,
                                                    'period_id':wiz.period_id.id  ,
                                                    'date':  wiz.date,
                                                    'name':  rec.name,
                                                    'move_id':  move_id,
                                                    'partner_id': partner_id,
                                                    'account_id':  account_id[0],
                                                    #'analytic_account_id': analytic_id,
                                                    'ref': rec.partner,
                                                    'debit':  rec.debit or 0.0,
                                                    'credit':  rec.credit or 0.0,
                                                    }, context)
            
        return {'type': 'ir.actions.act_window_close'}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
