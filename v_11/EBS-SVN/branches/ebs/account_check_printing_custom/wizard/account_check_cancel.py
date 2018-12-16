# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from odoo import models, fields
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class account_cancel_check(models.TransientModel):
    """
    Wizard object allow user to cancel all checks that are oudated based on configured
    period in the journal.
    """

    _name = 'account.cancel.check'
    _description = 'Cancel Checks'


    journal_ids = fields.Many2many('account.journal', 'cancel_check_journal_rel', 'cancel_check_id', 'journal_id', 'Bank Accounts', 
                                         domain = [('type','in',['bank','cash'])], required=True)
    to_reconcile= fields.Selection([('checks', ' Only Checks'), ('All', 'All Entries  ')], 'Reconcile only:', required=True)                                            

    #v9: ,('allow_check_writing','=',True)
    def get_moves(self):
        if self._context is None:
            self._context = {}
        
        #form = self.read(self._ids, [])[0]
        journal_ids = self.journal_ids
        if self.to_reconcile == 'checks' :
                        
            log_ids = self.get_move(self.journal_ids)
            return {
                'domain': "[('id','in',%s)]" % log_ids,
                'name': 'Checks',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'check.log',#.log',
                'type': 'ir.actions.act_window'
        }
        
        else:
            move_ids=self.get_move(self.journal_ids)
            return {
                'domain': "[('id','in',%s)]" % move_ids,
                'name': 'Checks',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'account.move',#.log',
                'type': 'ir.actions.act_window'
        }

    def get_move(self=False,journal_ids=False):
        """
        Method that perform the action of canceling the outdated checks by:
        * search all outdated checks found in  the system based on configuration
        * create reverse posted move 
        * change status the check in the log to canceled

        @return: Window action of moves the created for canceled checks
        """
        """
        Method that perform the action of canceling the outdated checks by:
        * search all outdated checks found in  the system based on configuration
        * create reverse posted move 
        * change status the check in the log to canceled

        @return: Window action of moves the created for canceled checks
        """
        if self._context is None:
            self._context = {}
        #form = self.read(ids, [])[0]
        journal_ids = self.journal_ids
        journal_ids_list = []
        for jid in journal_ids:
            journal_ids_list.append(jid.id)
        log_pool = self.env['check.log']
        journal_obj = self.env['account.journal']
        move_obj = self.env['account.move']
        ml_ids=[]
        for journal in journal_obj.search([('id','in',journal_ids_list)]):

            date= (datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d') + relativedelta(months=-journal.grace_period)).strftime('%Y-%m-%d')
            for ml_id in self.env['account.move.line'].search([('date','<=',date),('journal_id','=',journal.id),('statement_id','=',False)]):
                ml_ids.append(ml_id.id)

            if journal.type!='bank' and   self.to_reconcile == 'checks':
                 raise UserError(_('Journals of  bank type only ! '))


            # Cancel Checks Only 
            elif journal.type=='bank' and   self.to_reconcile=='checks':
                            
                log_ids = log_pool.search([('status','=','active'),('name.move_line_ids','in',ml_ids)]).ids
                #log_ids = log_pool.search([('status','=','active')])
                self.with_context({'reverse_move': True, 'ref':'Canceled check: '})
                for log_obj in log_pool.search([('id','in', log_ids)]):
                    move = log_obj.name.move_line_ids[0].move_id
                    revert_id  = move.reverse_moves()
                    revert_id= move_obj.search([('id','in',revert_id)])
                    
                    for m in move_obj.search([('id','in',[revert_id.id,move.id])]):
                        m.write ({ 'state':'posted' })
                    for m in move_obj.search([('id','in',[revert_id.id])]):
                        #m.write ({ 'state':'posted' })
                        m.write ({ 'ref':'Canceled check: ' + move.ref, 'canceled_chk':True })
                    #move_obj.write([revert_id.id,move.id], { 'state':'posted' })  
                    #move_obj.write([revert_id.id], { 'ref':'Canceled check: ' + move.ref, 'canceled_chk':True })
                    log_obj.write({'status': 'canceled'})  
                    #log_pool.write(log_ids, {'status': 'canceled'})
                return log_ids

            # Cancel all Entries for selected Journal(s)
            elif  self.to_reconcile =='All' :
                 move_ids = []
                 move_ids_view = []
                 for l in self.env['account.move.line'].browse(ml_ids):
                     if l.move_id not in move_ids:
                        move_ids.append(l.move_id)
                 for move in move_ids:
                    revert = move.reverse_moves() 
                    revert= move_obj.search([('id','=',revert)])
                    for m in move_obj.search([('id','in',[revert.id,move.id])]):
                        m.write ({ 'state':'posted' })
                    for m in move_obj.search([('id','in',[revert.id])]):
                        #m.write ({ 'state':'posted' })
                        m.write ({ 'ref':'Canceled check: ' + move.ref, 'canceled_chk':True })
                   
                    #move_obj.write([revert.id,move.id], { 'state':'posted' })  
                    #move_obj.write([revert.id], { 'ref':'Canceled check: ' + str(move.ref), 'canceled_chk':True })
                    # return moves to view 
 
                    move_ids_view.append(move.id )
                    move_ids_view.append(revert.id)
 

                 return move_ids_view
            else :
                return False 
 

                 

account_cancel_check()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
