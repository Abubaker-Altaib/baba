# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _

class wizard_bank_letter(osv.osv_memory):

    _name = 'wizard.bank.letter'
    
    def _get_journal(self, cr, uid, context=None):
        id = context.get('active_ids',False)
        return id and self.pool.get('account.voucher').browse(cr, uid, id, context=context)[0].journal_id.name or False

    _columns = {
        'name': fields.char('Partner bank', size=124, required=True),
        
        'bank': fields.char('Bank', size=124, required=True),
    }
    
    _defaults = {
        'bank': _get_journal,
    }
    
    def act_bank_letter(self, cr, uid, ids, context={}):
        """ 
        Method print the report and write the text 'bank letter' in voucher
        or raise error if their is a check already printed before.

        @return: dictionary to print report
        """
        voucher_pool = self.pool.get('account.voucher')
        data = {
                'ids': context.get('active_ids', []),
                'model': context.get('active_model', 'ir.ui.menu'),
                'form': self.read(cr, uid, ids, ['name','bank'])[0]
        }
        voucher = voucher_pool.browse(cr, uid, data['ids'][0], context=context) 
        if voucher.chk_seq and voucher.chk_seq !='Bank Letter':
            raise orm.except_orm(_('Error!'), _('Please delete the check no first!'))
        
        voucher_pool.write(cr, uid, [voucher.id],{'chk_seq':'Bank Letter'},context=context)
        return { 'type': 'ir.actions.report.xml', 'report_name': 'bank.letter', 'datas': data}

wizard_bank_letter()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
