# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from osv import osv, fields
from tools.translate import _
from dateutil.relativedelta import relativedelta


class account_cancel_check(osv.osv_memory):
    """
    Wizard object allow user to cancel all checks that are oudated based on configured
    period in the journal.
    """

    _name = 'account.cancel.check'
    _description = 'Cancel Checks'

    _columns = {
        'journal_ids': fields.many2many('account.journal', 'cancel_check_journal_rel', 'cancel_check_id', 'journal_id', 'Bank Accounts', 
                                         domain = [('type','=','bank'),('allow_check_writing','=',True)], required=True),                                           
    }

    def get_moves(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        form = self.read(cr, uid, ids, [])[0]
        
        journal_ids = form['journal_ids']
        
        log_ids = self.get_move(cr, uid, ids,journal_ids, context=context)
        
        return {
                'domain': "[('id','in',%s)]" % log_ids,
                'name': 'Checks',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'check.log',
                'type': 'ir.actions.act_window'
        }

    def get_move(self, cr, uid, ids=False,journal_ids=False, context=None):
        """
        Method that perform the action of canceling the outdated checks by:
        * search all outdated checks found in  the system based on configuration
        * create reverse posted move 
        * change status the check in the log to canceled

        @return: Window action of moves the created for canceled checks
        """
        form = self.read(cr, uid, ids, [])[0]
        journal_ids = form['journal_ids']
        log_pool = self.pool.get('check.log')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        ml_ids=[]
        for journal in journal_obj.browse(cr, uid, journal_ids):
            date= (datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d') + relativedelta(months=-journal.grace_period)).strftime('%Y-%m-%d')
            ml_ids += self.pool.get('account.move.line').search(cr, uid, [('date','<=',date),('journal_id','=',journal.id),
                                                                     ('statement_id','=',False)], context=context)
        log_ids = log_pool.search(cr, uid, [('status','=','active'),('name.move_ids','in',ml_ids)], context=context)

        context.update({'reverse_move': True, 'ref':'Canceled check: '})
        for log_obj in log_pool.browse(cr, uid, log_ids, context=context):
            move = log_obj.name.move_id
            pids = self.pool.get('account.period').find(cr, uid, time.strftime('%Y-%m-%d'), context={'company_id':move.company_id.id})
            revert_id = move.revert_move([move.journal_id.id], pids, time.strftime('%Y-%m-%d'), True, context=context)  
            move_obj.write(cr, uid, [revert_id, move.id], { 'state':'posted' })  
            move_obj.write(cr, uid, [revert_id], { 'ref':'Canceled check: ' + move.ref, 'canceled_chk':True })  
        log_pool.write(cr, uid, log_ids, {'status': 'cancel'}, context=context)            
             
        return log_ids


account_cancel_check()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
