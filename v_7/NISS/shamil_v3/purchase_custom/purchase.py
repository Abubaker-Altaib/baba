# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
import datetime

#******************************************************************
# Inherit purchase module to adding fields related to requisition #
#******************************************************************

#
# Model definition
#

class purchase_order(osv.osv):
    """
    Inherit purchase module to add fields related to requisition"""

    def _check_location(self, cr, uid, ids, context=None):
        """ Checks if location type is correct acording to the purchase type.
        @return: True or False
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.location_id :
                    if order.purpose == 'direct' and order.location_id.usage == 'internal':return False
                    if order.purpose == 'store' and order.location_id.usage != 'internal':return False
        return True

    _inherit = "purchase.order"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Destination', readonly=1,states={'draft':[('readonly', False)]},domain=[('usage','<>','view')]),
        'ir_id' : fields.many2one('ireq.m','Request for approval No', readonly=1, help="It referes to Request for approval order from which this purchase order was created."),
        'ir_date':fields.date('IR Date', readonly=1, help="Date on which internal requisition has been created"),
        'pq_id' : fields.many2one('pur.quote','Purchase Quotation', readonly=1),
        'delivery_period': fields.integer('Delivery period',readonly=1,states={'draft':[('readonly', False)]}),
        'delv_plan': fields.char('Delivery Plan', size=256,readonly=1,states={'draft':[('readonly', False)]},),
        'e_date':fields.date('Expected Date',readonly=1,states={'draft':[('readonly', False)]}),
        'cat_id':fields.many2one('product.category', 'Category', readonly=1),
        'department_id':fields.many2one('hr.department', 'Department',readonly=1 ),
        'purpose': fields.selection([('store', 'Feed Store'),('direct','Direct Issue'),],'Purpose', readonly=1),
        'test_report_print': fields.char('Purchase Report Printing', size=256),
        'user_id':  fields.many2one('res.users', 'Responsible', readonly=True  ),    
    }
    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }

    _constraints = [
        (_check_location, 'You must chose a correct type of location',['location_id'])]
    
    def onchange_delivery_period(self, cr, uid, ids, delivery_period, context=None):
        """ 
        Change the date when changing the delivery period.

        @return: dictionary of vals of expected date
        """
        expected_date = datetime.date.today() + datetime.timedelta(days=delivery_period)
        return {'value':{'e_date': expected_date.strftime('%Y-%m-%d'),}}
    

    def wkf_sign_order(self, cr, uid, ids, context=None):
        """ 
        workflow function make the order sign and check the location field.

        @return: Boolean True  
        """
        for po in self.browse(cr, uid, ids, context=context):
            if not po.location_id:
                raise osv.except_osv(_('NO Stock Location !'), _('Please chose stock location then make Confirmation.'))
        self.write(cr, uid, ids, {'state': 'sign', })
        return True

    def action_invoice_create(self, cr, uid, ids, context=None):
        """
        This method get currency from user company

        @param self: object pointer
        @param cr: database cursor
        @param inv_id: The invoice id  which is created and use this id to edit this invoice by new values 
        @return: returns the id of affected record
        """
        res = {}
        inv_id = super(purchase_order,self).action_invoice_create(cr, uid, ids, context)
        inv_obj = self.pool.get('account.invoice')
        for purchase_obj in self.browse(cr, uid, ids):
            res = { 
                    'currency_id': purchase_obj.company_id.currency_id.id or purchase_obj.pricelist_id.currency_id.id,
                    }        
            inv_obj.write(cr,uid,inv_id,res)
        return inv_id 
#
# Model definition
#
class purchase_order_line(osv.osv):
    """
    Add filds to purchase order line """

    _inherit = "purchase.order.line"
    _columns = {
        'price_unit_tax': fields.float('Tax Unit Price',digits=(16, 4)),
        'price_unit_total': fields.float('Total Unit Price',digits=(16, 4)),
        'quote_product': fields.many2one('pq.products', 'quote product', ondelete='restrict', readonly=True),
               }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
