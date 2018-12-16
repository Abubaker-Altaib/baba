# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import fields, osv
from openerp import netsvc

class account_close_period(osv.osv_memory):
    """This model to close moves in special period """
    _name = "account.close.period"
    _description = "Close Period"
    _columns = {
        'journal_id': fields.many2one('account.journal', 'journal', help='Select journal of Accounts',),
        'period_id': fields.many2one('account.period', 'period', help='Select period of Accounts',),
        'move_ids': fields.many2many('account.move','close_period_move_id_rel', 'close_period_id', 'move_id','Moves',),
        'move_filled': fields.boolean('Moved Filled'),
        'date_from': fields.date('Date From'), 
        'date_to': fields.date('Date To'),
    }
    
    _defaults = {
        'date_from': time.strftime('%Y-01-01'), 
        'date_to': time.strftime('%Y-%m-%d')
    }
  
    def get_moves(self, cr, uid, ids, context=None):
        """
        Get All moves belong not in draft, posted or reversed state
        @return: dictionary of values
        """
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        obj_account_move = self.pool.get('account.move')
        wf_service = netsvc.LocalService("workflow")
        domain=[('state','=',('closed')), ('date', '>=', data['date_from']), ('date','<=',data['date_to'])]
        if data['period_id']:
           domain.append(('period_id','=', data['period_id'][0]))
        if data['journal_id']:
           domain.append(('journal_id','=', data['journal_id'][0]))
        #Remove all move_ids if existed
        for wizard in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [wizard.id],{'move_filled':False,'move_ids':[(5, 0, [move.id for move in wizard.move_ids])]})
        move_ids=obj_account_move.search(cr,uid,domain,context=context)

        if move_ids:
           self.write(cr, uid, ids,{'move_filled':True, 'move_ids':[(6, 0, move_ids)]})

        return True

    def close_period(self, cr, uid, ids, context=None):
        """
        Validate all accounts belong in consolidation account or not
        @return: dictionary of values
        """
        if context is None:
            context = {}
        obj_account_move = self.pool.get('account.move')
        wf_service = netsvc.LocalService("workflow")

        move_ids= [move.id for move in self.browse(cr, uid, ids[0]).move_ids]
        completed_move_ids=obj_account_move.search(cr,uid,[('state','=','completed'),('id','in',move_ids)],context=context)

        for move_id in completed_move_ids:
            wf_service.trg_validate(uid, 'account.move',move_id, 'closed', cr)
            obj_account_move.create_log(cr, uid, [move_id], 'completed', 'closed', 'from_wizard', context)

        closed_move_ids=obj_account_move.search(cr,uid,[('state','=','closed'),('id','in',move_ids)],context=context)
        for move_id in closed_move_ids:
            obj_account_move.post(cr, uid, [move_id], context)
            #wf_service.trg_validate(uid, 'account.move',move_id, 'post', cr)
            obj_account_move.create_log(cr, uid, [move_id], 'closed', 'post', 'from_wizard', context)

        self.write(cr, uid, ids,{'move_filled':False})
  
        '''return {
                'domain': "[('id','in',%s)]" % move_ids,
                'name': 'account entries',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window'
        }'''
        
   
