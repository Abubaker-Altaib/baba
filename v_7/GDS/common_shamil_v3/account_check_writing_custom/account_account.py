# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv,fields
from openerp.tools.translate import _
import tools

class account_journal(osv.Model):
    """
    Inherit account journal to allow user configure checks printing properties and sequence.
    """
 
    _inherit = "account.journal"

    _columns = {
        'allow_check_writing': fields.boolean('Allow Check writing', help='Fill this if the journal is to be used for writing checks.'),
        'use_preprint_check': fields.boolean('Use Preprinted Check'),
        'check_sequence': fields.many2one('ir.sequence', 'Check Sequence', help="This field contains the information related to the numbering of the check number."),
        'grace_period': fields.integer('Grace Period',help="Number of month that each entry of this journal is not received after this period will cancelled"),
        }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        """
        Search for records based on a search domain.

        @param args: list of tuples specifying the search domain [('field_name', 'operator', value), ...]. Pass an empty list to match all records.
        @param offset: optional number of results to skip in the returned values (default: 0)
        @param limit: optional max number of records to return (default: **None**)
        @param order: optional columns to sort by (default: self._order=id )
        @param count: optional (default: **False**), if **True**, returns only the number of records matching the criteria, not their ids
        @return: id or list of ids of records 

        """
        if context is None:
            context = {}
        ids = super(account_journal, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)
        if context and context.has_key('pay_type'):
            if context['pay_type']=='cash':
                ids=self.search(cr, uid, [('type','=','cash')])
            elif context['pay_type'] =='chk':
                ids=self.search(cr, uid, [('type','=','bank'),('allow_check_writing','=',True)])
            else:
                ids=self.search(cr, uid, [('type','=','bank')])
                
        return ids
    _defaults = {
        'grace_period': 6,
        
    }
class res_company(osv.Model):
    """
    Inherit company object to allow user to configure checks layout 
    based on company level
    """
    _inherit = "res.company"

    _columns = {
        'check_layout': fields.selection([('top', 'Check on Top'), ('middle', 'Check in middle'),
                                          ('bottom', 'Check on bottom'),],"Choose Check layout", readonly = True,
                                          help="Check on top is compatible with Quicken, QuickBooks and Microsoft Money. Check in middle is compatible with Peachtree, ACCPAC and DacEasy. Check on bottom is compatible with Peachtree, ACCPAC and DacEasy only"),
        'currency_format': fields.selection([ ('euro','Europian Format'), ('ar','Arabic Format')],
                                            'Check Printing Format'),
    }
    
    _defaults = {
        'check_layout': 'top',
        'currency_format':'ar',
    }

class check_log(osv.Model):
    """
    This class for storing some data for each printed check as a 
    summary log display check info and it's state.
    """

    _name = 'check.log'
    _description = 'Check Log'

    _columns = {
        'signed':fields.boolean('Signed'),
        'name':fields.many2one('account.voucher','Payment Amount', ondelete='cascade'),
        'status': fields.selection([('active','Active'), ('voided', 'Voided'), ('lost', 'Lost'), ('cancel', 'Canceled'),
                                    ('unk', 'Unknown'),('delete', 'Deleted')],"Check Status",),
        'check_no': fields.char('Check Number', size=128),
        'journal_id': fields.many2one('account.journal', string='Bank', readonly=True),    
        'date_due': fields.related( 'name' , 'date', type='date', relation='account.voucher', string='Due Date', store=True),
        'partner_id': fields.related('name', 'partner_id', type='many2one', relation='res.partner', string='Beneficiary', store=True, readonly=True),
        'company_id': fields.related('name', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'date': fields.related('name', 'date', type='date', string='Date', store=True, readonly=True),
        'deleted':fields.boolean('Deleted'),
    }

    _defaults = {
        'status' :'blank',
    }

    def _check_no(self, cr, uid, ids):
        """
        Constrain method to prohibit system from duplicating check no for the same 
        bank account / journal.
        
        @return: Boolean True or False
        """
        for log in self.browse(cr, uid, ids):
            checks = self.search(cr, uid, [('journal_id','=',log.journal_id.id),('check_no','=',log.check_no),('deleted','=',False)])
            if len(checks)>1:
                return False
        return True

    _constraints = [(_check_no, 'This number already exist!', [])]


class account_move(osv.osv):
    """
    Inherit object move to add boolean field that determine it's canceled 
    check move if it's True
    """

    _inherit = 'account.move'
    _columns = {
        'canceled_chk' : fields.boolean('Cancel Check'),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
