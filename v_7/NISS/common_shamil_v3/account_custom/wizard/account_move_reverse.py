# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time

class account_move_reverse(osv.TransientModel):

    def _get_journal(self, cr, uid, context={}):

       """
       Get journal_id from current object
       @return: id of journal
       """
       move_id = context.get('active_ids', [])
       return move_id and self.pool.get('account.move').browse(cr, uid, move_id[0], context=context).journal_id.id

    _name = 'account.move.reverse'
    
    _description = 'Reverse Move'
    
    _columns = {
     	'journal_id': fields.many2one('account.journal', 'Journal', required=True ,
                                      help='Journal for the reversion move'),
    
    	'period_id': fields.many2one('account.period', 'Move Period', required=True,
                                      help='Period for the reversion move'),
    
    	'date': fields.date('Date', help='Date for the move.', required=True),
    
    	'reconcile' : fields.boolean('Reconcile', help='Reconcile Moves?'),
    }

    _defaults = {
        'journal_id': _get_journal,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'reconcile': True,
    }

    def onchange_date(self, cr, uid, ids, date, context={}):
        """
        Onchange method to change in some field 
        @param date: date of move
        @return: dictionary of value
        """
        pids = date and self.pool.get('account.period').find(cr, uid, date, context=context) or False
        return {'value':{'period_id':pids and pids[0] or False}}

    def reverse(self, cr, uid, data, context=None):
        """
        This method to execute revert_move method
        @param date: date of move
        @return: dictionary of value        
        """
        form = self.read(cr, uid, data)[0]
        context['reverse_move'] = True
        for move in self.pool.get('account.move').browse(cr, uid, context.get('active_ids', []), context=context):
            move.revert_move(form['journal_id'], form['period_id'], form['date'], form['reconcile'], context=context)
        return {}
        





