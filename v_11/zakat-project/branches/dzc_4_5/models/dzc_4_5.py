from odoo import fields, models, api, exceptions, _
from datetime import datetime, timedelta
from datetime import date


class KhalwaSupportOrder(models.Model):
    _inherit = 'support.order'
    _name = 'khalwa.support.order'
    prev_support = fields.Boolean(default=False)
    place_id = fields.Many2one('dzc_4_5.places.of.worship', 'Place')
    products_ids = fields.One2many('dawa.support.products','dawa_id',string="Products")

    @api.model
    def create(self, vals):
        khalwa = self.env['dzc_4_5.places.of.worship'].search([('id', '=', vals['place_id'])])
        if khalwa.pre_support:
            raise exceptions.ValidationError('this Kalwa has previous Support')
        else:
            for k in khalwa:
                k.pre_support = True
        return super(KhalwaSupportOrder, self).create(vals)

    @api.multi
    def report_print(self):
        return self.env.ref('dzc_4_5.khalwa_support_repport_action').report_action(self)

    @api.multi
    def action_done(self):
        if self.support_method == 'cash':
            if self.support_type == 'organization':
                if not self.oragnaztion_id.property_account_id.id:
                    raise exceptions.ValidationError(_("There Is No Zakat Account Specified for this organization. "))
                elif not self.oragnaztion_id.journal_id.id:
                    raise exceptions.ValidationError(_("There Is No Zakat Journal Specified for this organization."))
                else:
                    organization_line = []
                    organization_line +=  [(0, 6, {
                    'name': self.oragnaztion_id.name,
                    'account_id': self.oragnaztion_id.property_account_id.id,
                    'quantity': 1,
                    'name': _('Organization Support'),
                    'price_unit': self.approved_amount,
                    })]

                    voucher = self.env['account.voucher'].create(
                    {
                    'name': '' ,
                    'journal_id': self.oragnaztion_id.journal_id.id,
                    'company_id': self.company_id.id,
                    'pay_now': 'pay_later',
                    'reference': self.oragnaztion_id.name,
                    'voucher_type': 'purchase',
                    'line_ids' :organization_line,
                    })
                    self.vaucher_id = voucher.id
                    if self.oragnaztion_id:
                        self.oragnaztion_id.write({'support_type':self.type_})
                    else:
                        raise exceptions.ValidationError(_("There Is No Organization Selected. "))   
            if self.support_type != 'organization':
                if not self.place_id.property_account_id.id:
                    raise exceptions.ValidationError(_("There Is No Zakat Account Specified for this Place. "))
                elif not self.place_id.property_journal_id.id:
                    raise exceptions.ValidationError(_("There Is No Zakat Journal Specified for this Place."))
                else:
                    place_line = []
                    place_line +=  [(0, 6, {
                    'name': self.place_id.name,
                    'account_id': self.place_id.property_account_id.id,
                    'quantity': 1,
                    'name': _('Place Support'),
                    'price_unit': self.approved_amount,
                    })]

                    voucher = self.env['account.voucher'].create(
                    {
                    'name': '' ,
                    'journal_id': self.place_id.property_journal_id.id,
                    'company_id': self.company_id.id,
                    'pay_now': 'pay_later',
                    'reference': self.place_id.name,
                    'voucher_type': 'purchase',
                    'line_ids' :place_line,
                    })
                    self.vaucher_id = voucher.id
                    
                    if not self.place_id:
                        raise exceptions.ValidationError(_("There Is No Place Selected. "))

        self.write({'state': 'done'})

  
class SupportProducts(models.Model):
    _name="dawa.support.products"

    dawa_id = fields.Many2one('khalwa.support.order')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Integer(string='Product Quantity')

    @api.constrains('product_qty')
    def qty_validation(self):
        if self.product_qty <= 0:
            raise ValidationError(_("Product Quantity MUST be greater Than Zero"))

    @api.constrains('amount')
    def qty_validation(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount MUST be Greater Than Zero"))
