# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv

class account_fiscalyear_close(osv.osv_memory):
    """
    Closes Account fiscal year and generate closing entries for the selected fiscal year revenue & expense accounts
    """
    _inherit = "account.fiscalyear.pl.close"

    def data_save(self, cr, uid, ids, context=None):
        """
        This function leave fiscal year and period states as it is
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscal year close state’s IDs
        """
        data_browse =  self.browse(cr, uid, ids, context=context)[0]
        period_state = data_browse.period_id.state
        fiscalyear_state = data_browse.fiscalyear_id.state
        #period_state = data_browse.period_id.id
        self.pool.get('account.period').write(cr, uid, data_browse.period_id.id ,{'state': 'draft'}, context=context)
        res = super(account_fiscalyear_close, self).data_save(cr, uid, ids, context=context)
        #Set active = True in account_move_line
        move_id = res.get('res_id', False)
        if move_id:
            move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('move_id','=',move_id),('active','=',False)], context=context)
            self.pool.get('account.move.line').write(cr, uid, move_line_ids,{'active': True}, context)
        self.pool.get('account.period').write(cr, uid,[data_browse.period_id.id],{'state': period_state}, context=context)
        self.pool.get('account.fiscalyear').write(cr, uid, [data_browse.fiscalyear_id.id], {'state': fiscalyear_state}, context=context)
        return res
