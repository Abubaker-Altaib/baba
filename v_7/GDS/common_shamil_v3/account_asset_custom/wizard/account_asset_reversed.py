# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class account_post_move(osv.osv_memory):

    """
    Account move line reconcile wizard, it checks for the write off the reconcile entry or directly reconcile.
    """
    _name = 'account.operation.reverse'
    _columns = {
        'move_date': fields.date('Move date', required=True),
    }
    def act_operation_reverse(self, cr, uid, ids, context=None):
        """
        This Method used to reverse asset operation by creating reversed move and
        update the operation state to reversed which will change the asset values.

        @return: Action window of the created moves
        """ 
        if context is None:
            context = {}
        history_obj = self.pool.get('account.asset.history')
        asset_obj = self.pool.get('account.asset.asset')
        period_pool = self.pool.get('account.period')
        history_ids=context['active_ids'] or ids and ids
        if history_ids :
            wiz = self.browse(cr, uid, ids)
            pids = period_pool.find(cr, uid, wiz[0].move_date, context=context)
            if not pids: raise osv.except_osv(_('No period found !'), _('Unable to find a valid period !'))
            moves=[]
            for rec in history_obj.browse(cr, uid,history_ids, context):
                asset_lines = []
                move=[]
                move_id = False
                if rec.state != 'reversed' and rec.type !='initial':
                    cr.execute( 'SELECT  SUM(debit) as credit, SUM(credit) as debit,h.type as type , '\
                                'l.account_id, l.name as name, l.journal_id, '\
                                '%s as date, %s as period_id, %s as asset_id, %s as history_id  '\
                                'FROM account_move_line l '\
                                'left join account_asset_history h on (h.id=l.history_id)'\
                                ' WHERE l.asset_id = %s  and l.history_id=%s'\
                                'GROUP BY h.type,l.account_id,l.name, l.journal_id', (wiz[0].move_date, pids[0],rec.asset_id.id, rec.id,rec.asset_id.id,rec.id))
                    result = cr.dictfetchall()  
                    if result:
                        move_id = self.pool.get('account.move').create(cr, uid,{'period_id':pids[0],
                                                          'journal_id': result[0]['journal_id'], 'date':wiz[0].move_date})
                        moves.append({'id': move_id})
                        for r in result:
                            r.update({'move_id':move_id, 'name':'Reverse operation'+'-'+r['type']})
                            self.pool.get('account.move.line').create(cr, uid,r)
                        self.pool.get('account.move').post(cr, uid, [move_id], context)
                        history_obj.write(cr, uid, rec.id, {'state':'reversed'},context=context)
                    move=[m['id'] for m in moves]
        return {                
                'domain': "[('id','in',%s)]" % move,
                'name': 'Asset operation move',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window'}
       

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
