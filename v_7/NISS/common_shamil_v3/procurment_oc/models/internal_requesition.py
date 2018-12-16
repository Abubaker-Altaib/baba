# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
import netsvc
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class ireq_m_inhiret(osv.osv):
    _inherit = 'ireq.m'
    _name = 'ireq.m'

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]

    _columns = {
        'executing_agency': fields.selection(USERS_SELECTION, 'Executing Agency', select=True, help='Department Which this request will executed it'),
    }

    _defaults = {

        'executing_agency': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to,

    }

    def is_oc(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            if record.executing_agency == 'oc':
                return True
        return False

    def create_purchase_order_oc(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes order state to completed_quote.
        
        @return: True 
        """
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        wf_service = netsvc.LocalService("workflow")
        for order in self.browse(cr,uid,ids):
            for quote in order.q_ids:
                if quote.state == 'done' :
                   voucher_id = voucher_obj.create(cr, uid, {
                                        'amount': quote.amount_total,
                                        'type': 'purchase',
                                        'date': time.strftime('%Y-%m-%d'),
                                        'partner_id': quote.supplier_id.id , 
                                        'account_id': quote.supplier_id.property_account_payable.id , 
                                        'journal_id': order.company_id.purchase_foreign_journal.id,
                                        'reference':  order.name  ,
                                        'state': 'draft',
                                        'name': order.purchase_purposes })
               
                   for line in quote.pq_pro_ids :
                       if order.multi == 'multiple' :
                          if line.chosen == True :
                             vocher_line_id = voucher_line_obj.create(cr, uid, {
                                                    'amount': line.price_subtotal ,
                                                    'voucher_id': voucher_id,
                                                    'type': 'dr',
                                                    'account_id': line.product_id.product_tmpl_id.categ_id.property_account_expense_categ.id,
                                                    'name': line.product_id.name or '',
                                                     })
                               
                       else:
                            vocher_line_id = voucher_line_obj.create(cr, uid, {
                                                    'amount': line.price_subtotal ,
                                                    'voucher_id': voucher_id,
                                                    'type': 'dr',
                                                    'account_id': line.product_id.product_tmpl_id.categ_id.property_account_expense_categ.id,
                                                    'name': line.product_id.name or '',
                                                     })  
                   voucher_obj.compute_tax(cr, uid, [voucher_id], context=context)
            self.write(cr, uid, [order.id], {'state':'completed_fin_request'}, context=context)
            
            wf_service.trg_validate(
                uid, 'ireq.m', order.id, 'done', cr)
            self.create_purchase_order(cr, uid, [order.id],)
            self.write(cr, uid, [order.id], {'state':'done'}, context=context)
        return True


class res_users_inherit(osv.osv):
    """
    To add separated users between Supply Department and Techncial Services Department """

    _inherit = 'res.users'

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]

    _columns = {
        'belong_to': fields.selection(USERS_SELECTION, 'Belongs To', select=True, help='Select Department Which this user belongs to it'),
    }


class ir_sequence(osv.osv):

    _inherit = 'ir.sequence'

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]

    _columns = {
        'executing_agency': fields.selection(USERS_SELECTION, 'Executing Agency', help='Department Which this request will executed it'),
    }

class purchase_order(osv.Model):
    """ 
    To change state values"""

    _inherit = 'purchase.order'
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]

    _columns = {
        'executing_agency': fields.selection(USERS_SELECTION, 'Executing Agency', help='Department Which this request will executed it'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
