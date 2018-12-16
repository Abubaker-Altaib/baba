# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class occasion_journal(osv.Model):
   """
   To define Occasion Account and Journal for each Company"""
    _inherit = 'admin_affairs.account'
    _columns = {
                'occasion_jorunal_id': fields.many2one('account.journal','Occasion journal',),
                'occasion_account_id': fields.many2one('account.account', 'Occasion Account',),
                'occasion_analytic_id':  fields.many2one('account.analytic.account' , "Occasion Analytic Account"),
                
                'hotel_journal_id': fields.many2one('account.journal','Hotel service journal',),
                'hotel_account_id': fields.many2one('account.account', 'Hotel service account',),
                'hotel_analytic_id':  fields.many2one('account.analytic.account' , "Hotel service analytic account"),
                
                'ticket_journal_id': fields.many2one('account.journal','Ticket booking journal',),
                'ticket_account_id': fields.many2one('account.account', 'Ticket booking account',),
                'ticket_analytic_id':  fields.many2one('account.analytic.account' , "Ticket service analytic account")
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
