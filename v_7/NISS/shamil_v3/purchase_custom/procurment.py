# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
from osv import osv, fields
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


#
# Model definition
#

class procurement_order(osv.osv):
    """
    To create purchase requestion from procurment """

    _inherit = 'procurement.order'
    _columns = {
        'ireq_id': fields.many2one('ireq.m', 'Internal Requsetion'),
    }
    
    def check_buy(self, cr, uid, ids):
        """ 
        Override to Checks product type. and removes the supplier check.

        @return: Boolean True or False
        """
        user = self.pool.get('res.users').browse(cr, uid, uid)
        partner_obj = self.pool.get('res.partner')
        for procurement in self.browse(cr, uid, ids):
            if procurement.product_id.product_tmpl_id.supply_method != 'buy':
                return False
            if not procurement.product_id.seller_ids:
                # STOPING RAISE
                return True
            partner = procurement.product_id.seller_id #Taken Main Supplier of Product of Procurement.
            if not partner:
                cr.execute('update procurement_order set message=%s where id=%s',
                           (_('No default supplier defined for this product'), procurement.id))
                return False
            if user.company_id and user.company_id.partner_id:
                if partner.id == user.company_id.partner_id.id:
                    return False
            address_id = partner_obj.address_get(cr, uid, [partner.id], ['delivery'])['delivery']
            if not address_id:
                cr.execute('update procurement_order set message=%s where id=%s',
                        (_('No address defined for the supplier'), procurement.id))
                return False
        return True

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line_vals, context=None):
        """
        Create the purchase order from the procurement, using
        the provided field values, after adding the given purchase
        order line in the purchase order.

        @params procurement: the procurement object generating the purchase order
        @params dict po_vals: field values for the new purchase order (the
                                 ``order_line`` field will be overwritten with one
                                 single line, as passed in ``line_vals``).
        @params dict line_vals: field values of the single purchase order line that
                                  the purchase order will contain.
        @return: id of the newly created purchase order
        """
        po_vals.update({'pro_ids': [(0,0,line_vals)]})
        return self.pool.get('ireq.m').create(cr, uid, po_vals, context=context)

    def _get_purchase_schedule_date(self, cr, uid, procurement, company, context=None):
        """ 
        Return the datetime value to use as Schedule Date (``date_planned``) for the
        Purchase Order Lines created to satisfy the given procurement.

        @param procurement: the procurement for which a PO will be created.
        @param company: the company to which the new PO will belong to.
        @return: the desired Schedule Date for the PO lines
        @rtype: datetime
        """
        procurement_date_planned = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        schedule_date = (procurement_date_planned - relativedelta(days=company.po_lead))
        return schedule_date

    def make_po(self, cr, uid, ids, context=None):
        """ 
        Make purchase order from procurement

        @return: New created Purchase Orders procurement wise
        """
        res = {}
        if context is None:
            context = {}
        uom_obj = self.pool.get('product.uom')
        seq_obj = self.pool.get('ir.sequence').get(cr, uid, 'ireq.m')
        for procurement in self.browse(cr, uid, ids, context=context):
            partner = procurement.product_id.seller_id # Taken Main Supplier of Product of Procurement.
            seller_qty = procurement.product_id.seller_qty
            partner_id = partner.id
            uom_id = procurement.product_id.uom_po_id.id
            qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
            if seller_qty:
                qty = max(qty,seller_qty)

            #Passing partner_id to context for purchase order line integrity of Line name
            context.update({'lang': partner.lang, 'partner_id': partner_id})

            cat = procurement.product_id.categ_id.id
            po_vals = {
                'name':seq_obj,
                'ir_ref':procurement.name,
                'pro_ids': [],
                'purpose': 'store',
                'cat_id': cat,
                }
            
            line_vals = {
                'name': procurement.name,
                'product_qty': qty,
                'product_id': procurement.product_id.id,
                'product_uom': uom_id,
            }
            res[procurement.id] = self.create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context=context)
            self.write(cr, uid, [procurement.id], {'state': 'running', 'ireq_id': res[procurement.id]})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
