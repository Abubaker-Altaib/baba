# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_voucher(osv.Model):

    _inherit = 'account.voucher'

    _columns = {
        'chk_seq' : fields.char("Check Number", size=64),
    }

    def action_move_line_create(self, cr, uid, ids, vals={}, context=None):
        """
        Inherit action_move_line_create method to prevent creating journal entries when pay_type check or bank letter and doesn't print yet
        
        @return: super action_move_line_create
        """
        if self.search(cr, uid, [('id','in',ids), ('state','=','receive'), ('pay_type','in',('chk','letter')), ('chk_seq','=',False)], context=context):
            raise orm.except_orm(_('Warning !'), _('Kindly print your payment check or bank letter before delivery it.'))
        return super(account_voucher,self).action_move_line_create(cr, uid, ids, vals={}, context=context)


    def receive_voucher(self, cr, uid, ids, context=None):
        """
        Inherit receive_voucher method to create journal entry when the operation is treasury feeding
        
        @return: change state to 'receive'
        """
        
        for voucher in self.browse(cr, uid, ids, context=context):
                if voucher.pay_type =='cash' and voucher.amount > voucher.account_id.payment_ceiling:
                    raise orm.except_orm(_('Warning !'), _('The Amount You Intered %s is Exceed The Payments Ceiling Of %s Account %s')%(voucher.amount,voucher.account_id.name,voucher.account_id.payment_ceiling))
        #if self.browse(cr, uid, ids, context=context)[0].operation_type == 'treasury':
        #   self.action_move_line_create(cr, uid, ids, context=context)
        super(account_voucher, self).receive_voucher(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state': 'receive'}, context=context)


    def action_cancel_voucher(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'cancel'
        @return: boolean True
        """
        for voucher in self.browse(cr,uid,ids,context=context):
            if voucher.chk_seq:
                check_log = self.pool.get("check.log")
                check_log_ids = check_log.search(cr,uid,[('name','=',voucher.id),('journal_id','=',voucher.pay_journal_id.id),
                    ('check_no','=',voucher.chk_seq),])
                check_log.write(cr, uid, check_log_ids, {'status': 'cancel'}, context=context)
        return super(account_voucher, self).action_cancel_voucher(cr, uid, ids, context=context)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
