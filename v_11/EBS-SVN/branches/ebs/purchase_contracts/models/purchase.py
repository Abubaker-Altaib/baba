# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from odoo import api, fields, models, exceptions,_



class foreign_purchase(models.Model):
    """ 
    To manage purchase orders wich related to purchase contract """

    _inherit = 'purchase.order'

    contract_id = fields.Many2one('purchase.contract','Purchase Contract',readonly=True)


    def action_picking_create(self):
        """
        Override to read account id from purchase contract object
        if the purchase order related to acontract.

        @return: picking id 
        """
        res = {}
        account = None
        picking_obj = self.env['stock.picking']
        picking_id = super(foreign_purchase, self).action_picking_create()
        picking = picking_obj
        purchase_obj = picking.purchase_id
        if purchase_obj:
            if purchase_obj.purchase_type == 'foreign':
                if purchase_obj.contract_id:
                    account = purchase_obj.contract_id.contract_account
                    if not account:
                        raise exceptions.ValidationError(_('no account defined for purchase foreign.'))
                    else:
                        res = { 
                            'account_id': account.id or False,
                              }
            picking.write(res)
        return picking_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
