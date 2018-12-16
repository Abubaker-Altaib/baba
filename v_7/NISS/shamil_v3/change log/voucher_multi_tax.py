    _columns = {
        'tax_id': fields.many2many('account.tax', 'account_voucher_tax_rel', 'voucher_id', 'tax_id', '   ', readonly=True,
                                       states={'draft':[('readonly', False)], 'approve':[('readonly', False)]}, domain=[('parent_id', '=', False)]),
    }

    _defaults = {
        'tax_id':False,
    }

    def onchange_price(self, cr, uid, ids, line_ids, tax_id, partner_id=False, context={}): #NEED TO TEST
        """
        Method call when changing Voucher Lines and/or Voucher Taxs, recalculate voucher amount 
        before taxs, taxs amount and voucher total amount.        
        """
        tax_id = tax_id[0][2]
        if tax_id:
            tax_id = not isinstance(tax_id, list) and [tax_id] or tax_id
            for tax in tax_id:
                super(account_voucher,self).onchange_price(cr, uid, ids, line_ids, tax, partner_id=partner_id, context=context)
        else:
            return super(account_voucher,self).onchange_price(cr, uid, ids, line_ids, False, partner_id=partner_id, context=context)
        return {'value':{}}
    
