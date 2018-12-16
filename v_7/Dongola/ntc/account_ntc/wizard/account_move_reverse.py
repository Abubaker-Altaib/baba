# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_move_reverse(osv.TransientModel):
    """
    Wizard to create reverse move for posted move
    """
    _inherit = 'account.move.reverse'
    
    def reverse(self, cr, uid, data, context=None):
        """
        This method inherited to add log to reverse wizard
        @param date: date of move
        @return: dictionary of value
        """
        move_pool = self.pool.get('account.move')
        for move in self.pool.get('account.move').browse(cr, uid, context.get('active_ids', []), context=context):
            move_pool.create_log(cr, uid, [move.id], move.state, 'reversed', 'from_reverse_wizard', context)
        return super(account_move_reverse, self).reverse(cr, uid, data, context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
